// Open Feedback Popup in a New Window
document.addEventListener("DOMContentLoaded", function () {
    const feedbackButton = document.getElementById("feedbackButton");

    if (feedbackButton) {
        feedbackButton.addEventListener("click", function () {
            const popupWidth = 400;
            const popupHeight = 300;
            const left = (window.screen.width - popupWidth) / 2;
            const top = (window.screen.height - popupHeight) / 2;

            window.open(
                "/feedback/", // Replace with your feedback form URL or route
                "FeedbackForm",
                `width=${popupWidth},height=${popupHeight},top=${top},left=${left},resizable=no,scrollbars=no`
            );
        });
    }
});
