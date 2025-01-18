import torch
import re
import chardet
from transformers import RobertaTokenizer, RobertaModel
from sklearn.metrics.pairwise import cosine_similarity
import javalang
import numpy as np


# Read the source code (delete spaces, delete comments)
def read_raw_file(file_path):
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

# Splitting Java files into elements (methods, fields, etc.)
def split_java_file_to_elements(code):
    try:
        tree = javalang.parse.parse(code)
        elements = []
    except:
        return split_code_by_tokens(code)

    for node in tree.types:
        if isinstance(node, javalang.tree.ClassDeclaration):
            elements.extend(extract_methods_with_javalang(code))
            break
        elif isinstance(node, javalang.tree.InterfaceDeclaration):
            elements.extend(extract_interface_members(node))
            break

    return elements

def split_code_by_tokens(code, max_tokens=450):
    # Use regular expressions to match words, symbols, etc. in Java as the basis for separations
    tokens = re.findall(r'\b\w+\b|[^\w\s]', code)

    if len(tokens) <= max_tokens:
        return [code]

    chunks = []
    current_chunk = []
    current_token_count = 0

    for token in tokens:
        if current_token_count + 1 > max_tokens:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_token_count = 0

        current_chunk.append(token)
        current_token_count += 1

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

# Extract all members of an interface (constants, method signatures)
def extract_interface_members(node):
    members = []

    for member in node.body:
        if isinstance(member, javalang.tree.ConstantDeclaration):
            members.append(extract_constant_declaration(member))
        elif isinstance(member, javalang.tree.MethodDeclaration):
            members.append(extract_method_signature(member))

    return members

# Extract Constant Declarations
def extract_constant_declaration(constant):
    return f"{constant.modifiers} {constant.type.name} {constant.declarators[0].name};"

# Extract method signature
def extract_method_signature(method):
    modifiers = ' '.join(modifier for modifier in method.modifiers)
    parameters = ', '.join(f"{param.type.name} {param.name}" for param in method.parameters)
    return_type = method.return_type.name if method.return_type else "void"
    return f"{modifiers} {return_type} {method.name}({parameters});"

# Extract the source code of all methods in the class
def extract_methods_with_javalang(java_code):
    tree = javalang.parse.parse(java_code)
    methods = []

    for path, node in tree:
        if isinstance(node, javalang.tree.MethodDeclaration):
            start_line, start_column = node.position
            end_line, end_column = get_end_position(node)
            method_code = get_method_code(java_code, start_line, start_column, end_line, end_column)
            methods.append(method_code)

    return methods

def get_end_position(node):
    max_line, max_column = node.position

    def traverse(node):
        nonlocal max_line, max_column
        if hasattr(node, 'position') and node.position is not None:
            child_line, child_column = node.position
            if child_line > max_line or (child_line == max_line and child_column > max_column):
                max_line, max_column = child_line, child_column + len(str(node))

        if isinstance(node, list):
            for item in node:
                if isinstance(item, javalang.tree.Node):
                    traverse(item)
        elif isinstance(node, javalang.tree.Node):
            for child in node.children:
                if isinstance(child, list):
                    for item in child:
                        if isinstance(item, javalang.tree.Node):
                            traverse(item)
                elif isinstance(child, javalang.tree.Node):
                    traverse(child)

    traverse(node.body)
    return max_line, max_column + 1

def get_method_code(java_code, start_line, start_column, end_line, end_column):
    lines = java_code.splitlines(keepends=True)
    method_lines = []

    for i, line in enumerate(lines, start=1):
        if start_line <= i <= end_line:
            if i == start_line:
                method_lines.append(line[start_column - 1:])
            elif i == end_line:
                method_lines.append(line[:end_column])
            else:
                method_lines.append(line)
    method_lines.append('}')
    return ''.join(method_lines).strip()

model_path = "D:\science_research\change_impact_analysis\llm_cia\lib\\func3\microsoft\graphcodebert-base"
tokenizer = RobertaTokenizer.from_pretrained(model_path)
model = RobertaModel.from_pretrained(model_path).to(
    'cuda' if torch.cuda.is_available() else 'cpu')

# Extract code embedded
def get_code_embedding(code, tokenizer, model):
    inputs = tokenizer(code, return_tensors='pt', truncation=True, padding='max_length', max_length=512)
    with torch.no_grad():
        outputs = model(**inputs.to(model.device))
    code_embedding = outputs.last_hidden_state[:, 0, :].squeeze().cpu().numpy()
    return code_embedding

# Calculate the similarity of the two files
def calculate_similarity_between_files_split_with_method(file1_path, file2_path):
    code1 = read_raw_file(file1_path)
    file1_methods = split_java_file_to_elements(code1)
    file1_embeddings = [get_code_embedding(method, tokenizer, model) for method in file1_methods]

    code2 = read_raw_file(file2_path)
    file2_methods = split_java_file_to_elements(code2)
    file2_embeddings = [get_code_embedding(method, tokenizer, model) for method in file2_methods]

    if not file1_embeddings or not file2_embeddings:
        return 0.0

    similarity_matrix = cosine_similarity(file1_embeddings, file2_embeddings)
    average_similarity = np.mean(similarity_matrix)
    return average_similarity



