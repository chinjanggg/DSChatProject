$(document).ready(function() {
  $(".btn-logout").on('click', function() {
    emit('break', {}, broadcast=True, room=group);
    console.log('log out');
  });
});
