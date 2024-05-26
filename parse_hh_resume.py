import urllib3
import re
from bs4 import BeautifulSoup
import json

http = urllib3.PoolManager()
request = http.request('GET', 'https://hh.ru/resume/%id%')


def parse_html_to_json(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    def get_text(selector, attribute=None):
        element = soup.select_one(selector)
        if element:
            if attribute:
                return element.get(attribute, None)
            else:
                return element.get_text(strip=True)
        return None

    def parse_salary(selector):
        salary_text = get_text(selector)
        if salary_text:
            # Remove non-numeric characters except for thousand separators
            salary_text = salary_text.replace(' ', '').replace('₽', '').strip()
            # Extract the numeric part
            salary_number = re.sub(r'[^\d]', '', salary_text)
            return str(salary_number) if salary_number else None
        return None

    def get_telegram_username(selector):
        text = get_text(selector)
        if text and "telegram" in text:
            return text.split("telegram")[-1].strip()
        return None

    def parse_birthday(selector):
        birthday_text = get_text(selector)
        if birthday_text:
            parts = birthday_text.split()
            if len(parts) == 3:
                day = parts[0]
                month = parts[1]
                year = parts[2]
                return {"day": day, "month": month, "year": year}
        return {"day": None, "month": None, "year": None}

    def get_src(selector):
        element = soup.select_one(selector)
        return element['src'] if element else None

    def get_linkedin(selector):
        element = soup.select_one(selector)
        if element:
            link = element.find_parent('a', href=True)
            if link:
                return link['href']
        return None

    def get_skype(selector):
        text = get_text(selector)
        if text:
            return text.strip()
        return None

    full_name = get_text('[data-qa="resume-personal-name"]')
    if full_name:
        name_parts = full_name.split()
        last_name = name_parts[0] if len(name_parts) > 0 else None
        first_name = name_parts[1] if len(name_parts) > 1 else None
        middle_name = name_parts[2] if len(name_parts) > 2 else None
    else:
        first_name = last_name = middle_name = None

    birthday = parse_birthday('[data-qa="resume-personal-birthday"]')

    def parse_template_json():
        template_element = soup.find('template')
        if template_element:
            try:
                return json.loads(template_element.string.strip())
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                return None
        return None

    template_json = parse_template_json()
    if not template_json:
        return None
        
    linkedin_url = get_linkedin('.resume-contact-linkedin')

    data = {
        "new": True,
        "similar_applicant_id": 0,
        "files": [
            {
                "id": 0,
                "file_name": None,
                "file_type": None,
                "size": None,
                "mime_type": None,
                "uuid": None
            }
        ],
        "applicant": {
            "first_name": first_name,
            "last_name": last_name,
            "middle_name": middle_name,
            "contacts": {
                "phone": get_text('[data-qa="resume-contacts-phone"] a[data-qa="resume-contact-preferred"]'),
                "email": get_text('[data-qa="resume-contact-email"]'),
                "skype_username": get_skype('[data-qa="resume-personalsite-skype"]'),
                "linkedin": linkedin_url,
                "telegram_username": get_telegram_username('[data-qa="resume-contacts-phone"] .bloko-translate-guard span')
            },
            "current_position": {
                "position": get_text('[data-qa="resume-block-title-position"]'),
                "company": None
            },
            "salary": parse_salary('[data-qa="resume-block-salary"]'),
            "birth_date": birthday,
            "source_id": None,
            "photo_file_uuid": get_src('[data-qa="resume-photo-image"]'),
            "resume": get_text('link[rel="canonical"]', 'href'),
            "address": get_text('[data-qa="resume-personal-address"]'),
        }
    }
    return data

# Parse the HTML and print JSON
parsed_data = parse_html_to_json(request.data)
print(json.dumps(parsed_data, ensure_ascii=False, indent=2))
