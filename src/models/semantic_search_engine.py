import glob
import os
import shutil
from pathlib import Path

from haystack.document_stores.faiss import FAISSDocumentStore
from haystack.nodes import EmbeddingRetriever
from haystack.pipelines import DocumentSearchPipeline
from haystack.utils import convert_files_to_docs

from src.data.document import Document
from src.utils.solution_utils import get_project_root


class SemanticSearchEngine:
    def __init__(self, docs_md_dir="data/raw", docs_txt_dir="data/raw_txt", top_k_results=5,
                 embedding_model='sentence-transformers/multi-qa-mpnet-base-dot-v1', use_gpu=True):
        self.docs_md_dir = docs_md_dir
        self.docs_txt_dir = docs_txt_dir
        self.top_k_results = top_k_results
        self.embedding_model = embedding_model
        self.use_gpu = use_gpu
        self.all_docs = None
        self.document_store = None
        self.documents = []
        self.retriever = None
        self.semantic_search_pipeline = None
        self.save_dir_path = str(Path(get_project_root(), "saved_models", "semantic_search_engine"))
        self.document_store_path = "saved_models/semantic_search_engine/document_store"
        self.retriever_path = "saved_models/semantic_search_engine/retriever"
        self.sql_url = "sqlite:///saved_models/semantic_search_engine/haystack_docs_faiss.db"

    def prepare_data(self):
        os.makedirs(self.docs_md_dir, exist_ok=True)
        os.makedirs(self.docs_txt_dir, exist_ok=True)
        os.makedirs(self.save_dir_path, exist_ok=True)

        for filepath in glob.glob(self.docs_md_dir + "/*.*"):
            try:
                document = Document(filepath)
                self.documents.append(document)
            except ValueError:
                continue

            new_filename = os.path.basename(filepath).rsplit('.', 1)[0] + ".txt"
            with open(self.docs_txt_dir + "/" + new_filename, "w", encoding="utf-8") as file:
                file.write(document.plain_text_content)

        self.all_docs = convert_files_to_docs(dir_path=self.docs_txt_dir, split_paragraphs=True)

    def build_index(self):
        self.document_store = FAISSDocumentStore(faiss_index_factory_str="Flat", similarity="cosine",
                                                 sql_url=self.sql_url)
        self.document_store.write_documents(self.all_docs, batch_size=100)

        self.retriever = EmbeddingRetriever(document_store=self.document_store, use_gpu=self.use_gpu,
                                            embedding_model=self.embedding_model, top_k=self.top_k_results)
        self.document_store.update_embeddings(self.retriever, batch_size=100)

    def _remove_db_files_for_training(self):
        shutil.rmtree(self.docs_txt_dir, ignore_errors=True)
        shutil.rmtree(self.save_dir_path, ignore_errors=True)
        try:
            os.remove(self.sql_url.split('///')[1])
        except OSError:
            pass
        self.prepare_data()

    def train_model(self):
        self._remove_db_files_for_training()
        self.build_index()
        self.initialize_search_pipeline()

    def save_model(self):
        self.retriever.save(self.retriever_path)
        self.document_store.save(self.document_store_path)

    def load_model(self):
        self.document_store = FAISSDocumentStore(faiss_index_path=self.document_store_path)
        self.retriever = EmbeddingRetriever(embedding_model=self.retriever_path, document_store=self.document_store)
        self.semantic_search_pipeline = DocumentSearchPipeline(retriever=self.retriever)
        self.prepare_data()

    def initialize_search_pipeline(self):
        self.semantic_search_pipeline = DocumentSearchPipeline(retriever=self.retriever)

    def search_document(self, id):
        for doc in self.all_docs:
            if doc.id == id:
                return doc.meta['name']

    def search(self, question):
        prediction = self.semantic_search_pipeline.run(query=question)
        for pred in prediction['documents']:
            print("File:", self.search_document(pred.id))
            print("Score:", pred.score)
            print("Content:", pred.content)
            print("\n" * 5)

    def _get_document_by_filename(self, filename: str):
        filename = os.path.splitext(filename)[0]
        for document in self.documents:
            if os.path.splitext(document.filename)[0] == filename:
                return document

    def return_top_files(self, question, num_files=3):
        prediction = self.semantic_search_pipeline.run(query=question)

        filenames = []
        filenames_short_content = []

        for pred in prediction['documents']:
            content = pred.content.strip()
            original_document = self._get_document_by_filename(self.search_document(pred.id))
            original_source_name = original_document.filename
            score = pred.score

            if " " not in content or len(content.split(" ")) < 5:
                filenames_short_content.append((score, original_source_name))
            else:
                filenames.append((score, original_source_name))

        filenames.sort(reverse=True, key=lambda x: x[0])
        filenames += filenames_short_content[:num_files - len(filenames)]

        return filenames[:num_files]


if __name__ == '__main__':
    search_engine = SemanticSearchEngine()

    search_engine.train_model()

    # Save models
    search_engine.save_model()

    # Load models
    search_engine = SemanticSearchEngine()
    search_engine.load_model()

    # Perform search
    search_engine.search("Example question?")

    # Return top files
    top_files = search_engine.return_top_files("your search question", num_files=3)
    print("Top files:", top_files)
