$(document).ready(function() {
	var socket = io.connect('http://localhost:5000');

  $('.chat-list-item').on('click', function() {
  	console.log('loading...' + this.id);
    socket.emit('switch', {'group': this.id});
    console.log('loaded chat group id: '+ this.id);
    showGrName(this.id);
  });

});

function showGrName(id){
	var name = document.getElementById(id).innerHTML;
	document.getElementById("chat-box-head").innerHTML = name;
}

function GetUserName(){
	var username = '<%= Session["user_name"] %>';
	return username;
}