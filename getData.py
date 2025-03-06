import pyperclip
import yaml

def generate_script(csrf_token, country, brand, length):
    script = f"""
const X_csrf_token = '{csrf_token}';

const COUNTRY = '{country}';
const BRAND = '{brand}';
const LENGTH = {length};

const formData = new FormData();
formData.append('draw', '1');
formData.append('columns[0][data]', 'BIN');
formData.append('columns[0][name]', 'BIN');
formData.append('columns[0][searchable]', 'true');
formData.append('columns[0][orderable]', 'true');
formData.append('columns[0][search][value]', '');
formData.append('columns[0][search][regex]', 'false');
formData.append('columns[1][data]', 'card_brand');
formData.append('columns[1][name]', 'card_brand');
formData.append('columns[1][searchable]', 'true');
formData.append('columns[1][orderable]', 'true');
formData.append('columns[1][search][value]', '');
formData.append('columns[1][search][regex]', 'false');
formData.append('columns[2][data]', 'card_type');
formData.append('columns[2][name]', 'card_type');
formData.append('columns[2][searchable]', 'true');
formData.append('columns[2][orderable]', 'true');
formData.append('columns[2][search][value]', '');
formData.append('columns[2][search][regex]', 'false');
formData.append('columns[3][data]', 'card_level');
formData.append('columns[3][name]', 'card_level');
formData.append('columns[3][searchable]', 'true');
formData.append('columns[3][orderable]', 'true');
formData.append('columns[3][search][value]', '');
formData.append('columns[3][search][regex]', 'false');
formData.append('columns[4][data]', 'country_name');
formData.append('columns[4][name]', 'country_name');
formData.append('columns[4][searchable]', 'true');
formData.append('columns[4][orderable]', 'true');
formData.append('columns[4][search][value]', '');
formData.append('columns[4][search][regex]', 'false');
formData.append('columns[5][data]', 'issuer_name');
formData.append('columns[5][name]', 'issuer_name');
formData.append('columns[5][searchable]', 'true');
formData.append('columns[5][orderable]', 'true');
formData.append('columns[5][search][value]', '');
formData.append('columns[5][search][regex]', 'false');
formData.append('start', '0');
formData.append('search[value]', '');
formData.append('search[regex]', 'false');
formData.append('filter_brand', BRAND);
formData.append('filter_country', COUNTRY);
formData.append('filter_type', '');
formData.append('filter_level', '');
formData.append('filter_issuer', '');
if (LENGTH !== -1) {{
    formData.append('filter_length', LENGTH);
}}

const url = 'https://bincheck.io/api/v1.5/fectch';
fetch(url, {{
    method: 'POST', // Specify the method as POST
    headers: {{
        'X-CSRF-TOKEN': X_csrf_token,
        'X-Requested-With': 'XMLHttpRequest'
    }},
    body: formData
}})
    .then(response => {{
        if (!response.ok) {{
            throw new Error('Network response was not ok');
        }}
        return response.json();
    }})
    .then(data => {{
        console.log(data.data);
    }})
    .catch(error => {{
        console.error('Error:', error);
    }});
"""
    return script

if __name__ == '__main__':
    with open('config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    script = generate_script(config['csrf_token'], config['country'], config['brand'], config['length'])
    pyperclip.copy(script)
    print('Script đã được copy vào clipboard')