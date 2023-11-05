from flask import Flask, request, abort, render_template
from flask_socketio import SocketIO, send
import msgpack
import sqlite3
import json
import os
import UnityPy

app = Flask(__name__)
socketio = SocketIO(app)
config = json.loads(open('config.json', 'r').read())
scenes = None
if not config['gamedata']:
    config['gamedata'] = os.path.join(os.path.expanduser(
        '~'), 'AppData', 'LocalLow', 'Cygames', 'umamusume')


def getScene(storyId):
    con = sqlite3.connect(os.path.join(config['gamedata'], 'meta'))
    cur = con.cursor()
    cur.execute(
        f"SELECT h FROM a WHERE instr(n, 'storytimeline_{storyId}') AND NOT instr(n, 'resources');")
    assetName = cur.fetchone()[0]
    assetPath = os.path.join(
        config['gamedata'], 'dat', assetName[0:2], assetName)
    env = UnityPy.load(assetPath)
    timeline = [x.read_typetree()
                for x in env.objects if 'Title' in x.read_typetree()]
    dialogs = [x.read_typetree()
               for x in env.objects if 'Text' in x.read_typetree()]
    scene = {'Index': None, 'Title': timeline[0]['Title'], 'Dialog': []}
    for x in dialogs:
        nextBlock = x['NextBlock']
        dialog = {'Name': x['Name'], 'Text': x['Text']}
        if not dialog['Name'] and not dialog['Text']:
            continue
        if nextBlock == -1:
            dialog['Index'] = len(dialogs) - 1
        else:
            dialog['Index'] = nextBlock - 1
        scene['Dialog'].append(dialog)
    scene['Dialog'].sort(key=lambda x: x['Index'])
    return scene


@app.route('/notify/response', methods=['POST'])
def receiveMsg():
    global scenes
    if request.method == 'POST':
        msg = msgpack.unpackb(request.get_data())
        print(json.dumps(msg))
        if 'data' in msg:
            scenes = []
            if 'story_id' in msg['data']:
                scenes = [getScene(msg['data']['story_id'])]
                socketio.send(json.dumps(scenes))
            if 'unchecked_event_array' in msg['data']:
                for x in msg['data']['unchecked_event_array']:
                    scenes.append(getScene(x['story_id']))
                socketio.send(json.dumps(scenes))
        return ''
    else:
        abort(405)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@socketio.on('connect')
def resend():
    if scenes:
        send(json.dumps(scenes))


if __name__ == '__main__':
    socketio.run(app, port=8080)
