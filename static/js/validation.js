// Validation functions for all inputs: Serving sizes and calorie goals
// Used in logmeals.html, settings.html, welcome.html

// Validate the serving size inputs, limiting to positive numbers only
// and only up to 2 decimal places 
function isValid(input) {
    var charCode = input.which || input.keyCode;
    var value = input.target.value;

    // If the pressed key is a '-'
    if (input.charCode === 45)
        return false;

    // If the key contains nonvalid chars 
    if (input.charCode < 48 || input.charCode > 57)
        return false;

    // Limit input to 2 decimal places
    if (value.indexOf('.') !== -1 && value.length - value.indexOf('.') > 2)
        return false;

    return true;
}

