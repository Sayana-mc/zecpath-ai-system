from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


class EmbeddingEngine:
    """
    Generates semantic embeddings using
    Sentence Transformers.
    """

    def __init__(self):
        self.model = SentenceTransformer(
            MODEL_NAME
        )

    def encode(self, text):
        """
        Convert text into an embedding vector.
        """

        return self.model.encode(
            text,
            normalize_embeddings=True
        )

    def encode_many(self, texts):
        """
        Convert multiple texts into embeddings.
        """

        return self.model.encode(
            texts,
            normalize_embeddings=True
        )