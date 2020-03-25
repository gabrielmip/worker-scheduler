function getUserTimezone () {
    return Intl.DateTimeFormat().resolvedOptions().timeZone;
}

setTimeout(() => {
    document.getElementById('user_timezone_field').value = getUserTimezone();
});
