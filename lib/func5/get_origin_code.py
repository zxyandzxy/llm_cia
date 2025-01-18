import chardet
import re

def detect_encoding_and_read_file(file_path):
    raw = open(file_path, 'rb').read()
    result = chardet.detect(raw)
    encoding = result['encoding']

    in_package_section = False
    result_lines = []

    try:
        with open(file_path, 'r', encoding=encoding) as file:
            for line in file:
                stripped_line = line.strip()

                if in_package_section:
                    result_lines.append(line)
                elif stripped_line.startswith('package'):
                    in_package_section = True
                    result_lines.append(line)

    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    code = ''.join(result_lines)
    code = re.sub(r'//.*\n', '', code)
    code = re.sub(r'/\*[\s\S]*?\*/', '', code)
    lines = code.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    cleaned_code = '\n'.join(non_empty_lines)
    return cleaned_code.strip()
