from utils.channels import CHANNEL


def routing(data):
    category = data['category']
    subject_area = data['subjects']
    location = data['location']

    if category == 'аналитик 1С':
        return CHANNEL["Analystic_job"]
    elif category in ["BI-аналитик", "аналитик данных", "продуктовый аналитик"]:
        return CHANNEL["Data_Analysis_job"]
    elif category in [
        "бизнес-аналитик",
        "аналитик бизнес-процессов",
        "системный аналитик",
        "system owner",
        "проектировщик ИТ-решений",
    ] and "финтех" in subject_area and location == "🇷🇺 Россия":
        return CHANNEL["Analyst_job_fintech"]
    elif category in [
        "бизнес-аналитик",
        "аналитик бизнес-процессов",
        "системный аналитик",
        "system owner",
        "проектировщик ИТ-решений",
    ] and subject_area in ["e-commerce", "ритейл", "логистика"] and location == "🇷🇺 Россия":
        return CHANNEL["Analyst_job_retail"]
    elif category in [
        "бизнес-аналитик",
        "аналитик бизнес-процессов",
        "системный аналитик",
        "system owner",
        "проектировщик ИТ-решений",
    ] and "medtech" in subject_area and location == "🇷🇺 Россия":
        return CHANNEL["Analyst_job_medtech"]
    elif category in [
        "бизнес-аналитик",
        "аналитик бизнес-процессов",
        "системный аналитик",
        "system owner",
        "проектировщик ИТ-решений",
    ] and "стройтех" in subject_area and location == "🇷🇺 Россия":
        return CHANNEL["Analyst_job_proptech"]
    elif category in [
        "бизнес-аналитик",
        "аналитик бизнес-процессов",
        "системный аналитик",
        "system owner",
        "проектировщик ИТ-решений",
    ] and "госсистемы" in subject_area and location == "🇷🇺 Россия":
        return CHANNEL["Analyst_job_gostech"]
    elif category in [
        "бизнес-аналитик",
        "аналитик бизнес-процессов",
        "системный аналитик",
        "system owner",
        "проектировщик ИТ-решений",
    ] and location == "🇷🇺 Россия":
        return CHANNEL["Analyst_job_other"]
    else:
        return CHANNEL["Analyst_job_other_countries"]


def repeat_sending(data):
    subject_area = data['subjects']
    location = data['location']

    if "medtech" in subject_area and location == "🌐 Не важно":
        return CHANNEL["Analyst_job_medtech"]
    elif "стройтех" in subject_area and location == "🌐 Не важно":
        return CHANNEL["Analyst_job_proptech"]
    elif "госсистемы" in subject_area and location == "🌐 Не важно":
        return CHANNEL["Analyst_job_gostech"]
    else:
        return None
