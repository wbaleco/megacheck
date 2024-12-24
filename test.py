from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Olá! Flask está funcionando!"

if __name__ == '__main__':
    app.run(port=8080, debug=True) 