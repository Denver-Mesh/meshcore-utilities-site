import os
from typing import Any

from flask import (
    Flask,
    render_template
)
from werkzeug.middleware.proxy_fix import ProxyFix

from backend.api.routes.companion_name_tool.index import companion_name_tool
from backend.api.routes.prefix_matrix.index import prefix_matrix
from backend.api.routes.repeater_name_tool.index import repeater_name_tool
from backend.api.routes.serial_usb_tool.index import serial_usb_tool
from backend.api.routes.contacts.index import contacts
from backend.api.services.meshcore_stats import StatsService
from backend.constants import FLASK_HOST, FLASK_PORT, FLASK_GET

app = Flask(__name__)

# Trust reverse-proxy forwarded headers so redirects/url_for keep the public host/scheme/prefix.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

application_root = os.getenv("APPLICATION_ROOT", "")
if application_root:
    app.config["APPLICATION_ROOT"] = application_root

preferred_url_scheme = os.getenv("PREFERRED_URL_SCHEME", "")
if preferred_url_scheme:
    app.config["PREFERRED_URL_SCHEME"] = preferred_url_scheme

server_name = os.getenv("SERVER_NAME", "")
if server_name:
    app.config["SERVER_NAME"] = server_name

app.register_blueprint(repeater_name_tool)
app.register_blueprint(companion_name_tool)
app.register_blueprint(prefix_matrix)
app.register_blueprint(serial_usb_tool)
app.register_blueprint(contacts)


# Landing page
@app.route('/', methods=[FLASK_GET])
def index():
    # TODO: Render stats widget
    stats = StatsService()
    node_count: int = stats.get_node_count()
    repeater_count: int = stats.get_repeater_count()
    companion_count: int = stats.get_companion_count()
    room_count: int = stats.get_room_count()
    _node_count_by_region: dict[str, int] = stats.get_node_count_by_region()  # {'fnl': 1, 'tex': 0, 'den': 3}
    node_region_leaderboard: list[dict[str, Any]] = sorted(
        [
            {"name": region_name, "count": count}
            for region_name, count in _node_count_by_region.items()
        ],
        key=lambda x: x["count"],
        reverse=True,
    )
    # [{'name': 'den', 'count': 3}, {'name': 'fnl', 'count': 1}, {'name': 'tex', 'count': 0}]

    return render_template('index.html',
                           node_count=node_count,
                           repeater_count=repeater_count,
                           companion_count=companion_count,
                           room_count=room_count,
                           node_region_leaderboard=node_region_leaderboard
                           )


if __name__ == '__main__':
    # In Docker, we want to bind to all interfaces and disable debug mode
    app.run(debug=False, host=FLASK_HOST, port=FLASK_PORT)
