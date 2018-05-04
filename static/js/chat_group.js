$(document).ready(function() {
	var socket = io.connect('http://localhost:5000');

  $('.chat-list-item').on('click', function() {
    socket.emit('switch', {'group': this.id});
    showGrName(this.id);
    reloadChat();
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
}