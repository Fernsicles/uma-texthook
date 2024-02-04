let socket = io();
socket.on('message', (msg) => {
    let sceneList = document.getElementById('sceneList');
    let scenes = JSON.parse(msg);
    console.log(scenes);
    scenes.forEach((i) => {
        let scene = Object.assign(document.createElement('li'));
        let title = Object.assign(document.createElement('div'), { textContent: i.Title });
        scene.append(title);
        let dialog = Object.assign(document.createElement('ol'));
        scene.append(dialog);
        i.Dialog.forEach((i) => {
            let element = Object.assign(document.createElement('li'));
            element.value = i.Index;
            let name = Object.assign(document.createElement('div'), { textContent: i.Name });
            element.append(name);
            let text = Object.assign(document.createElement('div'), { textContent: i.Text });
            element.append(text);
            if (i.Choices.length) {
                let choices = Object.assign(document.createElement('div'));
                choices.append(Object.assign(document.createElement('div'), { textContent: 'Choices:' }));
                let choiceList = Object.assign(document.createElement('ol'));
                choices.append(choiceList);
                i.Choices.forEach((j) => {
                    let choice = Object.assign(document.createElement('li'));
                    let choiceText = Object.assign(document.createElement('div'), { textContent: j.Text });
                    choice.append(choiceText);
                    let nextBlock = Object.assign(document.createElement('div'), { textContent: `Next line: ${j.NextBlock}` });
                    choice.append(nextBlock);
                    choiceList.append(choice);
                });
                element.append(choices);
            }
            dialog.append(element);
        });
        sceneList.append(scene);
    });
});