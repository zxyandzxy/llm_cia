import json
import time
import random
import hashlib
from copy import deepcopy
import os
import subprocess

from lib.Ablation.ablate_func2 import llm_utils, pro_interface

Qwen_RESULT_DIR = 'D:\science_research\change_impact_analysis\llm_cia\Ablation_Results\\func2'

class AutoCIA(llm_utils.OpenAIEngine):
    def __init__(self, model_type, system_file, project_name, commit_num):
        super().__init__(model_type)
        self._system_file = system_file
        self._project_name = project_name
        self._commit_num = commit_num
        self._pi = pro_interface.repositoryInterface(project_name, commit_num)

    def _append_to_messages(self, message):
        self.messages.append(message)

    @property
    def _system_message(self):
        with open(self._system_file, encoding='utf-8') as f:
            system_message = f.read().strip()
        return system_message

    def _init_interaction_records(self):
        self._mid_map = {}  # md5_hash -> mid (message id)
        self._message_map = {}  # mid -> message
        self._interaction_records = []  # list of dict

    def _append_to_interaction_records(self, prompt_messages, response_message):
        def _save_message_and_get_mid(message):
            s = json.dumps(message).encode('utf-8')
            md5_hash = hashlib.md5(s).digest()
            if md5_hash not in self._mid_map:
                self._mid_map[md5_hash] = f"m{len(self._mid_map) + 1}"
                self._message_map[self._mid_map[md5_hash]] = deepcopy(message)
            return self._mid_map[md5_hash]

        self._interaction_records.append({
            "prompt_messages": [_save_message_and_get_mid(m) for m in prompt_messages],
            "response_message": _save_message_and_get_mid(response_message)
        })

    def startup(self):
        self._init_interaction_records()
        self.messages = []
        self._append_to_messages({'role': 'system', 'content': self._system_message})
        user_message = f'The project you need to analyze is `{self._project_name}`, a well-known Java open source project. The starting entity you need to deal with is {self._pi._coreclass}.java.'

        self._append_to_messages({
            'role': 'user',
            'content': user_message,
        })

        first_respose = self.get_response(self.messages)
        assistant_output = first_respose['choices'][0]['message']
        if assistant_output['content'] is None:
            assistant_output['content'] = ""
        self._append_to_interaction_records(user_message, assistant_output)
        self._append_to_messages(assistant_output)
        # Checks whether a function call is required
        if assistant_output['tool_calls'] != None:
            # call the function
            try:  # Note: the JSON response may not always be valid; be sure to handle errors
                function_name, function_response = self.call_function(assistant_output)
            except Exception as e:
                raise e
                return False  # drop erroneous response and retry if step budget left
            # send the info on the function call and function response to Qwen
            function_message = {
                "role": "tool",
                "name": function_name,
                "content": json.dumps(function_response),
            }
            self._append_to_messages(function_message)

    def call_function(self, response_message):
        function_name = response_message['tool_calls'][0]['function']['name']
        function_to_call = self._pi.fname2func[function_name]
        function_args = json.loads(response_message['tool_calls'][0]['function']['arguments'])
        function_response = function_to_call(**function_args)
        return function_name, function_response

    def step(self, function_call_mode="none"):
        if function_call_mode == "none":
            user_message = "This is the final round of conversation, and you need to give your answers strictly in the form of the example , without any other extra text (the elements in the Change set should be sorted in descending order of the likelihood of needing synchronous modification). Please note that in order to ensure recall, you need to give as many entities as possible (preferably more than 40) that need to be modified synchronously based on your analysis. An example of the answer is given below:" \
                           "Title: Diagnosis of starting entity `DatabaseURL`" \
                           "Change set: [ServerConstants, jdbcDriver]" \
                           "Details: Explain why each entity in your given change set needs to synchronize changes"
            self._append_to_messages({
                'role': 'user',
                'content': user_message,
            })
        prompt_messages = self.messages

        response = self.get_response(prompt_messages)
        response_message = response["choices"][0]["message"]
        self._append_to_interaction_records(prompt_messages, response_message)

        # Checks whether a function call is required
        if response_message['tool_calls'] != None:
            # call the function
            try:  # Note: the JSON response may not always be valid; be sure to handle errors
                function_name, function_response = self.call_function(response_message)
            except Exception as e:
                raise e
                return False  # drop erroneous response and retry if step budget left

            self._append_to_messages(response_message)  # extend conversation with assistant's reply
            # send the info on the function call and function response to Qwen
            function_message = {
                "role": "tool",
                "name": function_name,
                "content": json.dumps(function_response),
            }
            self._append_to_messages(function_message)
            return False  # not done
        else:
            self._append_to_messages(response_message)  # extend conversation with assistant's reply
            if function_call_mode == "auto":
                user_message = "This is the final round of conversation, and you need to give your answers strictly in the form of the example, without any other extra text (the elements in the Change set should be sorted in descending order of the likelihood of needing synchronous modification). Please note that in order to ensure recall, you need to give as many entities as possible (preferably more than 40) that need to be modified synchronously based on your analysis. An example of the answer is given below:" \
                               "Title: Diagnosis of starting entity `DatabaseURL`" \
                               "Change set: [ServerConstants, jdbcDriver]" \
                               "Details: Explain why each entity in your given change set needs to synchronize changes"
                self._append_to_messages({
                    'role': 'user',
                    'content': user_message,
                })
                prompt_messages = self.messages

                response = self.get_response(prompt_messages)
                response_message = response["choices"][0]["message"]
                self._append_to_interaction_records(prompt_messages, response_message)
                self._append_to_messages(response_message)
            return True

    def run(self, budget=7):
        self.startup()
        for i in range(budget):
            if i == budget - 1:
                function_call_mode = "none"
            else:
                function_call_mode = "auto"
            done = self.step(function_call_mode)
            time.sleep(0.1)
            if done:
                break

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
    svn_update_to_revision(commit_num, project2root[project_name])
    ad = AutoCIA(model, './prompts/system_msg.txt', project_name, commit_num)
    start = time.perf_counter()
    try:
        ad.run()
    except Exception as e:
        raise e
    end = time.perf_counter()

    cost_time_path = os.path.join("D:\science_research\change_impact_analysis\llm_cia\Ablation_Results", "func2", "LLM_CIA_COST", f"{project_name}.txt")

    with open(cost_time_path, 'a', encoding='utf-8') as file:
        file.write(f"{commit_num} : {end - start:.5f} s\n")
    file_path = os.path.join(Qwen_RESULT_DIR, "func2", project_name, str(commit_num) + '.json')
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
        commit_file_path = os.path.join("D:\science_research\change_impact_analysis\llm_cia\\ablate_commit",
                                        f"{project_name}.txt")
        with open(commit_file_path, 'r', encoding='utf-8') as file:
            commits = file.readlines()
            commits = [x.replace("\n", "") for x in commits]
            sample_list = commits

        sample_list = sorted(sample_list, key=int, reverse=True)
        for i in sample_list:
            output_path = os.path.join(Qwen_RESULT_DIR, project_name, f"{str(i)}.json")
            if os.path.exists(output_path):
                continue
            getQwenResult("qwen-plus-latest", project_name, i)