// Get Elements
var modal = document.getElementById('myModal');
var btn = document.getElementById("createChat");
var span = document.getElementsByClassName("close")[0];
var addbtn = document.getElementById("btn-addfriend");
var chatname = document.getElementById("name-input");
var funame = document.getElementById("funame-input");
var friendlist = document.getElementById("friendlist");
var fldiv = document.getElementsByClassName("friendlistdiv")

btn.onclick = function() {
  modal.style.display = "block";
}

span.onclick = function() {
  closeclear();
}

window.onclick = function(event) {
  if (event.target == modal) {
    closeclear();
  }
}

function closeclear() {
  chatname.value = "";
  funame.value = "";
  modal.style.display = "none";
  $("#friendlist").empty();
}

addbtn.onclick = function() {
  if(funame.value) {
    addFriendList(funame.value);
    funame.value = "";
    fldiv.scrollTop = fldiv.scrollHeight - fldiv.clientHeight;
  }
}

function addFriendList(username) {
  var node = document.createElement("LI");
  var textnode = document.createTextNode(username);
  node.appendChild(textnode);
  friendlist.append(node);
  console.log("add "+username)
}
