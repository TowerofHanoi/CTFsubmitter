var retries = 0;

function add_log(msg){
    var levels = {
        'INFO': 'info',
        'ERROR': 'danger',
        'DEBUG': 'default',
        'WARNING': 'warning'
    };

    var level = levels[msg.levelname];

    // append data to the DOM item
    // check if we have the same message preceding this
    var row = $("#loglist tr:first()");

    function push_row(){
        var table = $("#loglist").prepend(
        '<tr class="' + level + '"><td class="col-xs-2">'
        + msg.time +
        '</td><td class="col-xs-9"><span class="logmsg">' + msg.msg + "</span>" + '</td><td>&nbsp;</td></tr>');
        var tr = table.find('tr:first()');
        tr.data({"logs": [msg]});
    }

    if (row.length == 0){
        push_row();
    }else{
        var rdata = row.data();
        if(msg.msg == rdata.logs[0].msg){
            rdata.logs.push(msg);
            row.children('td:first()').text(msg.time);
            // update counter
            row.children('td:last()').html(
                '<span class="badge pull-right">' +
                rdata.logs.length +
                '</span>');
        }else{
            push_row()
        }
    }

};


function update_stats(msg){
    if (msg['_id'] == '_total'){
        $('#total_submitted').text(msg.total_submitted);
        $('#correctly_added').text(msg.total_inserted);
        $('#error_inserting').text(msg.total_submitted-msg.total_inserted);
    }else{
        $('#total_submitted').text(msg.total_submitted);
    }
}


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
        switch(msg.msgtype){
            case "log":
                add_log(msg);
                break;
            case "stats":
                update_stats(msg);
                break;
            default:
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