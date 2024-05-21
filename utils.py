def save_to_file(data, filename, encoding=None):
    with open(f'data/{filename}', 'w', encoding=encoding) as file:
        file.write(data)
