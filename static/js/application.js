
$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
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
window.onload = function() {
var Clock = (function(){

	var exports = function(element) {
		this._element = element;
		var html = '';
		for (var i=0;i<6;i++) {
			html += '<span>&nbsp;</span>';
		}
		this._element.innerHTML = html;
		this._slots = this._element.getElementsByTagName('span');
		this._tick();
	};

	exports.prototype = {

		_tick:function() {
			var time = new Date();
			this._update(this._pad(time.getHours()) + this._pad(time.getMinutes()) + this._pad(time.getSeconds()));
			var self = this;
			setTimeout(function(){
				self._tick();
			},1000);
		},

		_pad:function(value) {
			return ('0' + value).slice(-2);
		},

		_update:function(timeString) {

			var i=0,l=this._slots.length,value,slot,now;
			for (;i<l;i++) {

				value = timeString.charAt(i);
				slot = this._slots[i];
				now = slot.dataset.now;

				if (!now) {
					slot.dataset.now = value;
					slot.dataset.old = value;
					continue;
				}

				if (now !== value) {
					this._flip(slot,value);
				}
			}
		},

		_flip:function(slot,value) {

			// setup new state
			slot.classList.remove('flip');
			slot.dataset.old = slot.dataset.now;
			slot.dataset.now = value;

			// force dom reflow
			slot.offsetLeft;

			// start flippin
			slot.classList.add('flip');

		}

	};

	return exports;
}());

var i=0,clocks = document.querySelectorAll('.clock'),l=clocks.length;
for (;i<l;i++) {
	new Clock(clocks[i]);
}
}
