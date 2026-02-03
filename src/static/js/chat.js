var client_id = Math.floor(Math.random()*9999999999999999)
document.querySelector("#ws-id").textContent = client_id;
const ws = new WebSocket("ws://127.0.0.1:8080/chat/ws/" + client_id);
ws.onmessage = function(event) {
    var messages = document.getElementById('messages')
    var message = document.createElement('li')
    var content = document.createTextNode(event.data)
    message.appendChild(content)
    messages.appendChild(message)
};
function sendMessage(event) {
    var input = document.getElementById("messageText")
    ws.send(input.value)
    input.value = ''
    event.preventDefault()
}
