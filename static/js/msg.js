 //{ i : {'message': message, 'user':userid, 'time':time, 'group':groupid }}

 function clear_msg_box() {
 	document.getElementByID("message-area").innerHTML = "";
 }

 function append_msg(msg) {
 	var pnode = document.createElement("DIV");
 	var cnode = document.createElement("SPAN");
 	pnode.className = "l-text-box";
 	pnode.innerHTML = msg[message];
 	cnode.innerHTML = msg[user] + " [" + msg[time] + "]";
 	pnode.appendChild(cnode);
 	document.getElementByID("message-area").appendChild(pnode);
 }

 