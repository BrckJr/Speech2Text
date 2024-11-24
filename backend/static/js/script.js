// Create a canvas and get the context
const canvas = document.querySelector('canvas');
const ctx = canvas.getContext('2d');

// Set canvas size to match window size
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

// SineWave class to handle each complex sine wave
class SineWave {
    constructor(baseY, amplitudeRange, frequencyRange, speed, color, harmonics) {
        this.baseY = baseY; // Base Y-coordinate (center of oscillation)
        this.amplitudeRange = amplitudeRange; // Range for amplitude variation
        this.frequencyRange = frequencyRange; // Range for frequency variation
        this.speed = speed; // Speed of wave motion
        this.color = color; // Color of the sine wave
        this.harmonics = harmonics; // Number of sine components in the wave
        this.components = this.generateComponents(); // Create harmonic components
    }

    // Generate harmonic components with random amplitudes, frequencies, and phases
    generateComponents() {
        const components = [];
        for (let i = 0; i < this.harmonics; i++) {
            const amplitude = Math.random() * (this.amplitudeRange.max - this.amplitudeRange.min) + this.amplitudeRange.min;
            const frequency = Math.random() * (this.frequencyRange.max - this.frequencyRange.min) + this.frequencyRange.min;
            const phase = Math.random() * Math.PI * 2; // Random phase offset
            components.push({ amplitude, frequency, phase });
        }
        return components;
    }

    draw(time) {
        ctx.beginPath();
        ctx.strokeStyle = `rgba(${this.color.r}, ${this.color.g}, ${this.color.b}, 0.8)`; // Wave color
        ctx.lineWidth = 1; // Thickness of the sine wave

        for (let x = 0; x <= canvas.width; x += 1) {
            let yOffset = 0;

            // Sum the contributions of all harmonic components
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

// Generate complex sine waves
const sineWaves = [];
const numWaves = 10; // Number of sine waves per group (bottom / top)
const waveGap = 50; // Vertical gap between waves
const speed = 0.3; // Speed of wave motion
const harmonics = 50; // Number of harmonic components per wave

function createComplexWaves() {
    /*
    const colors = [
        { r: 255, g: 200, b: 200 }, // Soft red
        { r: 200, g: 255, b: 200 }, // Soft green
        { r: 200, g: 200, b: 255 }, // Soft blue
    ];
    */

    // Top waves
    for (let w = 0; w < numWaves; w++) {
        const waveY = 70; // Top group starts near the top of the screen
        const amplitudeRange = { min: 1, max: 5 }; // Amplitude range for complexity
        const frequencyRange = { min: 0.05, max: 0.1 }; // Frequency range for complexity
        // const color = colors[w % colors.length]; // Cycle through colors
        const color = { r: 255, g: 255, b: 255 } // make all waves in white
        const direction = Math.random() > 0.5 ? 1 : -1; // Randomize wave direction
        sineWaves.push(new SineWave(waveY, amplitudeRange, frequencyRange, direction * speed * Math.random(), color, harmonics));
    }

    // Bottom waves
    for (let w = 0; w < numWaves; w++) {
        const waveY = canvas.height - 70; // Bottom group starts near the bottom of the screen
        const amplitudeRange = { min: 1, max: 5 }; // Amplitude range for complexity
        const frequencyRange = { min: 0.05, max: 0.1 }; // Frequency range for complexity
        // const color = colors[w % colors.length]; // Cycle through colors
        const color = { r: 255, g: 255, b: 255 } // make all waves in white
        const direction = Math.random() > 0.5 ? 1 : -1; // Randomize wave direction
        sineWaves.push(new SineWave(waveY, amplitudeRange, frequencyRange, direction * speed * Math.random(), color, harmonics));
    }
}

// Animation loop
function animate(time) {
    ctx.fillStyle = "rgba(0, 0, 0, 0.1)"; // Subtle trail effect
    ctx.fillRect(0, 0, canvas.width, canvas.height); // Clear canvas with transparency

    sineWaves.forEach(wave => {
        wave.draw(time * 0.01); // Update wave position
    });

    requestAnimationFrame(animate);
}

// Initialize sine waves and start animation
createComplexWaves();
animate(0);
