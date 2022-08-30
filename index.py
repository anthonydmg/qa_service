from flask import Flask, request, render_template, jsonify
from qa_pipeline import pipeline, document_store
from utils import find_in_list_dicts

app = Flask(__name__)



@app.route('/api/question-answering', methods = ['POST'])
def apiQuestionAnswering():
    print('---request---')
    print(request)
    body = request.get_json()
    print(body)
    question = body['question']
    #question = request.form['quesion']
    #question = request.for                                                                                                                                                                                                                                                             m['question']
    #print(question)
    answers =  pipeline.run(
        query = question,  
        params = {'Retriever': {'top_k': 5}, 'Reader':{'top_k': 3}})
    answers = answers['answers']                                                                                                                                            
    doc_ids = [ ans.document_id for ans in answers]
    print('doc_ids:', doc_ids)
    documents = document_store.get_documents_by_id(doc_ids)
    documents = [doc.to_dict() for doc in documents]
    answers = [ ans.to_dict() for ans in answers]
    for ans in answers:
        ans['document'] = find_in_list_dicts(documents, "id", ans['document_id'])
    #answers = [ans.to_dict() for ans in answers]
    #print('documents: ',documents)
    
    return jsonify(answers)

if __name__== '__main__':
    app.run(host = '0.0.0.0', port = 5035, debug= True)


