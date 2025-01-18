import os
from pathlib import Path

from ..func1 import coupling_dependecy
from ..func5 import get_origin_code
from ..func3 import conceptual_dependency
from ..func4 import call_graph
from .. import get_file_path

class repositoryInterface():
    FUNCTION_DESCRIPTIONS = [
        {
            "name": "get_coupling_dependencies",
            "description": "This function takes two entities as input and returns the coupling dependencies that exist between the two entities. There are 18 types of coupling dependencies, including Inheritance(IH), Implementing Interface(II), Instanceof (IO), Return Type (RT), and Exception Throws (ET), etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity1": {
                        "type": "string",
                        "description": "File name of the first entity",
                    },
                    "entity2": {
                        "type": "string",
                        "description": "File name of the second entity",
                    },
                },
                "required": ["entity1", "entity2"],
            },
            "return": {
                "type": "array",
                "items": {
                    "type": "string",
                    "description": "the coupling relationship between two entity",
                }
            },
        },
        {
            "name": "get_co_change_relationship",
            "description": "This function takes a target entity as a parameter, and applies data mining to the project's version history to get the recommended synchronised changes, i.e. based on the fact that ‘the programmer who modified this entity in the past also modified ....’. The function will return an array where each element is (the entity name,  the number of supports, the confidence). The explanation of the number of supports and confidence is as follows: if the target entity is A.java, in the version history of A.java has been modified 8 times, at the same time in these 8 modifications of B.java appeared 7 times, then the number of supports is 7, the confidence is 7/8 = 0.875",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity": {
                        "type": "string",
                        "description": "File name of the target entity",
                    },
                },
                "required": ["entity"],
            },
            "return": {
                "type": "array",
                "items": {
                    "type": "object",
                    "description": "{the entity name,  the number of supports, the confidence}",
                },
            },
        },
        {
            "name": "get_conceptual_coupling",
            "description": "This function calculates the semantic similarity of the code of two entities through natural language processing techniques, specified by the cosine similarity, and returns the semantic similarity probability of the two entities.",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity1": {
                        "type": "string",
                        "description": "File name of the first entity",
                    },
                    "entity2": {
                        "type": "string",
                        "description": "File name of the second entity",
                    }
                },
                "required": ["entity1", "entity2"],
            },
            "return": {
                "type": "double",
                "description": "the semantic similarity probability of the two entities",
            }
        },
        {
            "name": "get_call_graph",
            "description": "This function parses out the call information in the target entity, and if another entity is used by the target entity (either through a method call or a direct reference to a variable), then that entity is used as one of the elements of the result array.",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity": {
                        "type": "string",
                        "description": "the file need to analysis",
                    },
                },
                "required": ["entity"],
            },
            "return": {
                "type": "array",
                "items": {
                    "type": "string",
                    "description": "Name of the entity to be called in the target entity",
                },
            },
        },
        {
            "name": "get_origin_code",
            "description": "This function takes one parameter: the name of the entity to be analysed, and returns the source code information for this entity as a string (Remove comment information and extra blank lines)",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity": {
                        "type": "string",
                        "description": "the file need to analysis",
                    },
                },
                "required": ["entity"],
            },
            "return": {
                "type": "string",
                "items": {
                    "type": "string",
                    "description": "the source code information for this entity",
                }
            }
        }
    ]

    def __init__(self, project_name, commit_num):
        self._project_name = project_name
        self._commit_num = commit_num
        self._initial_code_getter = 'get_co_change_relationship'
        self._coreclass = self.get_coreclass()
        self._project2root = {
            "freecol" : "D:\science_research\change_impact_analysis\llm_cia\\repository_data\\freecol",
            "hsqldb" : "D:\sciencce_research\change_impact_analysis\llm_cia\\repository_data\hsqldb",
            "JAMWiki" : "D:\science_research\change_impact_analysis\llm_cia\\repository_data\JAMWiki",
            "jEdit" : "D:\science_research\change_impact_analysis\llm_cia\\repository_data\jEdit",
            "JHotDraw" : "D:\science_research\change_impact_analysis\llm_cia\\repository_data\JHotDraw",
            "Makagiga" : "D:\science_research\change_impact_analysis\llm_cia\\repository_data\Makagiga",
            "OmegaT" : "D:\science_research\change_impact_analysis\llm_cia\\repository_data\OmegaT"
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
        project_defined_classes = call_graph.match_project_classes(self._project2root[self._project_name], imports,
                                                                   self._java_files)
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

    ## Meta Functions
    @property
    def function_descriptions(self):
        return self.__class__.FUNCTION_DESCRIPTIONS

    @property
    def fname2func(self):
        fname2func = {
            "get_coupling_dependencies": self.get_coupling_dependencies,
            "get_co_change_relationship": self.get_co_change_relationship,
            "get_conceptual_coupling": self.get_conceptual_coupling,
            "get_call_graph": self.get_call_graph,
            "get_origin_code": self.get_origin_code,
        }
        assert len(self.function_descriptions) == len(fname2func)
        return fname2func