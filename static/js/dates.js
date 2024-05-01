// Getting dates and times from the client, not the server.
// Used in homepage.html

// Get ampm function for time of day
function getAmPm() {
    let hours = new Date().getHours();
    if (hours < 12) {
        return 'morning';
    } else if (hours < 18) {
        return 'afternoon';
    } else {
        return 'evening';
    }
}

// getting the current date (formatted)
function getDate() {
    var current = new Date();
    var day = current.getDate();
    var suffix = "";

    // Determine the suffix for the day
    if (day === 1 || day === 21 || day === 31) {
        suffix = "st";
    } else if (day === 2 || day === 22) {
        suffix = "nd";
    } else if (day === 3 || day === 23) {
        suffix = "rd";
    } else {
        suffix = "th";
    }

    var formattedDate = current.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
    formattedDate = formattedDate.replace(/, \d{4}/, ''); // removing year from string

    return formattedDate + suffix;
}