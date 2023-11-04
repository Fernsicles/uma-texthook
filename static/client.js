let socket = io();
socket.on('message', (msg) => {
    console.log(msg);
    let title = document.getElementById('title');
    let dialogList = document.getElementById('dialogList')
    let dialog = JSON.parse(msg);
    title.innerText = dialog.Title;
    dialog.Dialog.forEach((i) => {
        let name = Object.assign(document.createElement('div'), {textContent: i.Name});
        let text = Object.assign(document.createElement('div'), {textContent: i.Text});
        let element = Object.assign(document.createElement('li'));
        element.append(name);
        element.append(text);
        dialogList.append(element);
    });
});