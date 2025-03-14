## Overview

### Code Repository Structure

> Experimental intermediate data

```
llm_cia\
	co_change_coupling_dependency\
		freecol\
		hsqldb\
		...
	conceptual_dependency_result\
	coupling_dependency_result\
	experiment_data\
	repository_data\
```

In this experiment we choose seven open source Java projects for the performance evaluation of our method:`freecol hsqldb JAMWiki jEdit JHotDraw Makagiga OmegaT`. The above folders have sub-folders for each of the 7 projects. Under each of the above folders, there are subfolders for each of the seven projects that store the intermediate data for the corresponding project.

**repository_data :** All seven open source projects are version controlled via `SVN`, and we download the source code data of the open source projects to this folder via `SVN`.

**experiment_data :** This folder was obtained via the `GitHub` code repository `[CIABoosting/IntermediaryData-for-ChangePatternsMapping: Intermediary data for the TSE article 'Change-Patterns Mapping'](https://github.com/CIABoosting/IntermediaryData-for-ChangePatternsMapping)` obtained. In each `commit` for each project, there are 5 files:

- **coreclass.txt :** Shows the probability of an entity being a coreclass (starting entity), with the entity with the highest probability being the coreclass
- **ImpactminerResult :** Storage of the original affected entities generated by the `Impactminer` 
- **JripplesResult : ** Storage of the original affected entities generated by the `Jripples` tool
- **RoseResult :** Storage of the original affected entities generated by the `ROSE` tool

**coupling_dependency_result : **

- This folder stores the results of the `func1 : get_coupling_dependencies` runs we designed; specifically, for each `commit` in `experiment_data`, we perform the `coreclass` and `Impactminer` result sets for each entity in the result set `get_coupling_dependencies` run and store the results.
- For example, `coupling_dependency_result\hsqldb\11_DatabaseManager.txt`, where the first line `DatabaseManagerCommon : ['There are no coupling dependencies between these two entities'`]` represents that there are no coupling dependencies between `DatabaseManager.java` and `DatabaseManagerCommon.java`. java` and `DatabaseManagerCommon.java` have no coupling dependencies between these two entities.

![image-20250114172332750](https://zxyandzxy.github.io/images/202501151106088.png)

**conceptual_dependency_result :**

- This folder stores the results of the `func3 : get_conceptual_coupling` runs we designed; specifically, for each `commit` in `experiment_data`, we perform a ` get_conceptual_coupling` operation and store the results.
-  As in `conceptual_dependency_result\jEdit\159_Handler.txt`, where the first line `XmlParser : 0.80684215` represents the conceptual coupling score between `Handler.java` and `XmlParser.java` is 0.80684215![image-20250114172405980](https://zxyandzxy.github.io/images/202501151106335.png)

**co_change_coupling_dependency : **This folder stores the coupling dependencies (calculated by `func1 : get_coupling_dependencies`) between the various entities after we have mined the version history. For example, `co_change_coupling_dependency\JAMWiki\AdminServlet.txt`, where the first line `DatabaseConnection : ['There are no coupling dependencies between these two entities']` represents that there are no coupling dependencies between `AdminServlet.java` and `DatabaseConnection.java`.

![image-20250114172820024](https://zxyandzxy.github.io/images/202501151106878.png)

> Function Implementation and large language model Interaction Code

```
llm_cia\
	  lib\
		func1\
		func2\
		...
		GPT\
		Qwen_plus\
			prompts\system_msg.txt
			autoCIA.py
			llm_util.py
			pro_interface.py
		autoCIA.py
		compute_score.py
		get_file_path.py
	results\
		Qwen_RESULTS\
			freecol\
			hsqldb\
			...
		...
	RQ2.py
	generate_co_change_coupling_dependency.py
	generate_conceptual_dependency_result.py
	generate_coupling_dependency_result.py
	generate_ground_truth_conceptual_analysis_result.py
	generate_ground_truth_coupling_analysis_result.py
```

- The `func1 func2 func3 func4 func5` under `lib` is the specific code for the 5 functions we designed and implemented
- `GPT` and `Qwen_plus` are concrete implementation logics for the interaction between `LLM` and local functions
- `autoCIA.py` is the entry file through which the process of interaction between `LLM` and the local functions is initiated for CIA tasks
- `compute_score.py` is the file for the calculation of performance metrics, which evaluates the performance of the method through precision and recall
- `get_file_path.py` is the utility function to find the path to the source code file of an entity
- `results` stores `LLM` interactions with local functions
- `RQ2 is the code for the three experimental programs in RQ2`
- `generate_co_change_coupling_dependency.py`is the code that generates the `co_change_coupling_dependency`folder
- `generate_conceptual_dependency_result.py`is the code that generates the`conceptual_dependency_result`folder
- `generate_coupling_dependency_result.py`is the code that generates the`coupling_dependency_result`folder
- `generate_ground_truth_conceptual_analysis_result.py` is the code that generates the`ground_truth_conceptual_analysis`folder
- `generate_ground_truth_conpling_analysis_result.py` is the code that generates the`ground_truth_coupling_analysis`folder`

> special reminder

- When you want to use our code, you first need to download the `graphcodebert model` at  [microsoft/graphcodebert-base at main](https://huggingface.co/microsoft/graphcodebert-base/tree/main) and put it in the `lib\func3\microsoft` folder.
- You need to download the open source project via `SVN` and put it in repository_data folder.

