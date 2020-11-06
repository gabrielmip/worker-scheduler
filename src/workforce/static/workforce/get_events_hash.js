function getEventsHash() {
    const xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            processHashDifferenceCheck(this.responseText);
        }
    };
    xhttp.open("GET", "/schedule_hash?date=" + requested_date, true);
    xhttp.send();
}

function processHashDifferenceCheck(newHash) {
    const hashIsEqual = (newHash === events_hash);
    document.getElementById('refresh-warner').style.display = hashIsEqual ? 'none' : 'flex';

    if (hashIsEqual) {
        setTimerToCheckHashDifference();
    }
}

const getMinutesInMiliseconds = (minutes) => minutes * 60 * 1000;

function setTimerToCheckHashDifference() {
    setTimeout(() => {
        getEventsHash();
    }, getMinutesInMiliseconds(1));
}

setTimerToCheckHashDifference();
