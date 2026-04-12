import logging

from util import file_reader
from service.git_service import GitService


class Extractor:
    def __init__(self, settings):
        self.settings = settings
        self.Git = GitService(settings.get("repo_dir", "./"))

    def get_documentation_context(self):
        """
        Obtiene el contexto del repositorio necesario para generar documentación:
        estructura del proyecto y metadatos de Git.
        """
        logging.debug("Getting project structure")
        project_structure = file_reader.get_project_structure(
            self.settings, self.settings.get("repo_dir", "./")
        )

        logging.debug("Getting git repo info")
        repo_info = self.Git.repo_info(self.settings)

        return project_structure, repo_info

    def get_release_notes_context(self):
        """
        Obtiene el contexto del repositorio necesario para generar release notes:
        metadatos de Git y diffs entre la rama actual y la base.
        """
        logging.debug("Getting repo info")
        repo_info = self.Git.repo_info(self.settings)

        logging.debug("Getting diffs")
        diffs = self.Git.get_diff(self.settings)

        return repo_info, diffs
