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
    ] and "финтех" in subject_area and location == "РФ":
        return CHANNEL["Analyst_job_fintech"]
    elif category in [
        "бизнес-аналитик",
        "аналитик бизнес-процессов",
        "системный аналитик",
        "system owner",
        "проектировщик ИТ-решений",
    ] and subject_area in ["e-commerce", "ритейл", "логистика"] and location == "РФ":
        return CHANNEL["Analyst_job_retail"]
    elif category in [
        "бизнес-аналитик",
        "аналитик бизнес-процессов",
        "системный аналитик",
        "system owner",
        "проектировщик ИТ-решений",
    ] and location == "РФ":
        return CHANNEL["Analyst_job_other"]
    else:
        return CHANNEL["Analyst_job_other_countries"]

