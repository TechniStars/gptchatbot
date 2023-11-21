import os
from pathlib import Path


def get_project_root():
    """
    Returns the path to the project's root directory.
    """
    return str(Path(os.path.dirname(os.path.abspath(__file__)).split('qa-chatbot-synerise')[0], 'qa-chatbot-synerise'))
