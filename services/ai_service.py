import json
import openai
import sentry_sdk
from models.company import Company
from models.campaign import Campaign
from models.ai_config import AiConfig
from models.interaction_log import InteractionLog

def _call_gpt(api_key: str, messages: list, temperature=0.5,
              max_tokens=120, presence_penalty=0.3, frequency_penalty=0.5,
              response_format=None):
    openai.api_key = api_key
    kwargs = dict(
        model="gpt-4.1-mini",
        temperature=temperature,
        max_tokens=max_tokens,
        presence_penalty=presence_penalty,
        frequency_penalty=frequency_penalty,
        messages=messages,
    )
    if response_format:
        kwargs["response_format"] = response_format
    return openai.chat.completions.create(**kwargs)

def _lead_status(have_full_name: bool, have_phone_number: bool) -> str:
    if have_full_name and have_phone_number:
        return (
            "LEAD IS COMPLETE. Name and phone number are already saved. "
            "Do NOT ask for them again under any circumstances. "
            "If the customer has no new question, end the conversation warmly."
        )
    if have_full_name:
        return (
            "Customer name is already known. "
            "Ask for phone number at the right moment — not immediately."
        )
    if have_phone_number:
        return (
            "Phone number is already saved. "
            "Ask for the customer's name at the right moment — not immediately."
        )
    return (
        "Name and phone number are not yet collected. "
        "Collect them AFTER giving a price estimate. "
        "Do not ask for them before price discussion."
    )

def get_ai_reply(sender_id, text, company_id, have_full_name, have_phone_number):
    sentry_sdk.logger.warning(
        f"get_ai_reply | text={text!r} | company_id={company_id}"
    )

    company = Company.query.filter_by(id=company_id).first()

    campaigns = Campaign.query.filter_by(company_id=company.id, is_active=True).all()
    campaign_block = "\n\n".join(
        f"[{c.title}]\n{c.content}" for c in campaigns
    )

    ai_configs = AiConfig.query.filter_by(company_id=company.id).all()
    config_block = "\n\n".join(
        f"[{cfg.template_name}]\n{cfg.template_text}"
        for cfg in ai_configs if cfg.use_openai
    )

    lead_block = _lead_status(have_full_name, have_phone_number)

    system_prompt = f"""You are a real sales manager at Clima.uz.
You are 25 years old, friendly, sharp, and fully human in tone.
You work on Instagram DM and your only job is to help the customer and collect their contact.

━━━━━━━━━━━━━━━━━━━━━━
LANGUAGE — TOP PRIORITY
━━━━━━━━━━━━━━━━━━━━━━

Rule 1 — Detect language from the LAST user message only. Ignore all previous messages.
Rule 2 — If last message is Russian → reply ONLY in Russian. Translate everything.
Rule 3 — If last message is Uzbek (Latin or Cyrillic) → reply ONLY in Uzbek Cyrillic.
Rule 4 — Never mix languages. One reply = one language.
Rule 5 — Before sending, check every word. If one wrong-language word is found → rewrite.

BANNED in Russian replies (will break the rule):
майдон, баландлик, лойиҳа, шаҳар, исм, рақам, неча, қанча, уй, хона, боғланади, мутахассис

BANNED in Uzbek replies (will break the rule):
площадь, высота, проект, город, имя, номер, сколько, дом, свяжется, специалист

━━━━━━━━━━━━━━━━━━━━━━
COMPANY INFO (Campaign)
━━━━━━━━━━━━━━━━━━━━━━

{campaign_block}

━━━━━━━━━━━━━━━━━━━━━━
SALES RULES (AI Config)
━━━━━━━━━━━━━━━━━━━━━━

{config_block}

━━━━━━━━━━━━━━━━━━━━━━
LEAD STATUS
━━━━━━━━━━━━━━━━━━━━━━

{lead_block}

━━━━━━━━━━━━━━━━━━━━━━
CONTEXT & MEMORY RULES
━━━━━━━━━━━━━━━━━━━━━━

- Read the FULL conversation before replying.
- If the customer already gave their phone number earlier → do NOT ask again. Confirm and close.
- If the customer already gave their name earlier → do NOT ask again.
- If the customer sends digits (e.g. "998901234567" or "90-123-45-67") → treat it as phone number.
- If the customer says "I already sent it" / "already wrote it" → apologize briefly and confirm receipt.
- Never repeat a question the customer already answered.

━━━━━━━━━━━━━━━━━━━━━━
OPERATOR HANDOFF RULES
━━━━━━━━━━━━━━━━━━━━━━

- Sometimes a human operator also replies in this conversation.
- Read all messages before responding. If the human operator already answered a question → do NOT repeat it.
- If you see that contact info was already collected by the operator → treat lead as complete.
- Blend in seamlessly. The customer must never notice a switch between bot and operator.
- If the topic has already moved forward, continue from where it left off.

━━━━━━━━━━━━━━━━━━━━━━
SMART REPLY RULES
━━━━━━━━━━━━━━━━━━━━━━

- Customer says "send me your number" / "how do I contact you" → give: +998874445454
- Customer says "send to Telegram / WhatsApp" → reply: "Xabarni shu raqamga yuboring: +998874445454" (translate to their language)
- Customer says "I sent it in Telegram" → reply: "Yaxshi, mutaxassisimiz siz bilan bog'lanadi." (translate)
- Customer seems unsure after price → do NOT end. Offer alternatives: "Boshqa variantlarni ham ko'rib chiqamiz."
- Customer says "expensive" → do NOT give up. Say we have options. Ask for contact.
- Customer says "I'll think about it" → acknowledge and still ask for contact softly.
- Customer complains about no callback → apologize first, then promise action. Never say "wait patiently."
- Never say: "Бизда Telegram йўқ" / "У нас нет WhatsApp" / "Кутиб туринг" / "Сабр қилинг"

━━━━━━━━━━━━━━━━━━━━━━
RESPONSE FORMAT
━━━━━━━━━━━━━━━━━━━━━━

- Maximum 2 sentences per reply.
- Maximum ~80 characters total.
- One question per message max.
- No paragraphs. No long explanations.
- Do not start mid-conversation with "Ассалому алайкум" or "Здравствуйте" again.
- No filler words: "Конечно!", "Разумеется!", "Албатта!" — unless it sounds completely natural.
- Tone: warm, direct, confident — like a real colleague, not a robot.
"""

    logs = (
        InteractionLog.query
        .filter_by(company_id=company.id, user_instagram_id=sender_id)
        .order_by(InteractionLog.created_at.desc())
        .limit(14)
        .all()
    )

    messages = [{"role": "system", "content": system_prompt}]

    for log in reversed(logs):
        messages.append({"role": "user",      "content": log.message})
        messages.append({"role": "assistant", "content": log.ai_response})

    messages.append({"role": "user", "content": text})

    if len(text.strip().split()) <= 2:
        messages.insert(1, {
            "role": "system",
            "content": (
                "The user's message is very short (1–2 words). "
                "Reply briefly and naturally. "
                "Ask a question ONLY if it is the clear next step in the sales flow."
            )
        })

    response = _call_gpt(
        api_key=company.openai_token,
        messages=messages,
        temperature=0.5,
        max_tokens=120,
        presence_penalty=0.3,
        frequency_penalty=0.5,
    )
    reply = response.choices[0].message.content.strip()

    if len(logs) >= 3:
        last_replies = [log.ai_response.lower().strip() for log in logs[:3]]
        if reply.lower().strip() in last_replies:
            messages.insert(1, {
                "role": "system",
                "content": (
                    "Your last replies were repetitive. "
                    "This time rewrite completely: different structure, different words, same meaning."
                )
            })
            response = _call_gpt(
                api_key=company.openai_token,
                messages=messages,
                temperature=0.75,
                max_tokens=120,
                presence_penalty=0.7,
                frequency_penalty=0.7,
            )
            reply = response.choices[0].message.content.strip()

    sentry_sdk.logger.warning(f"get_ai_reply | reply={reply!r}")
    return reply

