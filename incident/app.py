from flask import Flask, request
from models import get_output

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/question', methods=['GET'])
def question():
    question = request.args.getlist("question")[0]
    llm = request.args.getlist("llm")[0]
    output = get_output(llm, question)
    return {'result': output}

if __name__ == '__main__':
    app.run(port=5002, debug=True)