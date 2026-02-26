import json

from flask import Flask, render_template

from backend.api.routes.repeater_name_tool.index import repeater_name_tool
from backend.api.routes.companion_name_tool.index import companion_name_tool
from backend.api.routes.prefix_matrix.index import prefix_matrix
from backend.api.services.repeater_contacts import prepare_repeater_contacts
from backend.constants import FLASK_HOST, FLASK_PORT, FLASK_GET

app = Flask(__name__)
app.register_blueprint(repeater_name_tool)
app.register_blueprint(companion_name_tool)
app.register_blueprint(prefix_matrix)


# Landing page
@app.route('/', methods=[FLASK_GET])
def index():
    return render_template('index.html')


@app.route('/repeater_contacts', methods=[FLASK_GET])
def get_repeater_contacts():
    """
    Send a JSON file with all contacts for repeaters in the Denver area
    return: A JSON object with a list of contacts for repeaters in the Denver area
    """
    data = prepare_repeater_contacts()
    return json.dumps(data)


if __name__ == '__main__':
    # In Docker, we want to bind to all interfaces and disable debug mode
    app.run(debug=False, host=FLASK_HOST, port=FLASK_PORT)