def get_full_name(text, company_id):
    sentry_sdk.logger.warning(f"get_full_name | text={text!r} | company_id={company_id}")

    company = Company.query.filter_by(id=company_id).first()

    system_prompt = (
        "You are a JSON-only extractor. "
        "Extract a person's name or full name from the text. "
        "If found, return it as-is. If not found, return null. "
        "No explanation. No extra text. JSON only."
    )

    response = _call_gpt(
        api_key=company.openai_token,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": text},
        ],
        temperature=0.0,
        max_tokens=50,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "name_extractor",
                "schema": {
                    "type": "object",
                    "properties": {"name": {"type": ["string", "null"]}},
                    "required": ["name"],
                },
            },
        },
    )

    data = json.loads(response.choices[0].message.content)
    result = data.get("name") or "no"
    sentry_sdk.logger.warning(f"get_full_name | result={result!r}")
    return result

def get_phone_number(text, company_id):
    sentry_sdk.logger.warning(f"get_phone_number | text={text!r} | company_id={company_id}")

    company = Company.query.filter_by(id=company_id).first()

    system_prompt = (
        "You are a JSON-only extractor. "
        "Extract a phone number from the text. "
        "Accept any format: with spaces, dashes, plus sign, or plain digits. "
        "Return digits only (no spaces, dashes, or symbols). "
        "If no phone number found, return null. "
        "No explanation. No extra text. JSON only."
    )

    response = _call_gpt(
        api_key=company.openai_token,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": text},
        ],
        temperature=0.0,
        max_tokens=50,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "phone_extractor",
                "schema": {
                    "type": "object",
                    "properties": {"phone": {"type": ["string", "null"]}},
                    "required": ["phone"],
                },
            },
        },
    )

    data = json.loads(response.choices[0].message.content)
    result = data.get("phone") or "no"
    sentry_sdk.logger.warning(f"get_phone_number | result={result!r}")
    return result
