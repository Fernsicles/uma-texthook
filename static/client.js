let socket = io();
socket.on('message', (msg) => {
    let sceneList = document.getElementById('sceneList');
    let scenes = JSON.parse(msg);
    console.log(scenes);
    scenes.forEach((i) => {
        let scene = Object.assign(document.createElement('li'));
        let title = Object.assign(document.createElement('div'), { textContent: i.Title });
        scene.append(title);
        let dialog = Object.assign(document.createElement('ul'));
        scene.append(dialog);
        i.Dialog.forEach((i) => {
            let element = Object.assign(document.createElement('li'));
            let name = Object.assign(document.createElement('div'), { textContent: i.Name });
            element.append(name);
            let text = Object.assign(document.createElement('div'), { textContent: i.Text });
            element.append(text);
            dialog.append(element);
        });
        sceneList.append(scene);
    });
});