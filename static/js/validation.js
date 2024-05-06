// Validation functions for all inputs: Serving sizes and calorie goals
// Used in logmeals.html, settings.html, welcome.html

// Validate the serving size inputs, limiting to positive numbers only
// and only up to 2 decimal places 
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

    // limit input to 2 decimal places
    var decimalIndex = value.indexOf('.');
    if (decimalIndex !== -1 && value.length - decimalIndex > 2)
        return false;

    // if the key is a valid number or a decimal point
    if ((charCode >= 48 && charCode <= 57) || charCode === 46)
        return true;

    return false;
}

// When the user submits the form and all fields are valid, lock it
// Used to validate Calorie Goal inputs (settings.html)
function closeForm() {
    // Obtain form elements
    // var validFormElements = document.querySelector(":valid")
    // cc
    var validFormElements = document.querySelector(":valid")
    var calorieInput = validFormElements.querySelector("#firstCalorieInput")
    var settingsButton = validFormElements.querySelector("#firstCalorieButton")

    // Check if the input was validated
    if (calorieInput != null) {
        // Remove any leading zeros
        var currentNumber = calorieInput.value;
        calorieInput.value = currentNumber.replace(/^0+/, '');

        // Round the number to two decimal places
        var currentFloat = parseFloat(calorieInput.value);

        if (!isNaN(currentFloat)) {
            // If it's not NaN, round the float to two decimal places and update the input value
            calorieInput.value = currentFloat.toFixed(2);
        }

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


