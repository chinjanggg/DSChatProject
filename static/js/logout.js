$(document).ready(function() {
  $(".btn-logout").on('click', function() {
    emit('break', {});
    console.log('log out');
  });
});
