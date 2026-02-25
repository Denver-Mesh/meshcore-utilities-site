from flask import Flask, render_template

from backend.api.routes.name_tool.index import name_tool
from backend.constants import FLASK_HOST, FLASK_PORT

app = Flask(__name__)
app.register_blueprint(name_tool)


# Landing page
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    # In Docker, we want to bind to all interfaces and disable debug mode
    app.run(debug=False, host=FLASK_HOST, port=FLASK_PORT)
