import os
import subprocess
from lib.get_file_path import find_first_file
from lib.func3.conceptual_dependency import calculate_similarity_between_files_split_with_method

project2root = {
        "freecol": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\\freecol",
        "hsqldb": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\hsqldb",
        "JAMWiki": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\JAMWiki",
        "jEdit": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\jEdit",
        "JHotDraw": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\JHotDraw",
        "Makagiga": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\Makagiga",
        "OmegaT": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\OmegaT"
    }

def remove_lock_files(repo_path):
    for root, dirs, files in os.walk(repo_path):
        svn_dir = os.path.join(root, '.svn')
        lock_file = os.path.join(svn_dir, 'lock')
        if os.path.exists(lock_file):
            print(f"Removing lock file at {lock_file}")
            os.remove(lock_file)

def svn_update_to_revision(revision, path='.'):
    try:
        remove_lock_files(path)
        command = ['svn', 'cleanup', path]
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        command = ['svn', 'update', '--revision', str(revision), path]
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            print(f"Successfully updated to revision {revision}.")
        else:
            print("Failed to update.")

    except subprocess.CalledProcessError as e:
        pass

def get_conceptual_dependency(parent_folder):
    project_name = parent_folder.split("\\")[-1]
    with os.scandir(parent_folder) as entries:
        for entry in entries:
            if entry.is_dir():
                folder_path = entry.path
                commit_num = folder_path.split("\\")[-1]

                coreclass_path = os.path.join(folder_path, "coreclass.txt")
                with open(coreclass_path, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        if line == lines[0]:
                            coreclass = line.split(':')[0].strip()
                            break

                traditional_cia_result = []
                Impactminer_path = os.path.join(folder_path, "ImpactminerResult", f"{coreclass}.txt")
                with open(Impactminer_path, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        traditional_cia_result.append(line.strip())

                svn_update_to_revision(commit_num, project2root[project_name])

                file1_path = find_first_file(project_name, coreclass + '.java')
                conceptual_result = []

                for entity in traditional_cia_result:
                    file2_path = find_first_file(project_name, entity + '.java')
                    if file2_path is None:
                        conceptual_result.append(f"{entity} has been removed due to the repository version iteration\n")
                    else:
                        conceptual = calculate_similarity_between_files_split_with_method(file1_path, file2_path)
                        conceptual_result.append(f"{entity} : {str(conceptual)}\n")

                output_path = os.path.join(
                    "D:\science_research\change_impact_analysis\llm_cia\conceptual_dependency_result",
                    project_name, f"{commit_num}_{coreclass}.txt")
                with open(output_path, 'w', encoding='utf-8') as file:
                    for line in conceptual_result:
                        file.write(line)
                print(f"Data has successfully write to {output_path}")

if __name__ == "__main__":
    parent_folder = "D:\science_research\change_impact_analysis\llm_cia\experiment_data"
    project = ['freecol', 'hsqldb', 'JAMWiki', 'jEdit', 'JHotDraw', 'Makagiga', 'OmegaT']
    for project_name in project:
        path = os.path.join(parent_folder, f"{project_name}Result.txt")
        get_conceptual_dependency(path)