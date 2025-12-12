import json
import openai
import sentry_sdk
from models.company import Company
from models.campaign import Campaign
from models.ai_config import AiConfig

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

    if any(k in text_low for k in ru_keywords):
        return "ru"
    if any(k in text_low for k in uz_keywords):
        return "uz"
    if any(k in text_low for k in en_keywords):
        return "en"

    # Default -> Uzbek
    return "uz"

def get_ai_reply(text, company_id, have_full_name, have_phone_number):
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
        language_instruction = "Har doim faqat o'zbek tilida qisqa, professional javob qaytaring."
    elif user_lang == "ru":
        language_instruction = "Всегда отвечай кратко и профессионально только на русском языке."
    else:
        language_instruction = "Always answer shortly and professionally in English."

    system_prompt = f"""
Siz kompaniyaning AI Assistantisiz.

Kampaniya malumotlari:
{campaign_texts}

Sen uchun configuration - sen shunday ishlashing kerak, shu qoidalarga rioya qil va bular sening maqsading ham:
{ai_templates}

Javob tili:
{language_instruction}

Qoidalar:
- {have_full_name} shu True bo'lsa Ismini soramagin agar False bo'lsa sora.
- {have_phone_number} shu True bo'lsa Telefon raqamini soramagin agar False bo'lsa sora. 
- Javobni faqat yuqoridagi kampaniya ma'lumotlari asosida bering.
- Hech qachon mavzudan tashqari gap yozmagin.
- Har doim professional, qisqa va aniq javob bering.
- Agar savol kampaniyalarda bo'lmasa:
  Uzbekcha: "Bu savol kompaniya materiallarida mavjud emas."
  Ruscha:   "Этот вопрос отсутствует в материалах компании."
  Inglizcha: "This question is not available in the company materials."
"""

    response = openai.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
    )

    sentry_sdk.logger.warning(f"Instagram webhook post get_ai_reply = response - {response.choices[0].message.content}")
    return response.choices[0].message.content

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
