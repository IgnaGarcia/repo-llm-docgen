import settings
import repo_reader


def main():
    # 1 load config file
    json_settings = settings.load_settings()
    print(json_settings)

    # 2 download repo (opt)
    path = json_settings["repo_dir"]

    # 3 read repo
    project_structure = repo_reader.get_project_structure(json_settings, path)
    print(project_structure)

    # 4 context retrieval

    # 5 should generate release notes?
    # 5.1 get git diff
    # 5.2 load info to llm
    # 5.4 load release notes template
    # 5.3 request release notes
    # 5.4 save release notes

    # 6 should update documentation?
    # 6.1 get actual documentation

    # 7 generate documentation
    # 7.1 load info to llm
    # 7.2 load template
    # 7.3 request new documentation
    # 7.4 save documentation
    print("main ok")


main()
