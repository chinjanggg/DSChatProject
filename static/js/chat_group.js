$(document).ready(function() {
	var socket = io.connect('http://localhost:5000');

  $("#chat-list-item").on('click', function() {
    socket.emit('switch', {'group': this.id});
    console.log('load chat group id: '+ this.id);
  });
});