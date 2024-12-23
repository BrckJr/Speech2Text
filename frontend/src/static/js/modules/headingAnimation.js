export function setupHeadingAnimation(element, text, speed = 150) {
    let index = 0;

    function typeEffect() {
        if (index < text.length) {
            element.textContent += text.charAt(index);
            index++;
            setTimeout(typeEffect, speed);
        } else {
            // Remove the blinking caret once typing is finished
            element.style.borderRight = "none";
        }
    }

    // Add the caret style
    element.style.borderRight = "2px solid black";
    element.style.animation = "blink-caret 0.6s step-end infinite";

    // Start the typing effect
    typeEffect();
}
