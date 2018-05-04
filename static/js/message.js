var history ;

$(document).ready(function() {

  //connect
  var socket = io.connect('http://localhost:5000');
  socket.on('connect', function() {
      console.log('connected');
  });

  //append chat
  socket.on('text', function(msg) {
    history = msg;
    //$(".message-area").append('<div class="text-box">'+us+': '+ms+' ['+tm+']</div>');
    updateScroll();
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

/////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
  var socket = io.connect('http://localhost:5000');

  $('.chat-list-item').on('click', function() {
    socket.emit('switch', {'group': this.id});
    showGrName(this.id);
    //reloadChat();
    clear_msg_box();
    show_history(this.id);
    console.log("printed")
  });

});

function showGrName(id){
  var name = document.getElementById(id).innerHTML;
  document.getElementById("chat-box-head").innerHTML = name;
}

function getUserName(){
  var username = '<%= Session["user_name"] %>';
  return username;
}

function reloadChat() {
    var wait = document.getElementById('waited-msg').innerHTML;
    document.getElementById('message-area').innerHTML = wait;
    console.log("display")
}

///////////////////////////////////////////////////////////////////////////////////

function clear_msg_box() {
  document.getElementById("message-area").innerHTML = "";
 } 

 function append_msg(msg) {
  var pnode = document.createElement("DIV");
  var cnode = document.createElement("SPAN");
  pnode.className = "l-text-box";
  pnode.innerHTML = msg['message'];
  cnode.innerHTML = msg['user'] + " [" + msg['time'] + "]";
  pnode.appendChild(cnode);
  document.getElementById("message-area").appendChild(pnode);
 }

 function show_history(grId){
  var i =0;
  for (var i = 0 ; i< history.length - 1; i++) {
    if(history[i]['group'] == grId) append_msg(history[i]);
    console.log('history'+i);
  }
 }
