/* Validation function for all calorie goal inputs.
The user is only allowed to type positive whole numbers (digits 0-9).
This function is used in welcome.html and settings.html. */

function isCalGoalValid(input) {
    var charCode = input.which || input.keyCode;

    // if the key is a valid number character
    if (charCode >= 48 && charCode <= 57)
        return true;

    return false;
}

/* Validation function for all serving size inputs.
The user is only allowed to type up to two decimal places. 
The user is also limited to numerical characters 
(digits 0-9) and the decimal point (.). This function is used in 
logmeals.html, editingplate.html, and custom_add.html. */

function isValid(input) {
    var charCode = input.which || input.keyCode;
    var value = input.target.value;

    // If the pressed key is a '-'
    if (charCode === 45)
        return false;

    // If the key is a decimal point and it already exists in the input,
    // or if the decimal point is at the end, return false
    if (charCode === 46 && (value.indexOf('.') !== -1 || value.endsWith('.')))
        return false;

    // if the key is a valid number or a decimal point
    if ((charCode >= 48 && charCode <= 57) || charCode === 46)
        return true;

    return false;
}

/* When the user submits the Calorie Goal form and all fields are valid, lock it.
This function is used to validate Calorie Goal inputs (settings.html) */

function closeForm() {
    // Obtain form elements
    var validFormElements = document.querySelector(":valid")
    var calorieInput = validFormElements.querySelector("#firstCalorieInput")
    var settingsButton = validFormElements.querySelector("#firstCalorieButton")

    // Check if the input was validated
    if (calorieInput != null) {
        // Remove any leading zeros
        var currentNumber = calorieInput.value;
        calorieInput.value = currentNumber.replace(/^0+/, '');

        // Round the number to a whole number
        var currentInt = parseInt(calorieInput.value);
        calorieInput.value = currentInt;

        // Disable the button but have it submit the form
        calorieInput.readOnly = true
        settingsButton.style.pointerEvents = "none"
        settingsButton.textContent = "Submitting..."
        settingsButton.style.opacity = "var(--bs-btn-disabled-opacity)"
        settingsButton.tabIndex = "-1"
        settingsButton.blur()
        linkPressed()
    }
}


