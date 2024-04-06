'use strict';

function handleResponse(data) {
    $('#dhallMenusDiv').html(data);
    var newHtml = $('#todaysDateDivUpdate').html();

    // Set the HTML content of #todaysDateDiv
    $('#todaysDateDiv').html(newHtml);
    // After adding dynamic content to the DOM, call the setup function
    setup();
}

function handleError() {
    alert('Error: Failed to fetch data from server');
}

function getResults() {
    let mealtime = $("input[name='mealtime_btnradio']:checked").val();
    const currentDate = $('#currentDateDiv').text();

    console.log(mealtime);
    console.log(currentDate)
    let encoded_mealtime = encodeURIComponent(mealtime);
    let encoded_date = encodeURIComponent(currentDate)
    let url = '/update-menus-mealtime?mealtime=' + encoded_mealtime + "&currentdate=" + encoded_date;
    let requestData = {
        type: 'GET',
        url: url,
        success: handleResponse,
        error: handleError
    };
    $.ajax(requestData);
}

function setup() {
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
    const popoverId = popoverTriggerEl.attributes['data-content-id'];
    if (popoverId) {
        const contentEl = $(`#${popoverId.value}`).html();
        return new bootstrap.Popover(popoverTriggerEl, {
            content: contentEl,
            html: true,
        });
    }
});

      
}
function debouncedGetResults() {
    clearTimeout(timer);
    timer = setTimeout(getResults, 500);
}

function modifyDate(daysToAddOrSubtract) {
    // Get the current date string from the #currentDateDiv element
    const currentDateStr = $('#currentDateDiv').text();
    
    // Parse the date string to a Date object
    const currentDate = new Date(currentDateStr);

    // Modify the date by adding or subtracting days
    currentDate.setDate(currentDate.getDate() + daysToAddOrSubtract);

    // Format the modified date as a string in the desired format
    const year = currentDate.getFullYear();
    const month = String(currentDate.getMonth() + 1).padStart(2, '0');
    const day = String(currentDate.getDate()).padStart(2, '0');
    const hours = String(currentDate.getHours()).padStart(2, '0');
    const minutes = String(currentDate.getMinutes()).padStart(2, '0');
    const seconds = String(currentDate.getSeconds()).padStart(2, '0');
    const milliseconds = String(currentDate.getMilliseconds()).padStart(3, '0');
    const timezoneOffsetMinutes = -currentDate.getTimezoneOffset();
    const timezoneOffsetHours = Math.floor(timezoneOffsetMinutes / 60);
    const timezoneOffsetMinutesRemainder = Math.abs(timezoneOffsetMinutes % 60);
    const timezoneOffsetHoursStr = String(Math.abs(timezoneOffsetHours)).padStart(2, '0');
    const timezoneOffsetMinutesStr = String(timezoneOffsetMinutesRemainder).padStart(2, '0');
    const timezoneOffsetString = `${timezoneOffsetHours < 0 ? '-' : '+'}${timezoneOffsetHoursStr}:${timezoneOffsetMinutesStr}`;
    const modifiedDateStr = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}.${milliseconds}${timezoneOffsetString}`;

    // Update the #currentDateDiv element with the modified date
    $('#currentDateDiv').text(modifiedDateStr);

    // Perform the AJAX request with the modified date
    getResults();
}

function handleLeftArrowClick() {
    // Subtract a day from the current date
    modifyDate(-1);
}

// Function to handle right arrow click
function handleRightArrowClick() {
    // Add a day to the current date
    modifyDate(1);
}

$(document).ready(function() {
    getResults();
    $("input[name='mealtime_btnradio']").change(function() {
        var selectedMealtime = $(this).val();
    
    // "Disappear" all meal elements
        $(".meal").css("display", "none");
        
        // Show the selected meal elements
        $("." + selectedMealtime).css("display", "block");
    });

    const leftArrow = document.getElementById('leftArrow');
    const rightArrow = document.getElementById('rightArrow');

    // Add click event listeners
    leftArrow.addEventListener('click', function() {
        // Handle left arrow click
        console.log('Left arrow clicked');
        handleLeftArrowClick();
    });

    rightArrow.addEventListener('click', function() {
        // Handle right arrow click
        console.log('Right arrow clicked');
        handleRightArrowClick();
    });

    
    
    // getResults();
});
