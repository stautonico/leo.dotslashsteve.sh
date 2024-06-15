from flask_socketio import SocketIO
from flask import Flask, render_template
import json
import datetime
import os
import subprocess

app = Flask(__name__)
app.config['SECRET_KEY'] = 'myreallysecureuselesskey'
app.config['DEBUG'] = True

FOLDER_NAME = "julioaalvarez.com"
DATE_FORMAT = "%a %b %d %H:%M:%S %Y"

socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)


def get_last_updated():
    if not os.path.exists("status.json"):
        return datetime.datetime.fromtimestamp(0)

    file = json.load(open("status.json"))

    return datetime.datetime.fromtimestamp(file["last_updated"])


def update(timestamp):
    payload = {"last_updated": timestamp.timestamp()}
    with open("status.json", "w") as f:
        f.write(json.dumps(payload))


def was_updated():
    # if not os.path.exists(FOLDER_NAME):
    #     os.system("git clone https://github.com/JulioAAlvarez/julioaalvarez.com")

    # os.chdir(FOLDER_NAME)

    os.system("git pull")

    timestring = subprocess.check_output("git log -1 --format=%cd --date=local".split()).decode().replace("\n", "")

    date_obj = datetime.datetime.strptime(timestring, DATE_FORMAT)

    # os.chdir("..")

    if date_obj > get_last_updated():
        update(date_obj)
        return True
    else:
        return False


def get_status_payload():
    file = json.load(open("status.json"))
    file["last_updated"] = file["last_updated"] * 1000
    return file


def get_status():
    while True:
        if was_updated():
            socketio.emit("status", get_status_payload(), namespace='/status')
        socketio.sleep(10)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect', namespace='/status')
def status_connect():
    # Send the first one over (because it'll delay the first one by 10 seconds for some reason)
    was_updated()
    socketio.emit('status', get_status_payload(), namespace='/status')

    socketio.start_background_task(get_status)


@socketio.on('disconnect', namespace='/status')
def status_disconnect():
    # Do something on disconnect
    pass


if __name__ == '__main__':
    socketio.run(app)
