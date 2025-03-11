import os
from collections import Counter

from lib.func4 import call_graph
from lib import get_file_path, compute_score

project2root = {
        "freecol": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\\freecol",
        "hsqldb": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\hsqldb",
        "JAMWiki": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\JAMWiki",
        "jEdit": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\jEdit",
        "JHotDraw": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\JHotDraw",
        "Makagiga": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\Makagiga",
        "OmegaT": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\OmegaT"
    }

def get_co_change_relationship(entity, project_name):
    if (entity.endswith('.java')):
        entity = entity[:-5]
    relationships = []
    file_path = 'D:\science_research\change_impact_analysis\llm_cia\lib\\func2\\' + project_name + 'Result.txt'
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
                            relationships.append(impact_class.strip())
                    break

    except FileNotFoundError:
        print("Error: The file was not found. file_path = " + file_path + ", entity = " + entity)
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
    if len(relationships) == 0:
        return []
    return relationships

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

def Program1(parent_folder):
    project_name = parent_folder.split("\\")[-1]
    java_files = call_graph.collect_java_files(project2root[project_name])

    total_metrics = {k: {'precision_sum': 0, 'recall_sum': 0, 'f1_score_sum': 0, 'count': 0} for k in
                     (5, 10, 20, 30, 40)}

    with os.scandir(parent_folder) as entries:
        for entry in entries:
            if entry.is_dir():
                folder_path = entry.path
                commit_num = folder_path.split("\\")[-1]
                # print('-' * 100)
                # print("process: " + folder_path)

                ground_truth = []
                coreclass_txt_path = os.path.join(folder_path, 'coreclass.txt')
                if os.path.exists(coreclass_txt_path):
                    with open(coreclass_txt_path, 'r') as f:
                        lines = f.readlines()
                        coreclass = lines[0].split(":")[0]

                        for i in range(len(lines)):
                            if i == 0:
                                continue
                            ground_truth.append(lines[i].split(":")[0])

                coupling_path = os.path.join(
                    "D:\science_research\change_impact_analysis\llm_cia\coupling_dependency_result",
                    project_name, commit_num + "_" + coreclass + '.txt')
                if os.path.exists(coupling_path):
                    cp_result = get_coupling_result(coupling_path)
                else:
                    print(f"coupling_path not found in: {folder_path}")
                    print('#' * 100)
                    continue

                conceptual_path = os.path.join(
                     "D:\science_research\change_impact_analysis\llm_cia\conceptual_dependency_result",
                      project_name, f"{commit_num}_{coreclass}.txt")
                if os.path.exists(conceptual_path):
                    con_result = get_conceptual_result(conceptual_path)
                else:
                    print(f"conceptual_path not found in: {folder_path}")
                    print('#' * 100)
                    continue

                file_path1 = get_file_path.find_first_file(project_name=project_name,
                                                           filename=coreclass + '.java')

                if file_path1 is None:
                    continue

                func1_result = []
                func2_result = []
                func2_res = get_co_change_relationship(coreclass, project_name)
                func3_result = []
                func4_result = []
                imports = call_graph.parse_imports(file_path1)
                func4_res = call_graph.match_project_classes(project2root[project_name],
                                                             imports, java_files)

                change_set = []
                for tra in con_result:
                    support = 0

                    if tra in cp_result and cp_result[tra] is True:
                        support += 1
                        func1_result.append(tra)

                    if tra in func2_res:
                        support += 1
                        func2_result.append(tra)

                    if tra in con_result and con_result[tra] is True:
                        support += 1
                        func3_result.append(tra)

                    if tra in func4_res:
                        support += 1
                        func4_result.append(tra)

                    change_set.append({'tra_name': tra, 'support': support})

                sorted_change_set = sorted(change_set, key=lambda x: x['support'], reverse=True)

                tra_names = [item['tra_name'] for item in sorted_change_set]

                task_metrics = compute_score.calculate_metrics(ground_truth, tra_names)
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

def Program2(parent_folder):
    project_name = parent_folder.split("\\")[-1]
    java_files = call_graph.collect_java_files(project2root[project_name])

    total_metrics = {k: {'precision_sum': 0, 'recall_sum': 0, 'f1_score_sum': 0, 'count': 0} for k in
                     (5, 10, 20, 30, 40)}
    with os.scandir(parent_folder) as entries:
        for entry in entries:
            if entry.is_dir():
                folder_path = entry.path
                commit_num = folder_path.split("\\")[-1]
                # print('-' * 100)
                # print("process: " + folder_path)

                ground_truth = []
                coreclass_txt_path = os.path.join(folder_path, 'coreclass.txt')

                if os.path.exists(coreclass_txt_path):
                    with open(coreclass_txt_path, 'r') as f:
                        lines = f.readlines()
                        coreclass = lines[0].split(":")[0]

                        for i in range(len(lines)):
                            if i == 0:
                                continue
                            ground_truth.append(lines[i].split(":")[0])

                coupling_path = os.path.join(
                    "D:\science_research\change_impact_analysis\llm_cia\coupling_dependency_result",
                    project_name, commit_num + "_" + coreclass + '.txt')
                if os.path.exists(coupling_path):
                    cp_result = get_coupling_result(coupling_path)
                else:
                    print(f"tra_cia_txt not found in: {folder_path}")
                    print('#' * 100)
                    continue

                conceptual_path = os.path.join(
                    "D:\science_research\change_impact_analysis\llm_cia\conceptual_dependency_result",
                    project_name, f"{commit_num}_{coreclass}.txt")
                if os.path.exists(conceptual_path):
                    con_result = get_conceptual_result(conceptual_path)
                else:
                    print(f"conceptual_path not found in: {folder_path}")
                    print('#' * 100)
                    continue

                file_path1 = get_file_path.find_first_file(project_name=project_name,
                                                           filename=coreclass + '.java')

                if file_path1 is None:
                    continue

                func1_result = []
                func2_result = []
                func2_res = get_co_change_relationship(coreclass, project_name)
                func3_result = []
                func4_result = []
                imports = call_graph.parse_imports(file_path1)
                func4_res = call_graph.match_project_classes(project2root[project_name],
                                                             imports, java_files)

                for tra in con_result:
                    if tra in cp_result and cp_result[tra] is True:
                        func1_result.append(tra)

                    if tra in func2_res:
                        func2_result.append(tra)

                    if tra in con_result and con_result[tra] is True:
                        func3_result.append(tra)

                    if tra in func4_res:
                        func4_result.append(tra)

                # Merge the three arrays and count the number of occurrences of each tra_name
                combined = func1_result + func2_result + func3_result + func4_result
                counter = Counter(combined)

                func_result = [{'tra_name': tra_name, 'support': count} for tra_name, count in counter.items()]
                sorted_func_result_set = sorted(func_result, key=lambda x: x['support'], reverse=True)
                func_tra_names = [item['tra_name'] for item in sorted_func_result_set]

                task_metrics = compute_score.calculate_metrics(ground_truth, func_tra_names)
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

