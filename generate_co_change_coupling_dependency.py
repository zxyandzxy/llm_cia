import os
from lib.get_file_path import find_first_file
from lib.func1.coupling_dependecy import run_jar

def get_coupling_dependency(parent_folder, project_name):
    with open(parent_folder, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()

            coreclass = line.split(':')[0].strip()
            relationships = []
            matches = line.split(':')[1].strip()
            matches = matches.split('|')

            for match in matches:
                match = match.strip()
                cur = match.split(',')
                if len(cur) == 3:
                    impact_class = cur[0].strip().replace("(", '')
                    relationships.append(impact_class.strip())

            coupling_result = []
            file1_path = find_first_file(project_name, coreclass)
            for entity in relationships:
                file2_path = find_first_file(project_name, entity)
                if file2_path is None:
                    coupling_result.append(f"{entity} has been removed due to the repository version iteration\n")
                else:
                    coupling = run_jar("D:\science_research\change_impact_analysis\llm_cia\lib\\func1\coupling_dependency-1.0.jar",
                                       file1_path, file2_path)
                    coupling_result.append(f"{entity} : {str(coupling)}\n")

            output_path = os.path.join("D:\science_research\change_impact_analysis\llm_cia\co_change_coupling_dependency", project_name, f"{coreclass}.txt")
            with open(output_path, 'w', encoding='utf-8') as file:
                for line in coupling_result:
                    file.write(line)
            print(f"Data has successfully write to {output_path}")

if __name__ == "__main__":
    parent_folder = "D:\science_research\change_impact_analysis\llm_cia\lib\\func2"
    project = ['freecol', 'hsqldb', 'JAMWiki', 'jEdit', 'JHotDraw', 'Makagiga', 'OmegaT']
    for project_name in project:
        path = os.path.join(parent_folder, f"{project_name}Result.txt")
        get_coupling_dependency(path, project_name)