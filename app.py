from flask_socketio import SocketIO
from flask import Flask, render_template
import json
import requests
from hashlib import sha1
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)


def get_last_hash():
    file = json.load(open("status.json"))
    return file['hash']


def update(new_hash):
    payload = {'hash': new_hash, 'last_updated': datetime.datetime.now().timestamp() * 1000}
    with open("status.json", "w") as f:
        f.write(json.dumps(payload))


def was_updated():
    r = requests.get('https://julioaalvarez.com/')
    # r = requests.get('http://localhost:8000')
    if r.status_code == 200:
        # Hash the page content
        hash = sha1(r.content).hexdigest()
        # Compare the hash with the previous hash
        if hash != get_last_hash() and hash != '' and hash is not None:
            update(hash)
            return True

    return False


def get_status_payload():
    file = json.load(open("status.json"))
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
    socketio.run(app,
                 static_url_path='',
                 static_folder="static")
