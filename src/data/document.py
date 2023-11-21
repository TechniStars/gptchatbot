import os.path

from src.config.config import CONFIG
from src.utils.summary_utils import get_summary_from_filepath
from src.utils.text_utils import md_to_plaintext, split_string_by_regex, html_to_plaintext


class Document:

    def __init__(self, file_path):
        self.file_path = file_path
        self.filename = os.path.basename(file_path)
        self.ext = os.path.splitext(file_path)[1].replace('.', '')
        self.supported_extensions = list(CONFIG['global_config']['documentation_source_files']['paragraph_split_regex'].keys())
        self.content = None
        self.read()

    def read(self):
        if self.ext not in self.supported_extensions:
            raise ValueError(f"Unsupported file extension: {self.ext}")

        file = open(self.file_path, 'r', encoding='utf-8')
        self.content = file.read()
        file.close()

    @property
    def summary(self):
        return get_summary_from_filepath(self.file_path)

    @property
    def paragraphs(self):
        regex = CONFIG['global_config']['documentation_source_files']['paragraph_split_regex'][self.ext]
        return split_string_by_regex(self.content, regex, plaintext_func=self.__get_plain_text_function(self.ext))

    @property
    def plain_text_content(self, convert_func=None):
        if not convert_func:
            convert_func = self.__get_plain_text_function(self.ext)
        return convert_func(self.content)

    def __get_plain_text_function(self, ext):
        functions = {
            'md': md_to_plaintext,
            'html': html_to_plaintext
        }

        return functions.get(ext.replace(".", ""), lambda x: x)