def RQ2_scheme(parent_folder):
    project_name = parent_folder.split("\\")[-1]
    java_files = call_graph.collect_java_files(project2root[project_name])

    total_metrics = {k: {'precision_sum': 0, 'recall_sum': 0, 'f1_score_sum': 0, 'count': 0} for k in
                     (5, 10, 20, 30, 40)}
    with os.scandir(parent_folder) as entries:
        for entry in entries:
            if entry.is_dir():
                folder_path = entry.path
                commit_num = folder_path.split("\\")[-1]
                # print('-' * 100)
                # print("process: " + folder_path)

                ground_truth = []
                coreclass_txt_path = os.path.join(folder_path, 'coreclass.txt')

                if os.path.exists(coreclass_txt_path):
                    with open(coreclass_txt_path, 'r') as f:
                        lines = f.readlines()
                        coreclass = lines[0].split(":")[0]

                        for i in range(len(lines)):
                            if i == 0:
                                continue
                            ground_truth.append(lines[i].split(":")[0])

                coupling_path = os.path.join(
                    "D:\science_research\change_impact_analysis\llm_cia\coupling_dependency_result",
                    project_name, commit_num + "_" + coreclass + '.txt')

                if os.path.exists(coupling_path):
                    cp_result = get_coupling_result(coupling_path)
                else:
                    print(f"coupling_path not found in: {folder_path}")
                    print('#' * 100)
                    continue

                conceptual_path = os.path.join(
                    "D:\science_research\change_impact_analysis\llm_cia\conceptual_dependency_result",
                    project_name, f"{commit_num}_{coreclass}.txt")
                if os.path.exists(conceptual_path):
                    con_result = get_conceptual_result(conceptual_path)
                else:
                    print(f"conceptual_path not found in: {folder_path}")
                    print('#' * 100)
                    continue

                file_path1 = get_file_path.find_first_file(project_name=project_name,
                                                           filename=coreclass + '.java')

                if file_path1 is None:
                    continue

                func1_result = []
                func2_res = get_co_change_relationship(coreclass, project_name)
                func3_result = []
                imports = call_graph.parse_imports(file_path1)
                func4_res = call_graph.match_project_classes(project2root[project_name],
                                                             imports, java_files)

                for tra in con_result:
                    if tra in cp_result and cp_result[tra] is True:
                        func1_result.append(tra)

                    if tra in con_result and con_result[tra] is True:
                        func3_result.append(tra)

                # Merge the three arrays and count the number of occurrences of each tra_name
                combined = func1_result + func2_res + func3_result + func4_res
                counter = Counter(combined)

                func_result = [{'tra_name': tra_name, 'support': count} for tra_name, count in counter.items()]
                sorted_func_result_set = sorted(func_result, key=lambda x: x['support'], reverse=True)
                func_tra_names = [item['tra_name'] for item in sorted_func_result_set]

                task_metrics = compute_score.calculate_metrics(ground_truth, func_tra_names)
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

if __name__ == "__main__":
    parent_folder = "D:\science_research\change_impact_analysis\llm_cia\experiment_data"
    project = ['freecol', 'hsqldb', 'JAMWiki', 'jEdit', 'JHotDraw', 'Makagiga', 'OmegaT']
    for project_name in project:
        path = os.path.join(parent_folder, project_name)
        print(project_name)
        print("--"*20)
        print("Program1")
        # Program1
        average_metrics = Program1(path)
        for k in average_metrics:
            print("k = " + str(k) + "-"*100)
            print("recall: " + "{:.4f}".format(average_metrics[k]["average_recall"]))
            print("precision: " + "{:.4f}".format(average_metrics[k]["average_precision"]))

        print("Program2")
        # Program2
        average_metrics = Program2(path)
        for k in average_metrics:
            print("k = " + str(k) + "-" * 100)
            print("recall: " + "{:.4f}".format(average_metrics[k]["average_recall"]))
            print("precision: " + "{:.4f}".format(average_metrics[k]["average_precision"]))

        print("RQ2_scheme")
        # RQ2_scheme
        average_metrics = RQ2_scheme(path)
        for k in average_metrics:
            print("k = " + str(k) + "-" * 100)
            print("recall: " + "{:.4f}".format(average_metrics[k]["average_recall"]))
            print("precision: " + "{:.4f}".format(average_metrics[k]["average_precision"]))

