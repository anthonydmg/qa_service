from haystack.pipelines import ExtractiveQAPipeline
from haystack.nodes import EmbeddingRetriever
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import FARMReader

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


retriever = EmbeddingRetriever(
    document_store=  document_store,
    embedding_model= "sentence-transformers/distiluse-base-multilingual-cased-v1",
    model_format = "sentence_transformers"
)

reader = FARMReader(model_name_or_path="mrm8488/bert-base-spanish-wwm-cased-finetuned-spa-squad2-es", use_gpu=True)

pipeline = ExtractiveQAPipeline(reader=reader, retriever=retriever)

#res = pipeline.run(
#    query = '¿Como realizar un retiro parcial de un curso?',
#    params = {'Retriever': {'top_k': 5}, 'Reader':{'top_k': 3}}
#)

#print(res['answers'])