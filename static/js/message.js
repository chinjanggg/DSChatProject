$(document).ready(function() {

  //connect
  var socket = io.connect('http://localhost:5000');
  socket.on('connect', function() {
      console.log('connected');
  });

  //append chat
  socket.on('message', function(msg) {
    $(".message-area").append('<li>'+msg+'</li>');
    updateScroll();
  });
  //send message when click
  $(".btn-sendmsg").on('click', function() {
    sendMessage();
  });

  //send message when hit enter
  $("#chat-input").keypress(function(e) {
    var code = e.keyCode || e.which;
    if (code == 13) {
      sendMessage();
    }
  });

  function sendMessage() {
    console.log("Sent Message: "+$("#chat-input").val());
    socket.send($("#chat-input").val());
    $("#chat-input").val("");
  }

  function updateScroll() {
    var msgDiv = document.getElementById("message-area");
    msgDiv.scrollTop = msgDiv.scrollHeight - msgDiv.clientHeight;
  }

});
