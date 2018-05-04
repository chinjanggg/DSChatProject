$(document).ready(function() {

  //connect
  var socket = io.connect('http://localhost:5000');
  socket.on('connect', function() {
      console.log('connected');
  });

  //append chat
  socket.on('text', function(msg) {
    var ms = msg['message'];
    var us = msg['user'];
    var tm = msg['time'];
    console.log("fsfg");
    if(us == getUn()){
      $(".message-area").append('<div class="r-text-box">'+ms+' ['+tm+']</div>');
    }else{
      $(".message-area").append('<div class="l-text-box">'+ms+' ['+tm+']</div>');
    }
    updateScroll();
  });

  function getUn(){
  var username = '<%= Session["user_name"] %>';
  return username;
}

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
