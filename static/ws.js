if ("WebSocket" in window) {
    // try connecting to tornado websocket interface
    var ws = new WebSocket("ws://" + window.location.hostname + ":8000/websocket");
        ws.onopen = function() {
            // Web Socket is connected. You can send data by send() method.
            // ws.send("message to send");
    };
    ws.onmessage = function (evt) { var received_msg = JSON.parse(evt.data); };
    ws.onclose = function() { alert('websocket closed :(\n...try realoading page') };
} else {
    alert('no websocket :(')
}