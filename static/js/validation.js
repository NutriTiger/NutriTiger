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

