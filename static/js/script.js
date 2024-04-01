'use strict';

function handleResponse(data) {
    $('#dhallMenusDiv').html(data);
    // After adding dynamic content to the DOM, call the setup function
    setup();
}

function handleError() {
    alert('Error: Failed to fetch data from server');
}

function getResults() {
    let mealtime = $("input[name='mealtime_btnradio']:checked").val();
    console.log(mealtime);
    let encoded_mealtime = encodeURIComponent(mealtime);
    let url = '/update-menus-mealtime?mealtime=' + encoded_mealtime;
    let requestData = {
        type: 'GET',
        url: url,
        success: handleResponse,
        error: handleError
    };
    $.ajax(requestData);
}

function setup() {
    // Initialize popovers for dynamically generated content
    /*const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    const popover = new bootstrap.Popover('.popover-dismiss', {
        trigger: 'focus'
      })*/
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
    const popoverId = popoverTriggerEl.attributes['data-content-id'];
    if (popoverId) {
        const contentEl = $(`#${popoverId.value}`).html();
        return new bootstrap.Popover(popoverTriggerEl, {
            content: contentEl,
            html: true,
        });
    } else { // do something else cause data-content-id isn't there.
    }
});

      
}



$(document).ready(function() {
    getResults();
    $("input[name='mealtime_btnradio']").change(function() {
        getResults();
    });
});
