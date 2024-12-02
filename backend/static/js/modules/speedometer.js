//Change this Value to set the percentage
let totalRot = ((90 / 100) * 180 * Math.PI) / 180;

let rotation = 0;
let doAnim = true;
let canvas = null;
let ctx = null;
let text = document.querySelector(".text_wpm_speedo");
canvas = document.getElementById("canvas_wpm_speedo");
ctx = canvas.getContext("2d");
setTimeout(requestAnimationFrame(animateSpeedometer), 1500);

function calcPointsCirc(cx, cy, rad, dashLength){
    var n = rad / dashLength,
    alpha = (Math.PI * 2) / n,
    pointObj = {},
    points = [],
    i = -1;

    while (i < n) {
        var theta = alpha * i,
        theta2 = alpha * (i + 1);

        points.push({
            x: Math.cos(theta) * rad + cx,
            y: Math.sin(theta) * rad + cy,
            ex: Math.cos(theta2) * rad + cx,
            ey: Math.sin(theta2) * rad + cy
        });
        i += 2;
    }
    return points;
}

export function animateSpeedometer() {
    //Clearing animation on every iteration
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Make center of the circle
    const center = {
        x: 175,
        y: 175
    };

    // Determine arc color based on rotation
    const isRed = rotation >= 0.75 * Math.PI;
    const arcColor = isRed ? "#B22222" : "#008000"; // Red or Green

    // Main arc
    ctx.beginPath();
    ctx.strokeStyle = arcColor; // Use determined arc color
    ctx.lineWidth = 3;
    ctx.arc(center.x, center.y, 174, Math.PI, Math.PI + Math.PI);
    ctx.stroke();

    // Function to draw dotted lines with color based on arc percentage
    const DrawDottedLine = (x1, y1, x2, y2, dotRadius, dotCount) => {
        const dx = x2 - x1;
        const dy = y2 - y1;
        const slopeOfLine = dy / dx;

        // Calculate angle of the line
        let degOfLine =
            Math.atan(slopeOfLine) * (180 / Math.PI) > 0
                ? Math.atan(slopeOfLine) * (180 / Math.PI)
                : 180 + Math.atan(slopeOfLine) * (180 / Math.PI);

        // Determine the angle of the needle
        let degOfNeedle = rotation * (180 / Math.PI);

        // Determine dot color based on the threshold
        let dotColor;
        if (degOfLine >= 0.75 * 180) {
            dotColor = degOfLine <= degOfNeedle ? "#B22222" : "#f1f1f1"; // Red for dots after 75%
        } else {
            dotColor = degOfLine <= degOfNeedle ? "#008000" : "#f1f1f1"; // Green for below 75%, light green for past the needle
        }

        // Calculate space between the dots
        const spaceX = dx / (dotCount - 1);
        const spaceY = dy / (dotCount - 1);

        // Draw each dot
        let newX = x1;
        let newY = y1;
        for (let i = 0; i < dotCount; i++) {
            // Gradually reduce the size of the dot
            dotRadius = dotRadius >= 0.75 ? dotRadius - i * (0.5 / 15) : dotRadius;
            drawDot(newX, newY, dotRadius, `${dotColor}${100 - (i + 1)}`);
            newX += spaceX;
            newY += spaceY;
        }
    };
    const drawDot = (x, y, dotRadius, dotColor) => {
        ctx.beginPath();
        ctx.arc(x, y, dotRadius, 0, 2 * Math.PI, false);
        ctx.fillStyle = dotColor;
        ctx.fill();
    };
    let firstDottedLineDots = calcPointsCirc(center.x, center.y, 165, 1);
    for (let k = 0; k < firstDottedLineDots.length; k++) {
        let x = firstDottedLineDots[k].x;
        let y = firstDottedLineDots[k].y;
        DrawDottedLine(x, y, 175, 175, 2.5, 25, "#008000");
    }


    //dummy circle to hide the line connecting to center
    ctx.beginPath();
    ctx.arc(center.x, center.y, 60, 2 * Math.PI, 0);
    ctx.fillStyle = "#333333";
    ctx.fill();

    //Speedometer triangle
    var x = -75,
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
    text.innerHTML = 50 + Math.round((rotation / Math.PI) * 200) + " wpm";
    requestAnimationFrame(animateSpeedometer);

}