from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

loader = PyPDFDirectoryLoader('.../data/')
pages = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=100,
    separators=['\n\n', '\n', '(?<=\. )', ' ', '']
)
docs = splitter.split_documents(pages)

embedding = HuggingFaceEmbeddings()

vectordb = FAISS.from_documents(
    documents=docs,
    embedding=embedding
)

vectordb.save_local('faiss_index')
