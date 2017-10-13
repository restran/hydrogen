import webbrowser

import webview
from flask import Flask
from flask import render_template, jsonify, request
from flask_debugtoolbar import DebugToolbarExtension
from mountains import logging
from mountains.logging import StreamHandler
from urls import init_url_rules
import settings

logging.init_log(StreamHandler())
logger = logging.getLogger(__name__)

# gui_dir = os.path.join(os.getcwd(), "templates")  # development path

# server = Flask(__name__, static_folder='static', template_folder='templates')
# server.config["SEND_FILE_MAX_AGE_DEFAULT"] = 1  # disable caching


# from blueprints.flaskr import init_db


# def register_blueprints(app):
#     """Register all blueprint modules
#     Reference: Armin Ronacher, "Flask for Fun and for Profit" PyBay 2016.
#     """
#     for name in find_modules('blueprints'):
#         logger.debug(name)
#         mod = import_string(name)
#         if hasattr(mod, 'bp'):
#             app.register_blueprint(mod.bp)
#     return None


app = Flask(__name__)

app.config.update(dict(
    # DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=settings.DEBUG,
    SECRET_KEY=settings.SECRET_KEY,
    static_folder='static',
    template_folder='templates',
    SEND_FILE_MAX_AGE_DEFAULT=1
))

toolbar = DebugToolbarExtension(app)


# app.config.from_envvar('FLASKR_SETTINGS', silent=True)

# register_blueprints(app)


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response


@app.route("/")
def landing():
    return render_template("index.html")


@app.route("/index2")
def landing2():
    return render_template("index2.html")


@app.route("/api/choose-path")
def choose_path():
    """
    Invoke a folder selection dialog here
    :return:
    """
    dirs = webview.create_file_dialog(webview.FOLDER_DIALOG)
    if dirs and len(dirs) > 0:
        directory = dirs[0]
        if isinstance(directory, bytes):
            directory = directory.decode("utf-8")

        response = {"status": "ok", "directory": directory}
    else:
        response = {"status": "cancel"}

    return jsonify(response)


@app.route("/api/full-screen")
def full_screen():
    webview.toggle_fullscreen()
    return jsonify({})


@app.route("/api/open-url", methods=["POST"])
def open_url():
    url = request.json["url"]
    webbrowser.open_new_tab(url)

    return jsonify({})


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 200


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 200


def run_server():
    init_url_rules(app)
    app.run(host="127.0.0.1", port=settings.PORT, threaded=True)


if __name__ == "__main__":
    run_server()
