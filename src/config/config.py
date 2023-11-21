import pathlib

import yaml

from src.utils.singleton import singleton
from src.utils.solution_utils import get_project_root


@singleton
class Config:
    """
    Configuration class - singleton
    """

    def __init__(self, yamls_to_load: dict):
        """
        Loads yaml configuration files into Config instance.

        Parameters
        ----------
        yamls_to_load: dict
            Dict containing {'key': 'path'} items, for example {'telegram': 'path/to/telegram.yaml'}
        """
        self.data = {}
        for key, path in yamls_to_load.items():
            print(f'Loading config from {path}')
            with open(path) as file:
                self.data[key] = yaml.load(file, Loader=yaml.Loader)

    def __getitem__(self, item):
        """
        Returns a value under the key from config

        Parameters
        ----------
        item
            key to get value from config
        Returns
        -------
        Any
            Value under the key from config
        """
        return self.data[item]


CONFIG = Config({
    'telegram_config': str(pathlib.Path(get_project_root(), 'config', 'telegram_config.yaml')),
    'chatgpt_config': str(pathlib.Path(get_project_root(), 'config', 'chatgpt_config.yaml')),
    'global_config': str(pathlib.Path(get_project_root(), 'config', 'global_config.yaml')),
    'api_config': str(pathlib.Path(get_project_root(), 'config', 'api_config.yaml'))
})
