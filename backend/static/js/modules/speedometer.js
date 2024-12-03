// Set the radius you want to use
let radius = 150; // You can change this value to any desired radius

// Change this Value to set the percentage
let totalRot = ((90 / 100) * 180 * Math.PI) / 180;

let rotation = 0;
let text = document.querySelector(".text_wpm_speedo");

export function animateSpeedometer() {
    const canvas = document.getElementById("canvas_wpm_speedo");
    const ctx = canvas.getContext("2d");
    // Clearing animation on every iteration
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Make center of the circle
    const center = {
        x: canvas.width/2,
        y: canvas.height
    };

    // Main arc (background arc) - This is the full circle behind the progress sections
    ctx.beginPath();
    ctx.strokeStyle = "#f1f1f1"; // light gray color for the background
    ctx.lineWidth = 1;
    ctx.arc(center.x, center.y, radius, Math.PI, Math.PI + Math.PI); // Use radius here
    ctx.stroke();

    // Function to draw full colored sections based on rotation
    const drawProgressArc = (startAngle, endAngle, color) => {
        ctx.beginPath();
        ctx.arc(center.x, center.y, radius, startAngle, endAngle); // Use radius here
        ctx.lineWidth = 8; // Make the arc thicker
        ctx.strokeStyle = color;
        ctx.stroke();
    };

    // Function to draw filled colored sector
    const drawProgressSector = (startAngle, endAngle, color) => {
        ctx.beginPath();
        ctx.moveTo(center.x, center.y); // Move to center
        ctx.arc(center.x, center.y, radius, startAngle, endAngle); // Use radius here
        ctx.fillStyle = color; // Set fill color
        ctx.fill(); // Fill the sector
    };

    // Draw the progress based on rotation
    const greenArcEndAngle = Math.PI + rotation; // For green section (rotation-based)
    const redArcStartAngle = Math.PI + rotation; // For red section (if any)
    const redArcEndAngle = Math.PI + Math.PI; // Full 180 degrees
    const threeQuarterAngle = Math.PI + 0.75 * Math.PI;

    // Draw the green section (if there's any rotation)
    drawProgressArc(Math.PI, greenArcEndAngle, "rgba(0, 128, 0)");
    drawProgressSector(redArcEndAngle, redArcStartAngle, "rgba(0, 128, 0, 0.3)")

    // Draw the red section if rotation exceeds 75% of the range
    if (rotation > 0.75 * Math.PI) {
        drawProgressArc(threeQuarterAngle, redArcEndAngle, "rgba(178, 34, 34)");
        drawProgressSector(threeQuarterAngle, redArcStartAngle, "rgba(178, 34, 34, 0.5)")
    }

    // Dummy circle to hide the line connecting to center
    ctx.beginPath();
    ctx.arc(center.x, center.y, 70, 0, 2 * Math.PI);
    ctx.fillStyle = "#333333";
    ctx.fill();

    // Speedometer triangle
    var x = -68,
    y = 0;
    ctx.save();
    ctx.beginPath();
    ctx.translate(175, 175);
    ctx.rotate(rotation);
    ctx.moveTo(x, y);
    ctx.lineTo(x + 10, y - 10);
    ctx.lineTo(x + 10, y + 10);
    ctx.closePath();
    ctx.fillStyle = rotation >= 0.75 * Math.PI ? "#B22222" : "#008000";
    ctx.fill();
    ctx.restore();

    // To slow down the simulation, increase the divisor
    if (rotation < totalRot) {
        rotation += (Math.PI) / 360;
        if (rotation > totalRot) {
            rotation -= (Math.PI) / 360;
        }
    }

    // Words per minute range: 50 - 250 wpm
    text.innerHTML = 50 + Math.round((rotation / Math.PI) * 200) + "";
    requestAnimationFrame(animateSpeedometer);
}
