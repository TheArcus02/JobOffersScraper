import os


def save_to_file(data, filename, encoding=None):
    os.makedirs('data', exist_ok=True)
    with open(f'data/{filename}', 'w', encoding=encoding) as file:
        file.write(data)
