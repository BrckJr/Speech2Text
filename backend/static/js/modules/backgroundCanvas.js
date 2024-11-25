// backgroundCanvas.js

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
        return components;
    }

    draw(ctx, canvas, time) {
        ctx.beginPath();
        ctx.strokeStyle = `rgba(${this.color.r}, ${this.color.g}, ${this.color.b}, 0.3)`; // Wave color
        ctx.lineWidth = 1; // Thickness of the wave

        for (let x = 0; x <= canvas.width; x += 1) {
            let yOffset = 0;

            // Sum contributions of harmonic components
            this.components.forEach(component => {
                yOffset += component.amplitude * Math.sin(component.frequency * (x + time * this.speed) + component.phase);
            });

            const y = this.baseY + yOffset; // Combine base Y and offset
            if (x === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        }

        ctx.stroke();
    }
}

export function setupCanvas() {
    const canvas = document.querySelector('#backgroundCanvas');
    const ctx = canvas.getContext('2d');

    // Set canvas size to match window size
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Create a single complex wave
    const wave = new ComplexWave(
        canvas.height / 2, // Center vertically
        { min: 5, max: 30 }, // Amplitude range
        { min: 0.1, max: 0.7 }, // Frequency range
        0.1, // Slow speed
        { r: 255, g: 255, b: 255 }, // White color
        100 // High number of harmonics for complexity
    );

    // Animation loop
    function animate(time) {
        ctx.fillStyle = "rgba(0, 0, 0, 0.2)"; // Subtle trail effect
        ctx.fillRect(0, 0, canvas.width, canvas.height); // Clear canvas with transparency

        wave.draw(ctx, canvas, time * 0.01); // Draw the wave with slow horizontal motion

        requestAnimationFrame(animate);
    }

    // Start animation
    animate(0);

    // Adjust canvas size on window resize
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        wave.baseY = canvas.height / 2; // Update wave center
    });
}
