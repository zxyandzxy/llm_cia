import json
import time
import argparse
import hashlib
from copy import deepcopy
from lib.Qwen_plus import llm_utils, pro_interface

Qwen_RESULT_DIR = 'D:\science_research\change_impact_analysis\llm_cia\\results\Qwen_RESULTS'

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
        user_message += f'\nBased on human experience in conducting CIA work, the results of the co-change are very significant. So start by calling the `{self._pi._initial_code_getter}` function to get the results of the co-change.'

        self._append_to_messages({
            'role': 'user',
            'content': user_message,
        })

        first_respose = self.get_response(self.messages)
        assistant_output = first_respose['choices'][0]['message']
        if assistant_output['content'] is None:
            assistant_output['content'] = ""
        self._append_to_messages(assistant_output)
        # If there is no need to call the tool, the final answer is returned directly
        if assistant_output['tool_calls'] == None:
            print(f"No tools to call, direct response：{assistant_output['content']} ")
            return
        else:
            arug = '{\n  \"entity\": \"'
            arug += self._pi._coreclass
            arug += '\"\n}'
            tool_info = {"name": self._pi._initial_code_getter, "role": "tool"}
            tool_info['content'] = json.dumps(self._pi.fname2func[self._pi._initial_code_getter](self._pi._coreclass))
            self._append_to_messages(tool_info)

    def call_function(self, response_message):
        function_name = response_message['tool_calls'][0]['function']['name']
        function_to_call = self._pi.fname2func[function_name]
        function_args = json.loads(response_message['tool_calls'][0]['function']['arguments'])
        function_response = function_to_call(**function_args)
        return function_name, function_response

    def step(self, function_call_mode="none"):
        if function_call_mode == "none":
            user_message = "The result of the function get_co_change_relationship should be included in its entirety as your answer. As for the ordering of each entity you need to decide for yourself based on your analysis. This is the last conversation where you have to give an answer in the form of the example(The elements in the Change set are sorted in descending order of the likelihood of synchronized modifications):" \
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
                user_message = "The result of the function get_co_change_relationship should be included in its entirety as your answer. As for the ordering of each entity you need to decide for yourself based on your analysis. This is the last conversation where you have to give an answer in the form of the example(The elements in the Change set are sorted in descending order of the likelihood of synchronized modifications):" \
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model', default='qwen-coder-plus')
    parser.add_argument('-n', '--commit_num')
    parser.add_argument('-o', '--out', default='test.json')
    parser.add_argument('-p', '--prompt', default='./prompts/system_msg.txt')
    parser.add_argument('-j', '--project_name')
    args = parser.parse_args()

    ad = AutoCIA(args.model, args.prompt, args.project_name, args.commit_num)

    try:
        ad.run(7)
    except Exception as e:
        raise e

    with open(args.out, "w") as f:
        json.dump({
            'time': time.time(),
            'messages': ad.messages,
            'interaction_records': {
                "step_histories": ad._interaction_records,
                "mid_to_message": ad._message_map
            },
        }, f, indent=4)