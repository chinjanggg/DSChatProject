$(document).ready(function() {
	var socket = io.connect('http://localhost:5000');

  $('.chat-list-item').on('click', function() {
  	console.log('loading...' + this.id);
    socket.emit('switch', {'group': this.id});
    console.log('loaded chat group id: '+ this.id);
  });

});