var retries = 0;

function add_log(msg){
    var levels = {
        'INFO': 'info',
        'ERROR': 'danger',
        'DEBUG': 'default',
        'WARNING': 'warning'
    };

    level = levels[msg['levelname']];

    // check if we have the same message preceding this
    row = $("#loglist tr:first()");
    if (row.length){
        old_msg = row.data()
        // if the old msg contains the same msg
        if (msg.msg == old_msg){
            //increment the counter here
        }
    }

    // append data to the DOM item
    $("#loglist tr:first()").data(msg);

    $("#loglist").prepend(
        '<tr class="' + level + '"><td>'
            + msg['time'] +
        "</td><td><span class=\"logmsg\">" + msg['msg'] + "</span>" + '</td></tr>');

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