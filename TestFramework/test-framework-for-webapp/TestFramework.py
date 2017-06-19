from flask import Flask
import webbrowser
app = Flask(__name__)


@app.route('/')
def hello():
    return "Hello World!"

if __name__ == '__main__':
    webbrowser.open_new('http://127.0.0.1:5000')
    app.run()
