import json
from bs4 import BeautifulSoup
import urllib3

http = urllib3.PoolManager()

def fetch_page_content(url):
    try:
        response = http.request('GET', url)
        if response.status == 200:
            return response.data.decode('utf-8')
        else:
            print(f"Failed to fetch page content: HTTP {response.status}")
            return None
    except Exception as e:
        print(f"Error fetching page content: {e}")
        return None

def parse_json_from_template(template_content):
    try:
        json_content = json.loads(template_content)
        return json_content
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON inside <template> tag: {e}")
        return None

def get_value(data, keys, default=None):
    for key in keys:
        if isinstance(data, list):
            try:
                data = data[key]
            except (IndexError, TypeError):
                return default
        else:
            data = data.get(key, {})
    return data if data else default

def get_contact_info(resume, contact_type):
    return next((item.get('text') for item in resume.get('personalSite', {}).get('value', [])
                 if item.get('type') == contact_type), None)

def extract_resume_data(resume):
    birth_date = {"year": None, "month": None, "day": None}
    birthday = resume.get('birthday', {}).get('value', None)
    if birthday:
        year, month, day = map(int, birthday.split('-'))
        birth_date = {"year": year, "month": month, "day": day}

    current_position = next((job for job in resume.get('experience', {}).get('value', [])
                            if job.get('endDate') is None), {})
    print(resume)
    return {
        "first_name": get_value(resume, ['firstName', 'value']),
        "last_name": get_value(resume, ['lastName', 'value']),
        "middle_name": get_value(resume, ['middleName', 'value']),
        "contacts": {
            "phone": get_value(resume, ['phone', 'value', 0, 'formatted']),
            "email": get_value(resume, ['email', 'value']),
            "skype_username": get_contact_info(resume, 'skype'),
            "telegram_username": None
        },
        "current_position": {
            "position": current_position.get('position'),
            "company": current_position.get('companyName')
        },
        "salary": str(get_value(resume, ['salary', 'value', 'amount'], '')),
        "birth_date": birth_date,
        "source_id": None,
        "photo_file_uuid": None,
        "resume": get_value(resume, ['authUrl', 'backurl'], ''),
        "address": None
    }

def parse_page_source(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    template_tag = soup.find('template')
    if not template_tag:
        print("No <template> tag found")
        return None

    json_content = parse_json_from_template(template_tag.decode_contents())
    if not json_content:
        return None

    resume = json_content.get('resume', {})
    config = json_content.get('config', {})
    image_resizing_cdn_host = config.get('imageResizingCdnHost', '')
    photo_url = get_value(resume, ['photoUrls', 'value', 0, 'big'])

    applicant_data = extract_resume_data(resume)
    applicant_data["photo_file_uuid"] = f"{image_resizing_cdn_host}{photo_url}" if photo_url else None

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
        "applicant": applicant_data
    }

    return data

page_content = fetch_page_content('https://hh.ru/resume/bc20b31cff02cb290a0039ed1f61314e795061')
if page_content:
    parsed_data = parse_page_source(page_content)
    print(json.dumps(parsed_data, ensure_ascii=False, indent=2))
