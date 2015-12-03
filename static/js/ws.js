var retries = 0;

function add_log(msg){
    var levels = {
        'INFO': 'info',
        'ERROR': 'danger',
        'DEBUG': 'default',
        'WARNING': 'warning'
    };

    level = levels[msg['levelname']];

    // append data to the DOM item

    row = $("#loglist tr:first()");
    alert(row);
    // check if we have the same message preceding this

    $("#loglist").prepend(
        '<tr class="' + level + '"><td>'
            + msg['time'] +
        "</td><td><span class=\"logmsg\">" + msg['message'] + "</span>" + '</td></tr>');

    $("#loglist tr:first()").data(msg);
};

function set_footer(txt, color){
    $(".footer").css("background-color", color);
    $(".footer").text(txt);
}

function connectws(){
    if ("WebSocket" in window) {
    var ws = new WebSocket("ws://" + window.location.hostname + ":8888/websocket");
    set_footer("connecting...", "#ff6600");

    ws.onopen = function() {
        retries = 0;
        set_footer("connected...", "#009900");
        $(".footer").fadeOut(1800)
    };
    ws.onmessage = function (evt) {
        var msg = JSON.parse(evt.data);
        if( msg["msgtype"] == "log"){
            add_log(msg);
        }
    };

    ws.onerror = function(err) {
        set_footer(err, "#ff6600")
        $(".footer").fadeIn(500);
    }

    ws.onclose = function() {
        if (retries <= 5){
            setTimeout(connectws, 1000);
            set_footer("connecting...","#ff6600");
            $(".footer").fadeIn(500);
            retries++;
        }else{
            set_footer("cannot connect to websocket :<","#ff0000");
        }
    };} else {
        set_footer("no websockets :<","#ff0000");
    }

}

$( document ).ready(function() {
    connectws();
});