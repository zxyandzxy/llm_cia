import os
import json
from lib.func4 import call_graph
from lib import get_file_path


project2root = {
        "freecol": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\\freecol",
        "hsqldb": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\hsqldb",
        "JAMWiki": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\JAMWiki",
        "jEdit": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\jEdit",
        "JHotDraw": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\JHotDraw",
        "Makagiga": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\Makagiga",
        "OmegaT": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\OmegaT"
    }

# Calculate Precision, Recall and F1-score for a given ground truth and result for different k values.
def calculate_metrics(ground_truth, result, k_values=(5, 10, 20, 30, 40)):
    gt_set = set(ground_truth)
    metrics_results = {}

    for k in k_values:
        top_k_result = result[:min(k, len(result))]
        tp = sum(1 for item in top_k_result if item in gt_set)

        precision = tp / len(top_k_result) if top_k_result else 0
        recall = tp / len(gt_set) if gt_set else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        metrics_results[k] = {
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score
        }

    return metrics_results

# Evaluates multiple tasks and calculates average Precision, Recall and F1-score for all tasks
def evaluate_all_tasks(tasks):
    total_metrics = {k: {'precision_sum': 0, 'recall_sum': 0, 'f1_score_sum': 0, 'count': 0} for k in
                     (5, 10, 20, 30, 40)}

    for ground_truth, result in tasks:
        task_metrics = calculate_metrics(ground_truth, result)

        for k, metrics in task_metrics.items():
            total_metrics[k]['precision_sum'] += metrics['precision']
            total_metrics[k]['recall_sum'] += metrics['recall']
            total_metrics[k]['f1_score_sum'] += metrics['f1_score']
            total_metrics[k]['count'] += 1

    average_metrics = {k: {
        'average_precision': metrics['precision_sum'] / metrics['count'] if metrics['count'] > 0 else 0,
        'average_recall': metrics['recall_sum'] / metrics['count'] if metrics['count'] > 0 else 0,
        'average_f1_score': metrics['f1_score_sum'] / metrics['count'] if metrics['count'] > 0 else 0
    } for k, metrics in total_metrics.items()}

    return average_metrics

#  Get the ground truth for the specified project and submission number.
def get_ground_truth(project_name, commit_num):
    base_path = "D:\science_research\change_impact_analysis\llm_cia\experiment_data"
    folder_path = os.path.join(base_path, project_name, commit_num)
    file_path = os.path.join(folder_path, 'coreclass.txt')

    ground_truth = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines[1:]:
                parts = line.strip().split(':')
                if len(parts) == 2:
                    entity_name = parts[0]
                    ground_truth.append(entity_name)
                else:
                    print(f"Warning: Invalid line format in {file_path}: {line}")
    except Exception as e:
        print(f"An error occurred while reading {file_path}: {e}")
        raise

    return ground_truth

# Extracts the Change set array from the given text, using simple string handling.
def extract_change_set(text):
    start_index = text.find("Change set:")
    if start_index == -1:
        print("Error: Change set information not found")
        return None

    start_index += len("Change set:")
    text_from_start = text[start_index:].strip()

    left_bracket_index = text_from_start.find('[')
    if left_bracket_index == -1:
        print("Error: left square bracket '[' not found")
        return None

    right_bracket_index = text_from_start.find(']')
    if right_bracket_index == -1 or right_bracket_index < left_bracket_index:
        print("Error: right square bracket ']' not found or square bracket mismatch")
        return None

    result = []
    change_set_str = text_from_start[left_bracket_index:right_bracket_index + 1]

    change_set_str_arr = change_set_str.split(",")
    for s in change_set_str_arr:
        s = str(s)
        s = s.strip().replace('[', '')
        s = s.strip().replace(']', '')
        s = s.strip().replace('.java', '')
        result.append(s)
    return result

def get_result_from_Json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        final_response = data.get('messages')[-1]['content']
        if "Change set:" in final_response:
            parsed_change_set = extract_change_set(final_response)
            if parsed_change_set is None:
                print(file_path)
            if parsed_change_set[0] == 'None identified':
                parsed_change_set = []
            if '...' in parsed_change_set:
                print(file_path)
            if parsed_change_set == "None":
                print(file_path)
            return parsed_change_set
    return None

def get_co_change_relationship(entity, project_name):
    if (entity.endswith('.java')):
        entity = entity[:-5]
    relationships = []
    file_path = os.path.join("D:\science_research\change_impact_analysis\llm_cia\lib\\func2",
                             project_name + 'Result.txt')
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
                            confidence = float(cur[2].replace(')', '').strip())
                            relationships.append((impact_class.strip(), confidence))
                    break

    except FileNotFoundError:
        print("Error: The file was not found. file_path = " + file_path + ", entity = " + entity)
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
    if len(relationships) == 0:
        return []
    sorted_entities = sorted(relationships, key=lambda x: x[1], reverse=True)
    sorted_entity_names = [entity[0] for entity in sorted_entities]
    return sorted_entity_names

def supplement_co_change(project_name, commit_num, result):
    coreclass_path = os.path.join("D:\science_research\change_impact_analysis\llm_cia\experiment_data",
                                  project_name, str(commit_num), "coreclass.txt")
    with open(coreclass_path, 'r') as f:
        lines = f.readlines()
        entity = lines[0].split(":")[0].strip()
    co_change_result = get_co_change_relationship(entity, project_name)
    for co_change_entity in co_change_result:
        if co_change_entity in result:
            continue
        result.append(co_change_entity)
    return result

