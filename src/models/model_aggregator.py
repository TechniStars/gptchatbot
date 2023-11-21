import glob
import os.path
import pathlib

from src.config.config import CONFIG
from src.data.document import Document
from src.models.paragraph_search import ParagraphSearch
from src.models.semantic_search_engine import SemanticSearchEngine
from src.models.stemmed_semantic_search import StemmedSemanticSearch
from src.utils.chatgpt.token_check import token_check, get_text_from_files, get_token_count, limit_text_to_token_limit
from src.utils.solution_utils import get_project_root
from src.utils.statistics.statisic_helpers import scale_model_similarity, is_question_valid
from src.utils.summary_utils import get_summary_from_filepath


class ModelAggregator:
    def __init__(self):
        self.model1 = StemmedSemanticSearch()
        self.model2 = SemanticSearchEngine()
        self.model2.load_model()

    def return_top_files(self, question: str):
        top_files_model1 = self.model1.return_top_files(question)
        top_files_model2 = self.model2.return_top_files(question)

        if top_files_model1 and top_files_model2:
            # Threshold of valid question
            if is_question_valid(top_files_model1[0][0], model_number=1) or is_question_valid(top_files_model2[0][0],
                                                                                              model_number=2):
                top_files_model1 = [(scale_model_similarity(file[0], model_number=1), file[1]) for file in
                                    top_files_model1]
                top_files_model2 = [(scale_model_similarity(file[0], model_number=2), file[1]) for file in
                                    top_files_model2]
                all_top_files = top_files_model1 + top_files_model2
                all_top_files = sorted(all_top_files, key=lambda x: x[0], reverse=True)

                file_names = []
                for _, filename in all_top_files:
                    if filename not in file_names:
                        file_names.append(filename)
                return file_names[:CONFIG['global_config']['GPT_model']['max_different_files']]

    def __filter_paragraphs(self, question: str, filenames):
        file_paths = glob.glob(str(pathlib.Path(get_project_root(), 'data/raw/*.*')))
        top_files_filepaths = [x for x in file_paths if os.path.basename(x) in filenames]
        if top_files_filepaths is None:
            return

        paragraphs = []
        documents = [Document(fpath) for fpath in top_files_filepaths]
        for doc in documents:
            paragraphs.extend([{'file_path': doc.file_path, 'content': paragraph} for paragraph in doc.paragraphs])

        paragraph_search_engine = ParagraphSearch()
        paragraph_search_engine.load_paragraphs(paragraphs)
        return paragraph_search_engine.return_top_paragraphs(question)

    def get_best_paragraphs(self, question):
        top_files = self.return_top_files(question)
        if not top_files:
            return

        return self.__filter_paragraphs(question, top_files)

    def get_source_text(self, question):
        # Get top files
        file_paths = glob.glob(str(pathlib.Path(get_project_root(), 'data/raw/*.*')))
        top_files_filenames = self.return_top_files(question)

        if not top_files_filenames:
            return ""

        # Check if top files are shorter than token length limit
        top_files_paths = [x for x in file_paths if os.path.basename(x) in top_files_filenames]
        text = get_text_from_files(top_files_paths)

        # If top files are short enough or forced in CONFIG, return it as source
        if token_check(text) or CONFIG['chatgpt_config']['system_prompt']['prevent_fake_urls_in_response']:
            return limit_text_to_token_limit(text)

        # If top files are too long, get paragraphs
        top_paragraphs = self.__filter_paragraphs(question, top_files_filenames)
        if not top_paragraphs:
            return ""

        token_counter = 0
        paragraphs_by_files = {}

        for score, paragraph in top_paragraphs:

            # Check if summary already exists
            if paragraph['file_path'] not in paragraphs_by_files:
                summary = get_summary_from_filepath(os.path.basename(paragraph['file_path']))
                token_counter += get_token_count(summary)

                # Check if summary isn't too long to add
                if token_counter > CONFIG['global_config']['GPT_model']['upper_token_limit_docs']:
                    break

                paragraphs_by_files[paragraph['file_path']] = {}
                paragraphs_by_files[paragraph['file_path']]['paragraphs'] = []
                paragraphs_by_files[paragraph['file_path']]['summary'] = summary

            # Check if paragraph isn't too long to add
            token_counter += get_token_count(paragraph['content'])
            if token_counter > CONFIG['global_config']['GPT_model']['upper_token_limit_docs']:
                break
            else:
                paragraphs_by_files[paragraph['file_path']]['paragraphs'].append(paragraph['content'])

        text = ""
        for filepath in paragraphs_by_files:
            filename = os.path.basename(filepath)
            text += f"<#Filename>{filename}</Filename>\n"
            text += f"<#File text summary>{paragraphs_by_files[filepath]['summary']}</File text summary>\n"
            for paragraph in paragraphs_by_files[filepath]['paragraphs']:
                text += f"<#Paragraph>{paragraph}</Paragraph>\n"
        return text


if __name__ == '__main__':
    model = ModelAggregator()
    print(model.get_source_text("what does your product do?"))
