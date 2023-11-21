import nltk

from src.data.document import Document

nltk.download('punkt')
nltk.download('stopwords')

from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import string
import os
import glob


@dataclass
class FileContents:
    filename: str = ""
    file_text: str = ""


class StemmedSemanticSearch:
    def __init__(self, folder_path='data/raw', n_best: int = 3):
        self.n_best = n_best
        self.documents = []
        self.load_files_from_folder(folder_path)

    def load_files_from_folder(self, folder_path):
        files_to_choose = []
        for filename in glob.glob(os.path.join(folder_path, '*.*')):
            try:
                document = Document(filename)
                files_to_choose.append(document)
            except ValueError:
                continue
        self.documents = files_to_choose

    @staticmethod
    def preprocess_text(text):
        text = text.lower()
        text = text.translate(str.maketrans("", "", string.punctuation))
        tokens = word_tokenize(text)
        stop_words = set(stopwords.words("english"))
        tokens = [token for token in tokens if token not in stop_words]
        stemmer = PorterStemmer()
        tokens = [stemmer.stem(token) for token in tokens]
        preprocessed_text = " ".join(tokens)
        return preprocessed_text

    def return_top_files(self, question):
        if not self.documents:
            raise ValueError("No documents loaded for comparison")
        preprocessed_question = self.preprocess_text(question)
        vectorizer = TfidfVectorizer()
        file_texts = [doc.content for doc in self.documents] + [preprocessed_question]
        tfidf_matrix = vectorizer.fit_transform(file_texts)
        cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])[0]
        sorted_files = sorted(zip(cosine_similarities, [doc.filename for doc in self.documents]), reverse=True)
        return sorted_files[:self.n_best]


# Usage example:
if __name__ == "__main__":
    search_model = StemmedSemanticSearch()

    question = "Example question?"
    best_matching_files = search_model.return_top_files(question)
    print(best_matching_files)
