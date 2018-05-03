$(document).ready(function() {
  var socket = io.connect('http://localhost:5000');

  $("#join-group").on('click', function() {
    socket.emit('join', $("#gid-input").val());
    console.log('join group id: '+$("#gid-input").val());
    $("#gid-input").val("");
  });
});
