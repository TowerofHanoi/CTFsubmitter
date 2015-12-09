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
            counter = rdata.logs.length <= 99 ? rdata.logs.length : '<span class="verysmall">99+</small>';
            row.children('td:last()').html(
                '<span class="badge pull-right">' +
                counter + '</span>');
        }else{
            push_row()
        }
    }

};

function update_stats(msg){

    function long2ip(ip) {
      //  discuss at: http://phpjs.org/functions/long2ip/
      // original by: Waldo Malqui Silva
      //   example 1: long2ip( 3221234342 );
      //   returns 1: '192.0.34.166'

      if (!isFinite(ip))
        return false;

      return [ip >>> 24, ip >>> 16 & 0xFF, ip >>> 8 & 0xFF, ip & 0xFF].join('.');
    }

    // must be rewritten!
    if (msg['_id'] == '_total'){
        $('#total_submitted').text(msg.total_submitted);
        $('#correctly_added').text(msg.total_inserted);
        $('#error_inserting').text(msg.total_submitted-msg.total_inserted);
        return;
    }

    var table;
    var row = $("#"+msg['_id']);
    if (row)
        row.remove()

    var insert_err = (msg.total_submitted - msg.total_inserted);

    function get_var(vname){
        if (typeof(msg[vname]) == 'undefined')
            return '-';

        return msg[vname];
    }

    var old = get_var('old');
    var accepted = get_var('accepted');
    var wrong = get_var('rejected');

    function err_class(){

        result = 0;


        result += (insert_err > msg.total_submitted/2);

        if (old != '-' && accepted != '-' && wrong != '-'){
            result  += (wrong+old > accepted);
        }

        if (result == 1)
            return 'warning'
        else if (result == 2)
            return 'danger'
        else
            return 'default'
    }


    if(msg['_id'].indexOf("service") > -1){
        table = $("#services");
        table.prepend(
            "<tr class=" + err_class() +
            " id="+ msg['_id'] + ">" +
            "<td>" + msg['_id'].substr(8) + "</td>" + 
            "<td>" + get_var('teams').length + "</td>" +
            "<td>" + accepted + "</td>" +
            "<td>" + old + "</td>" +
            "<td>" + wrong + "</td>" +
            "<td>" + msg.total_submitted + "</td>" +
            "<td>" + msg.total_inserted + "</td>" +
            "<td>" + insert_err + "</td>" +
            "</tr>"
        )
    }else if(msg['_id'].indexOf("team") > -1){
        table = $("#teams");
        table.prepend(
            "<tr class=" + err_class() +
            " id="+ msg['_id'] + ">" +
            "<td>" + msg['_id'].substr(5) + "</td>" + 
            "<td>" + get_var('services').length + "</td>" + 
            "<td>" + accepted + "</td>" +
            "<td>" + old + "</td>" +
            "<td>" + wrong + "</td>" +
            "<td>" + msg.total_submitted + "</td>" +
            "<td>" + msg.total_inserted + "</td>" +
            "<td>" + insert_err + "</td>" +
            "</tr>"
        )
    }else if(msg['_id'].indexOf("user") > -1){
        var ip = long2ip(parseInt(msg.ip));
        table = $("#users");
        table.prepend(
            "<tr class=" + err_class() +
            " id="+ msg['_id'] + ">" +
            "<td>" + ip + "</td>" +
            "<td>" + msg['_id'].substr(5) + "</td>" +
            "<td>" + accepted + "</td>" +
            "<td>" + old + "</td>" +
            "<td>" + wrong + "</td>" +
            "<td>" + msg.total_submitted + "</td>" +
            "<td>" + msg.total_inserted + "</td>" +
            "<td>" + insert_err + "</td>" +
            "</tr>"
        )
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