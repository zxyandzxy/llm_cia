import os
from pathlib import Path

from lib.func1 import coupling_dependecy
from lib.func5 import get_origin_code
from lib.func3 import conceptual_dependency
from lib.func4 import call_graph
from lib import get_file_path

class repositoryInterface():
    def __init__(self, project_name, commit_num):
        self._project_name = project_name
        self._commit_num = commit_num
        self._initial_code_getter = 'get_co_change_relationship'
        self._coreclass = self.get_coreclass()
        self._project2root = {
            "freecol": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\\freecol",
            "hsqldb": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\hsqldb",
            "JAMWiki": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\JAMWiki",
            "jEdit": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\jEdit",
            "JHotDraw": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\JHotDraw",
            "Makagiga": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\Makagiga",
            "OmegaT": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\OmegaT"
        }
        self._java_files = self.collect_java_files(self._project2root[self._project_name])

    def get_coreclass(self):
        base_path = 'D:\science_research\change_impact_analysis\llm_cia\experiment_data'
        file_path = os.path.join(base_path, self._project_name, self._commit_num, 'ImpactminerResult')
        try:
            if not os.path.exists(file_path):
                print(f"Error: The file at {file_path} does not exist.")
                return None
            file_names = os.listdir(file_path)
            coreclass = file_names[0].split(".")[0]
            return coreclass
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")
            return None

    def collect_java_files(self, project_root):
        java_files = []
        for root, _, files in os.walk(project_root):
            for file in files:
                if file.endswith('.java'):
                    java_files.append(Path(root) / file)
        return java_files

    def get_coupling_dependencies(self, entity1, entity2):
        if (entity1.endswith('.java')):
            entity1 = entity1[:-5]
        if (entity2.endswith('.java')):
            entity2 = entity2[:-5]

        file_path1 = get_file_path.find_first_file(project_name=self._project_name, filename=entity1 + '.java')
        file_path2 = get_file_path.find_first_file(project_name=self._project_name, filename=entity2 + '.java')
        if file_path1 is None and file_path2 is None:
            return [f"{entity1} and {entity2} have been removed from the project due to project version iteration"]
        if file_path1 is None:
            return [f"{entity1} has been removed from the project due to project version iteration"]
        if file_path2 is None:
            return [f"{entity2} has been removed from the project due to project version iteration"]
        return coupling_dependecy.run_jar("D:\science_research\change_impact_analysis\llm_cia\lib\\func1\coupling_dependency-1.0.jar", file_path1, file_path2)

    def get_co_change_relationship(self, entity):
        if (entity.endswith('.java')):
            entity = entity[:-5]
        relationships = []
        file_path = 'D:\science_research\change_impact_analysis\llm_cia\lib\\func2\\' + self._project_name + 'Result.txt'
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith(entity + ' :'):
                        matches = line.split(':')[1].strip()
                        matches = matches.split('|')
                        for match in matches:
                            match = match.strip()
                            cur = match.split(',')
                            if len(cur) == 3:
                                impact_class = cur[0].strip().replace("(", '')
                                support = cur[1].strip()
                                confidence = cur[2].strip().replace(")", '')
                                relationships.append((impact_class, support, confidence))
                        break

        except FileNotFoundError:
            print("Error: The file was not found. file_path = " + file_path + ", entity = " + entity)
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")
        if len(relationships) == 0:
            return ["No co-change relationship found for this entity"]
        return relationships

    def get_conceptual_coupling(self, entity1, entity2):
        if (entity1.endswith('.java')):
            entity1 = entity1[:-5]
        if (entity2.endswith('.java')):
            entity2 = entity2[:-5]

        file_path1 = get_file_path.find_first_file(project_name=self._project_name, filename=entity1 + '.java')
        file_path2 = get_file_path.find_first_file(project_name=self._project_name, filename=entity2 + '.java')
        if file_path1 is None and file_path2 is None:
            return [f"{entity1} and {entity2} have been removed from the project due to project version iteration"]
        if file_path1 is None:
            return [f"{entity1} has been removed from the project due to project version iteration"]
        if file_path2 is None:
            return [f"{entity2} has been removed from the project due to project version iteration"]

        return str(conceptual_dependency.calculate_similarity_between_files_split_with_method(file_path1, file_path2))

    def get_call_graph(self, entity):
        if (entity.endswith('.java')):
            entity = entity[:-5]
        file_path = get_file_path.find_first_file(self._project_name, entity + '.java')
        if file_path is None:
            return f"{entity} has been removed from the project due to project version iteration"
        imports = call_graph.parse_imports(file_path)
        project_defined_classes = call_graph.match_project_classes(self._project2root[self._project_name], imports, self._java_files)
        return project_defined_classes

    def get_origin_code(self, entity):
        if (entity.endswith('.java')):
            entity = entity[:-5]
        file_path = get_file_path.find_first_file(project_name=self._project_name, filename=entity + '.java')
        if file_path is None:
            return f"{entity} has been removed from the project due to project version iteration"
        java_code_string = get_origin_code.detect_encoding_and_read_file(file_path)
        if java_code_string is not None:
            return java_code_string
        return None

    @property
    def fname2func(self):
        fname2func = {
            "get_coupling_dependencies": self.get_coupling_dependencies,
            "get_co_change_relationship": self.get_co_change_relationship,
            "get_conceptual_coupling": self.get_conceptual_coupling,
            "get_call_graph": self.get_call_graph,
            "get_origin_code": self.get_origin_code,
        }
        return fname2func