function setAllHeaderButtonsVisibility (willBeVisible) {
    const headerButtons = document.querySelectorAll('.welcome-actions-header > *');
    const newDisplayContent = (willBeVisible)
        ? 'inline-block'
        : 'none';

    for (const button of headerButtons) {
        button.style.display = newDisplayContent;
    }
}

function showHeaderCallToActionButtons () {
    setAllHeaderButtonsVisibility(true);
    document.getElementById('return-button').style.display = 'none';
}

const hideHeaderCallToActionButtons = () => {
    setAllHeaderButtonsVisibility(false);
    document.getElementById('return-button').style.display = 'block';
};


function showEmailField () {
    document.getElementById('registered-email-form').style.opacity = 1;
    document.getElementById('registered-email').focus();
    window.scrollTo(0, document.body.scrollHeight);
    hideHeaderCallToActionButtons();
}

function hideEmailField () {
    document.getElementById('registered-email-form').style.opacity = 0;
    showHeaderCallToActionButtons();
}
