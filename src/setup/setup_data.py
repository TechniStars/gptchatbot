import json
import os

from src.utils.solution_utils import get_project_root

os.chdir(get_project_root())

from src.setup import configure_model_thresholds, generate_qa, generate_summaries
from src.models.semantic_search_engine import SemanticSearchEngine


setup_status_path = 'setup_status.json'


def setup_data():
    # Prepare data
    if not get_setup_status_of_job('generate_qa'):
        print('Generating QA examples...')
        generate_qa.main()
        set_setup_status_as_done('generate_qa')

    if not get_setup_status_of_job('generate_summaries'):
        print('Generating File summaries...')
        generate_summaries.main()
        set_setup_status_as_done('generate_summaries')

    # Train model SemanticSearchEngine
    if not get_setup_status_of_job('docs_search_engine'):
        print('Configuring search engine...')
        docs_search_engine = SemanticSearchEngine()
        docs_search_engine.train_model()
        docs_search_engine.save_model()
        set_setup_status_as_done('docs_search_engine')

    # Configure thresholds
    if not get_setup_status_of_job('configure_model_thresholds'):
        print('Configuring model thresholds...')
        configure_model_thresholds.find_thresholds_and_save_config()
        set_setup_status_as_done('configure_model_thresholds')

    print('Setup completed')


def get_setup_status():
    os.chdir(get_project_root())

    if not os.path.exists(setup_status_path):
        setup_status = {
            "generate_qa": False,
            "generate_summaries": False,
            "docs_search_engine": False,
            "configure_model_thresholds": False
        }

        with open(setup_status_path, 'w') as f:
            json.dump(setup_status, f)

    with open(setup_status_path, 'r') as f:
        return json.load(f)


def get_setup_status_of_job(key: str):
    setup_status = get_setup_status()
    if key not in setup_status:
        raise KeyError(f'{key} not in setup_status file in {setup_status_path}')

    return setup_status[key]


def set_setup_status_as_done(key: str):
    setup_status = get_setup_status()
    if key not in setup_status:
        raise KeyError(f'{key} not in setup_status file in {setup_status_path}')

    setup_status[key] = True
    with open(setup_status_path, 'w') as f:
        json.dump(setup_status, f)


if __name__ == '__main__':
    setup_data()
