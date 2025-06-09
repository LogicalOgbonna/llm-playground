import os

from chromadb import HttpClient
from langchain.embeddings.base import Embeddings
from langchain.schema.document import Document
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter 

from src.constants import Constants

CHROMA_PATH = "chroma"


class ChromaVectorDB:
    """
    This class is used to connect to the Chroma vector database.
    It is used to create a new index, connect to an existing index,
    and add documents to the index.
    """

    vector_store = None

    def __init__(self, index_name: str, embedding: Embeddings):
        """
        This method is used to initialize the Chroma vector database.
        It creates a new instance of the Chroma vector database.
        """
        self.connect(index_name=index_name, embedding=embedding)

    def connect(self, index_name: str, embedding: Embeddings):
        """
        This method is used to connect to the Chrome collection.
        :param index_name: The name of the collection to connect to.
        :param embedding: The embedding function to use for the collection.
        """
        if self.vector_store is not None:
            return self.vector_store

        self.vector_store = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=embedding,
            collection_name=index_name,
        )
        return self.vector_store

    @staticmethod
    def calculate_chunk_ids(chunks: list[Document], metadata: [dict] = []):
        """
        This method is used to calculate the chunk IDs for the documents.
        :param chunks: The chunks to calculate the IDs for.
        :return: The chunks with the IDs added to the metadata.
        """
        # This will create IDs like "data/monopoly.pdf:6:2"
        # Page Source : Page Number : Chunk Index

        last_page_id = None
        current_chunk_index = 0

        for chunk in chunks:
            source = chunk.metadata.get("source")
            page = chunk.metadata.get("page")
            current_page_id = f"{source}:{page}"

            # If the page ID is the same as the last one, increment the index.
            if current_page_id == last_page_id:
                current_chunk_index += 1
            else:
                current_chunk_index = 0

            # Calculate the chunk ID.
            chunk_id = f"{current_page_id}:{current_chunk_index}"
            last_page_id = current_page_id

            # Add it to the page meta-data.
            chunk.metadata["id"] = chunk_id

            # Add filter metadata if provided
            if metadata:
                for item in metadata:
                    for key, value in item.items():
                        chunk.metadata[key] = value
        return chunks

    def add_documents(self, documents: list[Document], metadata: [dict] = []):
        """
        This method is used to add documents to the Chroma index.
        :param documents: The documents to add to the index.
        :return: A dictionary with the success status and message.
        """

        chunks_with_ids = self.calculate_chunk_ids(documents, metadata)

        # Add or Update the documents.
        existing_items = self.vector_store.get(
            include=[]
        )  # IDs are always included by default
        existing_ids = set(existing_items["ids"])

        # Only add documents that don't exist in the DB.
        new_chunks = []
        for chunk in chunks_with_ids:
            if chunk.metadata["id"] not in existing_ids:
                new_chunks.append(chunk)

        if not new_chunks:
            return {"success": True, "message": "No new valid documents to add"}

        for batch_chunks in self.batch(new_chunks, 100):
            batch_ids = [chunk.metadata["id"] for chunk in batch_chunks]
            self.vector_store.add_documents(batch_chunks, ids=batch_ids)

    def search(self, query: str, k: int = 2, filter: dict = None) -> list[Document]:
        """
        This method is used to search for documents in the Chroma index.
        :param query: The query to search for.
        :param k: The number of documents to return.
        :param filter: Optional metadata filter dictionary.
        :return: A list of documents that match the query.
        """

        results = self.vector_store.similarity_search(query, k=k, filter=filter)
        return results

    @staticmethod
    def batch(iterable, n=100):
        """Split iterable into batches of n."""
        for i in range(0, len(iterable), n):
            yield iterable[i : i + n]

    @staticmethod
    def load_documents(file_path: str):
        loader = PyPDFDirectoryLoader(file_path)

        return loader.load()

    @staticmethod
    def split_documents(documents: list[Document], chunk_size: int, chunk_overlap: int):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        return text_splitter.split_documents(documents)
