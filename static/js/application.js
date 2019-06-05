
$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('https://' + document.domain + ':' + location.port + '/test');
    var numbers_received = [];

    //receive details from server
    socket.on('newnumber', function(msg) {
        console.log("Received number" + msg.number);
        //maintain a list of ten numbers
        if (numbers_received.length >= 1){
            numbers_received.shift()
        }
        numbers_received.push(msg.number);
        numbers_string = '';
        for (var i = 0; i < numbers_received.length; i++){
            numbers_string = numbers_string + '<p>' + numbers_received[i].toString() + '</p>';
        }
        $('#log').html(numbers_string);
    });

    socket.on('newtime', function(msg) {
        console.log("Received number" + msg.time);
        //maintain a list of ten numbers
        if (numbers_received.length >= 1){
            numbers_received.shift()
        }
        numbers_received.push(msg.time);
        numbers_string = '';
        for (var i = 0; i < numbers_received.length; i++){
            numbers_string = numbers_string + '<p>' + numbers_received[i].toString() + '</p>';
        }
        $('#log2').html(numbers_string);
    });
});
