from GPT.autoCIA import AutoCIA as gpt_autoCIA
from GPT.autoCIA import GPT_RESULT_DIR
from Qwen_plus.autoCIA import AutoCIA as qwen_autoCIA
from Qwen_plus.autoCIA import Qwen_RESULT_DIR
import json
import time
import os
import subprocess


project2root = {
            "freecol": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\\freecol",
            "hsqldb": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\hsqldb",
            "JAMWiki": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\JAMWiki",
            "jEdit": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\jEdit",
            "JHotDraw": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\JHotDraw",
            "Makagiga": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\Makagiga",
            "OmegaT": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\OmegaT"
        }


# Iterate through all directories in your working copy and delete the .svn/lock file.
def remove_lock_files(repo_path):
    for root, dirs, files in os.walk(repo_path):
        svn_dir = os.path.join(root, '.svn')
        lock_file = os.path.join(svn_dir, 'lock')
        if os.path.exists(lock_file):
            print(f"Removing lock file at {lock_file}")
            os.remove(lock_file)

# Update the SVN repository under the specified path to the specified version
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

def getQwenResult(model, project_name, commit_num):

    # svn_update_to_revision(commit_num, project2root[project_name])
    ad = qwen_autoCIA(model, './Qwen_plus/prompts/system_msg.txt', project_name, commit_num)
    start = time.perf_counter()
    try:
        ad.run()
    except Exception as e:
        raise e
    end = time.perf_counter()
    cost_time_path = os.path.join("D:\science_research\change_impact_analysis\llm_cia\\results\LLM_CIA_Time", f"{project_name}.txt")
    with open(cost_time_path, 'a', encoding='utf-8') as file:
        file.write(f"{commit_num} : {end - start:.5f} s\n")
    file_path = os.path.join(Qwen_RESULT_DIR + '\\' + project_name, str(commit_num) + '.json')
    with open(file_path, "w") as f:
        json.dump({
            'time': time.time(),
            'messages': ad.messages,
            'interaction_records': {
                "step_histories": ad._interaction_records,
                "mid_to_message": ad._message_map
            },
        }, f, indent=4)
    print(f"has processed {commit_num}")

def getGPTResult(model ,project_name, commit_num):

    svn_update_to_revision(commit_num, project2root[project_name])
    ad = gpt_autoCIA(model, './GPT/prompts/system_msg.txt', project_name, commit_num)

    try:
        ad.run()
    except Exception as e:
        raise e

    file_path = os.path.join(GPT_RESULT_DIR + '\\' + project_name, str(commit_num) + '.json')

    with open(file_path, "w") as f:
        json.dump({
            'time': time.time(),
            'messages': ad.messages,
            'interaction_records': {
                "step_histories": ad._interaction_records,
                "mid_to_message": ad._message_map
            },
        }, f, indent=4)

    print(f"has processed {commit_num}")

def get_first_level_subfolders(directory):
    try:
        if not os.path.exists(directory) or not os.path.isdir(directory):
            print(f"The path {directory} does not exist or is not a directory.")
            return []

        return [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]

    except Exception as e:
        print(f"An error occurred: {e}")
        return []


if __name__ == '__main__':
    project = ["freecol", "hsqldb", "JAMWiki", "jEdit", "JHotDraw", "Makagiga", "OmegaT"]
    for project_name in project:
        out = get_first_level_subfolders("D:\science_research\change_impact_analysis\llm_cia\experiment_data\\" + project_name)
        out = sorted(out, key=int, reverse=True)
        for i in out:
            output_path = os.path.join(Qwen_RESULT_DIR, project_name, f"{str(i)}.json")
            if os.path.exists(output_path):
                continue
            getQwenResult("qwen-plus-latest", project_name, i)
            # getGPTResult("gpt-3.5-turbo", project_name, i)  # gpt-4o-mini  gpt-3.5-turbo  gpt-4-turbo

