import logging
import sys

from util import settings
from orchestrator import Orchestrator


def main():
    json_settings = settings.load_settings()

    if json_settings.get("debug", False):
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    should_generate_rn = False
    if len(sys.argv) > 1:
        first_arg = sys.argv[1]
        should_generate_rn = first_arg in ("-r", "--release-notes")

    orchestrator = Orchestrator(json_settings)
    if should_generate_rn:
        orchestrator.generate_release_notes()
    else:
        orchestrator.generate_documentation()


if __name__ == "__main__":
    main()
