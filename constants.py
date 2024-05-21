OFFERS_URL = 'https://it.pracuj.pl/praca?et=1%2C3%2C17&itth=33%2C34%2C36%2C37%2C42%2C73%2C76%2C213%2C77&pn=1'
JSON_PATTERN = r'<script\s+id="__NEXT_DATA__"\s+type="application\/json">\{.*?\}<\/script>'
LOGIN_URL = 'https://login.pracuj.pl/api/public/users/sign-in'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'

OFFERS_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
        }}
        .container {{
            padding: 20px;
        }}
        .header {{
            background-color: #f8f8f8;
            padding: 10px 20px;
            border-bottom: 1px solid #ddd;
        }}
        .content {{
            padding: 20px;
        }}
        .offer {{
            margin-bottom: 30px;
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 5px;
        }}
        .offer h2 {{
            color: #333;
            font-size: 18px;
            margin-bottom: 10px;
        }}
        .offer p {{
            margin: 0;
        }}
        .section {{
            margin-bottom: 20px;
        }}
        .section h3 {{
            color: #555;
            font-size: 16px;
            margin-bottom: 10px;
        }}
        .section p, .section ul {{
            margin: 0;
            padding-left: 20px;
        }}
        .list {{
            margin: 0;
            padding: 0;
            list-style: none;
        }}
        .list li {{
            padding: 5px 0;
        }}
        .uri {{
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>New Job Offers</h1>
        </div>
        <div class="content">
            {offers}
        </div>
    </div>
</body>
</html>
"""
