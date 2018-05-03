$(document).ready(function() {
  $("#join-group").on('click', function() {
    emit('join', $("#gid-input").val());
    console.log('join group id: '+$("#gid-input").val());
    $("#gid-input").val("");
  });
});
