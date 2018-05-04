$(document).ready(function() {
	var socket = io.connect('http://localhost:5000');

  $("#join-group").on('click', function() {
    socket.emit('switch', {'group': this.id});
    console.log('load chat group id: '+ this.id);
  });
});