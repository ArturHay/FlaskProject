from flask import Flask

app = Flask(__name__)

@app.route('/call22', methods=['GET'])
def call22():
    return "22", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8877)
