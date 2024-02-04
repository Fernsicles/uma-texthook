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
    rootAsset = next(iter(env.container.values())).get_obj()
    timeline = [x.read_typetree()
                for x in env.objects if 'Title' in x.read_typetree()]
    textClips = [x for x in timeline[0]['BlockList'] if 'TextTrack' in x]
    scene = {'Title': timeline[0]['Title'], 'Dialog': []}
    for x in textClips:
        index = x['BlockIndex']
        textClipPathId = x['TextTrack']['ClipList'][0]['m_PathID']
        textClip = rootAsset.assets_file.files[textClipPathId].read_typetree()
        dialog = {'Index': index, 'Name': textClip['Name'],
                  'Text': textClip['Text'], 'Choices': textClip['ChoiceDataList']}
        if not dialog['Name'] and not dialog['Text'] and not dialog['Choices']:
            continue
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
            newScenes = []
            if 'story_id' in msg['data']:
                newScenes = [getScene(msg['data']['story_id'])]
                socketio.send(json.dumps(scenes))
            if 'unchecked_event_array' in msg['data']:
                for x in msg['data']['unchecked_event_array']:
                    newScenes.append(getScene(x['story_id']))
            if 'single_mode_load_common' in msg['data']:
                for x in msg['data']['single_mode_load_common']['unchecked_event_array']:
                    newScenes.append(getScene(x['story_id']))
            if newScenes:
                scenes = newScenes
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
