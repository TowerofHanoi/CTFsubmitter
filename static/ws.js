var retries = 0;

function connectws(){
    if ("WebSocket" in window) {
    // try connecting to tornado websocket interface
    var ws = new WebSocket("ws://" + window.location.hostname + ":8000/websocket");
    $(".footer").css("background-color","#ff6600");
    $(".footer").text("connecting...");

    ws.onopen = function() {
        $(".footer").css("background-color","#009900");
        $(".footer").hide(1000)
        // Web Socket is connected. You can send data by send() method.
        // ws.send("message to send");
    };
    ws.onmessage = function (evt) { var received_msg = JSON.parse(evt.data); };
    ws.onclose = function() {
        if (retries < 5){
            setTimeout(connectws, 1000);
            $(".footer").css("background-color","#ff6600");
            $(".footer").text("connecting...");
            $(".footer").show(10);
            retries++;
        }else{
            $(".footer").css("background-color","#ff0000");
            $(".footer").text("cannot connect to websocket :<");
        }
    };} else {
        $(".footer").css("background-color","#ff0000");
        $(".footer").text("no websockets :<");
    }
}

$( document ).ready(function() {
    connectws();
});