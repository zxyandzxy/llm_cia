import os

# Searches recursively for the specified filename in the given root directory, returning only the first match.
def find_first_file(project_name, filename):
    project2root = {
        "freecol": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\\freecol",
        "hsqldb": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\hsqldb",
        "JAMWiki": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\JAMWiki",
        "jEdit": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\jEdit",
        "JHotDraw": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\JHotDraw",
        "Makagiga": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\Makagiga",
        "OmegaT": "D:\science_research\change_impact_analysis\llm_cia\\repository_data\OmegaT"
    }
    for dirpath, _, filenames in os.walk(project2root[project_name]):
        if filename in filenames:
            return os.path.join(dirpath, filename)
    return None
