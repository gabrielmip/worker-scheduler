function getUserTimezoneOffset () {
    return (new Date()).getTimezoneOffset() / 60;
}

function localizeDateOptions () {
    const offset = getUserTimezoneOffset();
    const dateOptionCapturer = /([^ ]* )(\d\d)(.*)/;
    const options = Array.from(document.querySelectorAll('#id_timeslots_available > option'));

    for (const option of options) {
        const [_, dayOfTheWeek, hour, seconds] = option.innerHTML.match(dateOptionCapturer);
        const localizedHour = Number(hour) - offset;
        option.innerHTML = `${dayOfTheWeek}${localizedHour}${seconds}`;
    }
}

setTimeout(() => {
    document.getElementById('user_timezone_field').value = getUserTimezoneOffset();
    localizeDateOptions();
});
