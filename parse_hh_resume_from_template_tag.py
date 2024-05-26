import json
from bs4 import BeautifulSoup

def parse_page_source(input_json_str):
    # Load the JSON data from the input string
    data = json.loads(input_json_str)
    
    # Extract the extension_data from the JSON data
    extension_data = data.get('extension_data', {})
    
    # Extract the requests array from extension_data
    requests = extension_data.get('requests', [])
    
    # Extract the pageSource and parse the JSON object inside the <template> tag from each request's body
    parsed_templates = []
    for request in requests:
        page_source = request.get('body', {}).get('pageSource', '')
        if page_source:
            # Parse the HTML content directly with BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')
            template_tag = soup.find('template')
            if template_tag:
                template_content = template_tag.decode_contents()
                try:
                    # Parse the JSON content inside the <template> tag
                    json_content = json.loads(template_content)
                    parsed_templates.append(json_content)
                except json.JSONDecodeError as e:
                    print(f"Failed to decode JSON inside <template> tag: {e}")
    
    # Convert the parsed templates to a prettified JSON string
    parsed_templates_str = json.dumps(parsed_templates, indent=4)
    
    # Write the prettified JSON string to a file
    with open('parsed_templates.txt', 'w', encoding='utf-8') as file:
        file.write(parsed_templates_str)

# Load the input JSON file
with open('./applicant.json', 'r', encoding='utf-8') as file:
    input_json_str = file.read()

# Call the function to parse and print the prettified JSON
parse_page_source(input_json_str)
