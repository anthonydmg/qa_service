from flask import Flask, request, render_template, jsonify
from qa_pipeline import pipeline

app = Flask(__name__, template_folder= 'templates')

@app.route('/api/question-answering', methods = ['POST'])
def apiQuestionAnswering():
    print('---request---')
    #question = request.form['quesion']
    question = request.form['question']
    print(question)
    answers =  pipeline.run_query(question,  params = {'Retriever': {'top_k': 5}, 'Reader':{'top_k': 3}})
    
    return jsonify(answers)

if __name__== '__main__':
    app.run(host = '0.0.0.0', port = 105, debug= True)


