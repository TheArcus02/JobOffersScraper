import json
import os


def save_to_file(content, filename, encoding=None):
    os.makedirs(os.path.dirname(f'data/{filename}'), exist_ok=True)
    with open(f'data/{filename}', 'w', encoding=encoding) as file:
        if isinstance(content, str):
            file.write(content)
        elif isinstance(content, dict) or isinstance(content, list):
            json.dump(content, file, indent=4)
