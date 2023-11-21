import nltk

nltk.download('punkt')
nltk.download('stopwords')

from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import string


@dataclass
class FileContents:
    filename: str = ""
    file_text: str = ""


class ParagraphSearch:
    def __init__(self, n_best: int = 10):
        self.n_best = n_best
        self.paragraphs = {}
        self.paragraph_contents_list = []

    def load_paragraphs(self, paragraphs):
        for idx, doc in enumerate(paragraphs):
            paragraph_alias = f"Document {idx}"
            self.paragraphs[paragraph_alias] = doc
            self.paragraph_contents_list.append(FileContents(paragraph_alias, self.preprocess_text(doc['content'])))

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

    def return_top_paragraphs(self, question):
        if not self.paragraph_contents_list:
            raise ValueError("No documents loaded for comparison")
        preprocessed_question = self.preprocess_text(question)
        vectorizer = TfidfVectorizer()
        paragraphs_texts = [fc.file_text for fc in self.paragraph_contents_list] + [preprocessed_question]
        tfidf_matrix = vectorizer.fit_transform(paragraphs_texts)
        cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])[0]
        sorted_paragraphs = sorted(zip(cosine_similarities, [fc.filename for fc in self.paragraph_contents_list]),
                                   reverse=True)
        n_best_paragraphs = sorted_paragraphs[:self.n_best]
        result = []
        for score, paragraph_alias in n_best_paragraphs:
            result.append((score, self.paragraphs[paragraph_alias]))
        return result


# Usage example:
if __name__ == "__main__":
    search_model = ParagraphSearch()

    paragraphs = [
        {'file': '/home/user/Documents/GitHub/qa-chatbot-synerise/data/raw/0-docs-ai-search-introduction-to-ai-search-.md',
         'content': "Text of the first document."},
        {'file': '/home/user/Documents/GitHub/qa-chatbot-synerise/data/raw/0-docs-ai-search-introduction-to-ai-search-.md',
         'content': "Content of the second document."},
        {'file': '/home/user/Documents/GitHub/qa-chatbot-synerise/data/raw/0-docs-ai-search-introduction-to-ai-search-.md',
         'content': "Another example document."}
    ]

    search_model.load_paragraphs(paragraphs)

    question = "Example question?"
    best_matching_paragraphs = search_model.return_top_paragraphs(question)
    print(best_matching_paragraphs)
