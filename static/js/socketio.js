$(document).ready(function() {
    var socket = io.connect('http://localhost:5000');
    socket.on('connect', function() {
  console.log('connected');
    });

  socket.on('receive_message', function(message) {
    $(".message-show").append('<li>'+message+'</li>');
    console.log('Received message');
  });
 });