def get_coupling_result(file_path):
    result = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split(':', 1)
                if len(parts) != 2:
                    continue  #

                coreclass, array_str = parts[0].strip(), parts[1].strip()

                try:
                    target_substrings = [
                        "There are no coupling dependencies between these two entities",
                        "is not exist in project code"
                    ]

                    flag = True
                    for substring in target_substrings:
                        if substring in array_str:
                            result[coreclass] = False
                            flag = False
                    if flag is True:
                        result[coreclass] = True

                except (ValueError, SyntaxError):
                    print(array_str + "cannot be parsed, its coreclass is" + coreclass)
                    continue

    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

    return result

def get_conceptual_result(file_path):
    result = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split(':', 1)
                if len(parts) != 2:
                    continue  #

                coreclass, average_similarity = parts[0].strip(), parts[1].strip()

                if "is not exist in project code" in average_similarity:
                    result[coreclass] = False
                elif float(average_similarity) > 0.8:
                    result[coreclass] = True
                else:
                    result[coreclass] = False
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

    return result

def supplement_vote(project_name, commit_num, result):
    java_files = call_graph.collect_java_files(project2root[project_name])
    coreclass_path = os.path.join("D:\science_research\change_impact_analysis\llm_cia\experiment_data",
                                  project_name, str(commit_num), "coreclass.txt")
    with open(coreclass_path, 'r') as f:
        lines = f.readlines()
        coreclass = lines[0].split(":")[0].strip()

        # Get coupling dependencies, conceptual coupling and call graph results based on coreclass
        coupling_path = os.path.join(
            "D:\science_research\change_impact_analysis\llm_cia\coupling_dependency_result",
            project_name, commit_num + "_" + coreclass + '.txt')
        if os.path.exists(coupling_path):
            cp_result = get_coupling_result(coupling_path)
        else:
            print(f"coupling_path not found in: {coupling_path}")
            print('#' * 100)

        conceptual_path = os.path.join(
            "D:\science_research\change_impact_analysis\llm_cia\conceptual_dependency_result",
            project_name, f"{commit_num}_{coreclass}.txt")
        if os.path.exists(conceptual_path):
            con_result = get_conceptual_result(conceptual_path)
        else:
            print(f"conceptual_path not found in: {conceptual_path}")
            print('#' * 100)

        file_path1 = get_file_path.find_first_file(project_name=project_name,
                                                   filename=coreclass + '.java')
        if file_path1 is None:
            return supplement_co_change(project_name, commit_num, result)
        imports = call_graph.parse_imports(file_path1)
        call_graph_res = call_graph.match_project_classes(project2root[project_name],
                                                     imports, java_files)

        # Get voting results
        temp_result = get_co_change_relationship(coreclass, project_name)
        temp_zip_result = []
        for temp_entity in temp_result:
            vote = 0
            if temp_entity in cp_result and cp_result[temp_entity] is True:
                vote += 1
            if temp_entity in con_result and con_result[temp_entity] is True:
                vote += 1
            if temp_entity in call_graph_res:
                vote += 1
            temp_zip_result.append({'entity': temp_entity, 'vote': vote})
        sorted_temp_zip_result = sorted(
            temp_zip_result,
            key=lambda x: (-x['vote'], temp_result.index(x['entity']))
        )

        # Extracts the sorted entity fields into a final string array
        final_result = [item['entity'] for item in sorted_temp_zip_result]
        for final_entity in final_result:
            if final_entity in result:
                continue
            result.append(final_entity)
        return result

def get_project_task(parent_folder):
    project_name = parent_folder.split("\\")[-1]
    tasks = []
    with os.scandir(parent_folder) as entries:
        for entry in entries:
            file_path = entry.path
            commit_num = file_path.split("\\")[-1].split('.')[0]
            result = get_result_from_Json(file_path)
            # result = supplement_co_change(project_name, commit_num, result)
            # result = supplement_vote(project_name, commit_num, result)

            ground_truth = get_ground_truth(project_name, commit_num)
            tasks.append((ground_truth, result))
    average_metrics = evaluate_all_tasks(tasks)
    print(f"{project_name}")
    for k in average_metrics:
        print("k = " + str(k) + "-"*100)
        print("recall: " + "{:.4f}".format(average_metrics[k]["average_recall"]))
        print("precision: " + "{:.4f}".format(average_metrics[k]["average_precision"]))
        print("f1-score: " + "{:.4f}".format(average_metrics[k]["average_f1_score"]))

def get_LLM_answerLen(parent_folder):
    result_len = []
    with os.scandir(parent_folder) as entries:
        for entry in entries:
            file_path = entry.path
            result = get_result_from_Json(file_path)
            result_len.append(len(result))
    return sum(result_len) / len(result_len)

# parent_folder = "D:\science_research\change_impact_analysis\llm_cia\\results\Qwen_K_RESULTS"
# project = ["freecol", "hsqldb", "JAMWiki", "jEdit", "JHotDraw", "Makagiga", "OmegaT"]
# for project_name in project:
#     get_project_task(os.path.join(parent_folder, project_name))
#     print('\n' * 2)
#     # l = get_LLM_answerLen(os.path.join(parent_folder, project_name))
#     # print(f"{project_name} : {l}")