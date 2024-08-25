document.getElementById('change-avatar-button').addEventListener('click', function() {
    document.getElementById('avatar-input').click();
});

document.getElementById('avatar-input').addEventListener('change', function() {
    document.querySelector('form.change-avatar-form').submit();
});
