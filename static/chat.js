$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    $("#message").bind("input propertychange", function() {
        var json = {}
        json["uid"] = updater.uid;
        json["body"] = $("#message").val();
        updater.socket.send(JSON.stringify(json));
    });
    updater.start();
});

var updater = {
    socket: null,
    firstMsg: true,
    uid: null,

    start: function() {
        var url = "ws://" + location.host + "/sync";
        updater.socket = new WebSocket(url);
        updater.socket.onmessage = function(event) {
            if (updater.firstMsg) {
                updater.firstMsg = false;
                updater.uid = event.data;
                console.debug("uid:", updater.uid)
            } else {
                updater.showMessage(event.data);
            }
        }
    },

    showMessage: function(message) {
        $("#message").val(message);
    }
};
