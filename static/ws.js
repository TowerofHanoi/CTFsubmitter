var retries = 0;

function connectws(){
    if ("WebSocket" in window) {
    // try connecting to tornado websocket interface
    var ws = new WebSocket("ws://" + window.location.hostname + ":8888/websocket");
    $(".footer").css("background-color","#ff6600");
    $(".footer").text("connecting...");

    ws.onopen = function() {
        retries = 0;
        $(".footer").css("background-color","#009900");
        $(".footer").text("connected...");
        $(".footer").fadeOut(1500)
        // Web Socket is connected. You can send data by send() method.
        // ws.send("message to send");
    };
    ws.onmessage = function (evt) {
        var levels = {
            'INFO': 'info',
            'ERROR': 'danger',
            'DEBUG': 'default',
            'WARNING': 'warning'
        };

        var msg = JSON.parse(evt.data);
        level = levels[msg['levelname']];

        $("#loglist").prepend(
            '<li class="list-group-item list-group-item-'+
            level +'">'+ msg['message'] +'</li>');
    };
    ws.onclose = function() {
        if (retries <= 5){
            setTimeout(connectws, 1000);
            $(".footer").css("background-color","#ff6600");
            $(".footer").text("connecting...");
            $(".footer").fadeIn(500);
            retries++;
        }else{
            $(".footer").css("background-color","#ff0000");
            $(".footer").text("cannot connect to websocket :<");
        }
    };} else {
        $(".footer").css("background-color","#ff0000");
        $(".footer").text("no websockets :<");
    }

    ws.onerror = function(err) {
        $(".footer").css("background-color","#ff6600");
        $(".footer").text(err);
        $(".footer").fadeIn(500);
    }
}

$( document ).ready(function() {
    connectws();
});