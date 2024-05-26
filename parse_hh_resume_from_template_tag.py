import json
from bs4 import BeautifulSoup
import urllib3

http = urllib3.PoolManager()
request = http.request('GET', 'https://hh.ru/resume/bc20b31cff02cb290a0039ed1f61314e795061')
#request = http.request('GET', 'https://hh.ru/resume/283a0317ff09c641530039ed1f31664d39416e')

def parse_page_source(html_content):
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the <template> tag and extract its content
    template_tag = soup.find('template')
    if template_tag:
        template_content = template_tag.decode_contents()
        try:
            # Parse the JSON content inside the <template> tag
            json_content = json.loads(template_content)
            parsed_templates = [json_content]
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON inside <template> tag: {e}")
            return
    else:
        print("No <template> tag found")
        return

    resume = parsed_templates[0].get('resume', {})
    
    last_name = resume.get('lastName', {}).get('value', None)
    first_name = resume.get('firstName', {}).get('value', None)
    middle_name = resume.get('middleName', {}).get('value', None)
    
    phone = None
    if 'phone' in resume and 'value' in resume['phone']:
        phone = resume['phone']['value'][0].get('formatted', None)
        
    email = resume.get('email', {}).get('value', None)
    
    skype_text = None
    linkedin_url = None
    for item in resume.get('personalSite', {}).get('value', []):
        if item.get('type') == 'skype':
            skype_text = item.get('text')
        elif item.get('type') == 'linkedin':
            linkedin_url = item.get('url')
    
    salary_value = resume.get('salary', {}).get('value', {})
    salary = str(salary_value.get('amount', '')) if salary_value else None
    
    birth_date = {
        "year": None,
        "month": None,
        "day": None
    }
    birthday = resume.get('birthday', {}).get('value', None)
    if birthday:
        year, month, day = map(int, birthday.split('-'))
        birth_date = {
            "year": year,
            "month": month,
            "day": day
        }
    
    resume_url = parsed_templates[0].get('authUrl', {}).get('backurl', '')
    #resume id only
    #source_id = resume_url.split('/')[-1] if resume_url else None
    #1 assuming the current position is one with no endDate
    for job in resume.get('experience', {}).get('value', None):
        if job['endDate'] == None:
            company =  job['companyName']
            position = job['position']
    
    #2 assuming the current position is first one in the list
    # job = resume.get('experience', {}).get('value', None)[0]
    # company =  job['companyName']
    # position = job['position']
    
    config = parsed_templates[0].get('config', {})
    image_resizing_cdn_host = config.get('imageResizingCdnHost', '')
    photo_url = resume.get('photoUrls', {}).get('value', None)[0].get('big',None)
    print(resume.get('photoUrls', {}))

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
                "phone": phone,
                "email": email,
                "skype_username": skype_text,
                "linkedin": linkedin_url,
                "telegram_username": None  # Assuming there's no 'telegram_username' key in the data
            },
            "current_position": {
                "position": position,
                "company": company
            },
            "salary": salary,
            "birth_date": birth_date,
            "source_id": None,
            "photo_file_uuid": image_resizing_cdn_host+photo_url,
            "resume": resume_url,
            "address": None,
        }
    }
    return data

# Call the function to parse and print the prettified JSON
parsed_data = parse_page_source(request.data.decode('utf-8'))

print(json.dumps(parsed_data, ensure_ascii=False, indent=2))
