import subprocess
import os
from pathlib import Path
import re
from lib.get_file_path import find_first_file

# Collects the paths to all .java files in the project directory.
def collect_java_files(project_root):
    java_files = []
    for root, _, files in os.walk(project_root):
        for file in files:
            if file.endswith('.java'):
                java_files.append(Path(root) / file)
    return java_files

# Parses the import statement in a given .java file.
def parse_imports(file_path):
    imports = set()
    jdk_packages = {'java', 'javax', 'org.omg', 'sun', 'com.sun'}

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
        matches = re.findall(r'^import\s+([a-zA-Z0-9_.]+)\.?(?=\*?;)', content, re.MULTILINE)

        for match in matches:
            package = match.split('.')[0]
            if not any(package.startswith(jdk_prefix) for jdk_prefix in jdk_packages):
                imports.add(match)

    return imports

# Parses the import statement in a given .java file.
def parse_imports_second(file_path, project_name):
    imports = set()
    jdk_packages = {'java', 'javax', 'org.omg', 'sun', 'com.sun'}

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
        matches = re.findall(r'^import\s+([a-zA-Z0-9_.]+)\.?(?=\*?;)', content, re.MULTILINE)

        for match in matches:
            package = match.split('.')[0]
            if not any(package.startswith(jdk_prefix) for jdk_prefix in jdk_packages):
                imports.add(match)

    second_imports = set()
    for imp in imports:
        file_name = imp.split('.')[-1]
        new_path = find_first_file(project_name, file_name + '.java')
        if new_path is not None:
            new_imports = parse_imports(new_path)
        second_imports.update(new_imports)

    return second_imports

# Match the imported classes with the Java classes defined in the project
def match_project_classes(project_root, imported_classes, java_files):
    project_classes = set()

    class_to_file = {}
    for file in java_files:
        relative_path = file.relative_to(project_root).with_suffix('')
        full_class_name = str(relative_path).replace(os.sep, '.')
        class_to_file[full_class_name] = file

    for imported_class in imported_classes:
        if any(imported_class in class_file for class_file in class_to_file):
            project_classes.add(imported_class)

    project_classes = list(project_classes)
    project_classes = [s.split('.')[-1] for s in project_classes]
    return project_classes

def run_jar(jar_path, *args):
    cmd = ['java', '-jar', jar_path] + list(args)

    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        s = result.stdout.decode()
        s = s.replace("[", '').replace("]", '').replace(" ", '').split(',')
        return s
    except subprocess.CalledProcessError as e:
        return "An error occurred while running the jar file:", e.stderr.decode('utf-8', errors='ignore')
