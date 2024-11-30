// Class to represent a complex wave with multiple harmonic components
export class ComplexWave {
    constructor(baseY, amplitudeRange, frequencyRange, speed, color, harmonics) {
        this.baseY = baseY; // Base Y-coordinate (center of the wave)
        this.amplitudeRange = amplitudeRange; // Range for amplitude variation
        this.frequencyRange = frequencyRange; // Range for frequency variation
        this.speed = speed; // Speed of horizontal motion
        this.color = color; // Color of the wave
        this.harmonics = harmonics; // Number of sine components in the wave
        this.components = this.generateComponents(); // Generate harmonic components
    }

    // Generate harmonic components with random parameters
    generateComponents() {
        const components = [];
        for (let i = 0; i < this.harmonics; i++) {
            const amplitude =
                Math.random() * (this.amplitudeRange.max - this.amplitudeRange.min) + this.amplitudeRange.min;
            const frequency =
                Math.random() * (this.frequencyRange.max - this.frequencyRange.min) + this.frequencyRange.min;
            const phase = Math.random() * Math.PI * 2; // Random phase offset
            components.push({ amplitude, frequency, phase });
        }
        return components; // Return array of components
    }

    // Draw the wave on the canvas
    draw(ctx, canvas, time) {
        ctx.beginPath();
        ctx.strokeStyle = `rgba(${this.color.r}, ${this.color.g}, ${this.color.b}, 0.3)`; // Wave color with transparency
        ctx.lineWidth = 1; // Thickness of the wave

        // Loop through x coordinates to draw the wave
        for (let x = 0; x <= canvas.width; x += 1) {
            let yOffset = 0;

            // Sum the contributions of each harmonic component
            this.components.forEach(component => {
                yOffset += component.amplitude * Math.sin(component.frequency * (x + time * this.speed) + component.phase);
            });

            const y = this.baseY + yOffset; // Final Y position for the wave
            if (x === 0) {
                ctx.moveTo(x, y); // Move to the starting point
            } else {
                ctx.lineTo(x, y); // Draw a line to the next point
            }
        }

        ctx.stroke(); // Render the path on the canvas
    }
}

// Function to setup and animate the background canvas
export function setupCanvas() {
    const canvas = document.querySelector('#backgroundCanvas');
    if (!canvas) return; // Exit if canvas element is not found

    const ctx = canvas.getContext('2d'); // Get the 2D context for drawing

    // Set canvas size to match window size
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Create a new complex wave
    const wave = new ComplexWave(
        canvas.height / 2, // Center the wave vertically
        { min: 5, max: 30 }, // Amplitude range
        { min: 0.1, max: 0.45 }, // Frequency range
        0.7, // Speed of the wave
        { r: 255, g: 255, b: 255 }, // Color of the wave (white)
        100 // Number of harmonics
    );

    // Animation loop
    function animate(time) {
        ctx.fillStyle = "rgba(0, 0, 0, 0.2)"; // Set the background with a subtle trail effect
        ctx.fillRect(0, 0, canvas.width, canvas.height); // Clear the canvas with semi-transparency

        wave.draw(ctx, canvas, time * 0.01); // Draw the wave, adjusting for time

        requestAnimationFrame(animate); // Request the next frame for animation
    }

    animate(0); // Start the animation loop

    // Adjust the canvas size when the window is resized
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth; // Update canvas width
        canvas.height = window.innerHeight; // Update canvas height
        wave.baseY = canvas.height / 2; // Re-center the wave vertically
    });
}