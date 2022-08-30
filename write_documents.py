from ast import mod
from haystack import Document
import glob
from preprocessing import PreProcessorPDF
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import EmbeddingRetriever

docs_pdf = glob.glob('documents/*.pdf')


split_length = 300
split_overlap = 100

preprocesor = PreProcessorPDF()

docs_store = []
sources = []

for doc in docs_pdf:
    print('Doc Pdf:', doc)
    text_splits = preprocesor.process(doc)
    documents = [Document(content=text,  content_type= 'text' ) for text in text_splits]
    docs_store.extend(documents)
    sources.extend(len(documents) * [doc.split('/')[-1]])
print(docs_store)

doc_index = "document"

document_store = ElasticsearchDocumentStore(
    host= "localhost",
    username= "",
    password= "",
    index= doc_index,
    similarity= "cosine",
    embedding_dim= 512,
    embedding_field= "emb",
    excluded_meta_data=["emb"])

document_store.delete_documents(index= doc_index)

document_store.write_documents(docs_store)

retriever = EmbeddingRetriever(
    document_store=  document_store,
    embedding_model= "sentence-transformers/distiluse-base-multilingual-cased-v1",
    model_format = "sentence_transformers"
)

document_store.update_embeddings(retriever)

documents = retriever.run_query('cuando se realiza el retiro parcial?')

print(documents[0]['documents'][0].content)

#docs_pdf
