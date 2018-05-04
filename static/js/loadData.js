 function loadPage(){
    //loadChatList();
    //loadChatBox();
  }

  //____CHATLIST____
  function loadChatList(){
    //console.log("loadChatList");
    var i =0;
    for(i=0; i<15; i++){
      insertChatList(i);
    }
  }
  function insertChatList(chatID){
    //console.log("insert"+chatID);
    var node = document.createElement("LI");
    node.id = "chat"+chatID;
    node.className = "chat-list-item";
    node.innerHTML = getChatName(chatID);
    document.getElementById("chat-list").appendChild(node);
  }
  function getChatName(chatID){
    //console.log(chatID);
    return "Chat's Name "+ chatID;
  }

  //____CHATBOX____
  function loadChatBox(){
    var i = 0;
    for(i=0; i<20; i++){
      insertChatBox(i);
    }
  }
  function insertChatBox(textID){
    var node = document.createElement("DIV");
    node.id = "text"+textID;
    node.innerHTML = getText(textID);
    if(textID%3!=2){
      node.className = "l-text-box";
    }else{
      node.className = "r-text-box";
    }
    document.getElementById("message-area").appendChild(node);

  }
  function getText(textID){
    var text = ["Hello Suga",
                "I like your songs",
                "I like them too",
                "Haha",
                "I'm V",
                "?",
                "I want to be your friend",
                ":)",
                "..."];
    return text[textID%9];
  }
  