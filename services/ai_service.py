import json
import openai
import sentry_sdk
from models.company import Company
from models.campaign import Campaign
from models.ai_config import AiConfig
from models.interaction_log import InteractionLog

def detect_language(text):
    """
    Matndan tilni aniqlash: Uzbek, Russian yoki English.
    """
    text_low = text.lower()

    uz_keywords = [
        "qancha", "nech pul", "kurs", "narxi", "qayerda", "iltimos",
        "uzbek", "o'z", "sizda", "qanday"
    ]
    ru_keywords = [
        "сколько", "цена", "руб", "курс стоит", "пожалуйста", "сегодня",
        "привет", "здравствуйте", "да", "нет"
    ]
    en_keywords = [
        "how much", "price", "hello", "course", "please", "cost", "hi"
    ]

    if any(k in text_low for k in en_keywords):
        return "en"
    if any(k in text_low for k in ru_keywords):
        return "ru"
    if any(k in text_low for k in uz_keywords):
        return "uz"

    # Default -> Uzbek
    return "uz"

def get_ai_reply(sender_id, text, company_id, have_full_name, have_phone_number):
    sentry_sdk.logger.warning(f"Instagram webhook post get_ai_reply = text - {text}, company_id - {company_id}")
    
    company = Company.query.filter_by(id=company_id).first()
    openai.api_key = company.openai_token

    campaigns = Campaign.query.filter_by(company_id=company.id, is_active=True).all()
    campaign_texts = "\n\n".join([
        f"--- {c.title} ---\n{c.content}"
        for c in campaigns
    ])

    ai_configs = AiConfig.query.filter_by(company_id=company.id).all()

    ai_templates = "\n\n".join([
        f"[{cfg.template_name}]\n{cfg.template_text}"
        for cfg in ai_configs
        if cfg.use_openai is True
    ])

    user_lang = detect_language(text)

    if user_lang == "uz":
        language_instruction = "Reply only in casual Uzbek (latin), friendly and natural."
    elif user_lang == "ru":
        language_instruction = "Reply only in friendly, spoken Russian."
    else:
        language_instruction = "Reply only in casual, conversational English."

    system_prompt = f"""
You are a real Instagram manager (22–28 years old).
You chat like a normal human, not customer support.

Campaign information:
{campaign_texts}

Instructions:
{ai_templates}

Language rule:
{language_instruction}

Rules:
- Answer ONLY using campaign information.
- Be short, clear, human-like.
- Professional but NOT formal.
- Never repeat yourself.
- Do not greet again if already greeted.
- If question not in campaigns, respond with:
  - uz: Bu savol kompaniya materiallarida mavjud emas.
  - ru: Этот вопрос отсутствует в материалах компании.
  - en: This question is not available in the company materials.
- If full name exists ({have_full_name}) → do not ask.
- If phone exists ({have_phone_number}) → do not ask.
- If message is unclear or very short → ask follow-up.
""" 
    messages = [
        {"role": "system", "content": system_prompt}
    ]

    interaction_log_list = InteractionLog.query.filter_by(company_id=company.id, user_instagram_id=sender_id).order_by(InteractionLog.created_at.desc()).limit(12).all()
    for log in reversed(interaction_log_list):
        messages.append({"role": "user", "content": log.message})
        messages.append({"role": "assistant", "content": log.ai_response})

    messages.append({"role": "user", "content": text})

    if len(text.split()) <= 2:
        messages.insert(1, {
            "role": "system",
            "content": "User message is very short. Ask a natural follow-up question."
        })

    response = openai.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.85,
        max_tokens=120,
        presence_penalty=0.6,
        frequency_penalty=0.7,
        messages=messages
    )

    reply = response.choices[0].message.content
    last_ai = [log.ai_response.lower().strip() for log in interaction_log_list[:3]]

    if reply.lower().strip() in last_ai:
        messages.insert(1, {
            "role": "system",
            "content": "Rewrite your answer in a completely different way."
        })
        response = openai.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=1.0,
            max_tokens=120,
            presence_penalty=0.8,
            frequency_penalty=0.8,
            messages=messages
        )
        reply = response.choices[0].message.content
        
    sentry_sdk.logger.warning(f"Instagram webhook post get_ai_reply = response - {reply}")
    return reply

def get_full_name(text, company_id):
    sentry_sdk.logger.warning(f"Instagram webhook post get_full_name = text - {text}, company_id - {company_id}")
    
    company = Company.query.filter_by(id=company_id).first()
    openai.api_key = company.openai_token

    system_prompt = """
Sen faqat JSON qaytaradigan analizchisiz.
Text ichidan ism yoki ism-familyani aniqlaysan.
Agar ism yoki ism-familya bo‘lsa — faqat shu nomni qaytarasan.
Agar yo‘q bo‘lsa — name maydoni null bo‘lsin.
Hech qachon izoh, tushuntirish yoki boshqa gap yozma.
"""

    response = openai.chat.completions.create(
        model="gpt-4.1-mini",
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "name_extractor",
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": ["string", "null"]}
                    },
                    "required": ["name"]
                }
            }
        },
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
    )
    raw_json = response.choices[0].message.content
    data = json.loads(raw_json)

    sentry_sdk.logger.warning(f"Instagram webhook post get_full_name = response - {str(data)}")
    return data["name"] if data["name"] else "no"

def get_phone_number(text, company_id):
    sentry_sdk.logger.warning(f"Instagram webhook post get_phone_number = text - {text}, company_id - {company_id}")
    
    company = Company.query.filter_by(id=company_id).first()
    openai.api_key = company.openai_token

    system_prompt = """
Sen faqat JSON qaytaradigan analizchisiz.
Text ichidan telefon raqamni aniqlaysan.
Agar telefon raqam bo‘lsa — faqat raqamni qaytar.
Agar yo‘q bo‘lsa — phone maydoni null bo‘lsin.
Qo‘shimcha gap yozma.
"""

    response = openai.chat.completions.create(
        model="gpt-4.1-mini",
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "phone_extractor",
                "schema": {
                    "type": "object",
                    "properties": {
                        "phone": {"type": ["string", "null"]}
                    },
                    "required": ["phone"]
                }
            }
        },
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
    )
    raw_json = response.choices[0].message.content
    data = json.loads(raw_json)
    
    sentry_sdk.logger.warning(f"Instagram webhook post get_phone_number = response - {str(data)}")
    return data["phone"] if data["phone"] else "no"
