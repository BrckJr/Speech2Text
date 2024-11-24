// Create a canvas and get the context
const canvas = document.querySelector('canvas');
const ctx = canvas.getContext('2d');

// Set canvas size to match window size
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

// Particle class to represent each grain on the sine wave
class Particle {
    constructor(startX, baseY, amplitude, frequency, phaseOffset, speed, direction, color) {
        this.baseY = baseY; // Base Y-coordinate (center of oscillation)
        this.amplitude = amplitude; // Amplitude of the wave (vertical range)
        this.frequency = frequency; // Frequency of the wave
        this.phaseOffset = phaseOffset; // Phase offset for uniqueness
        this.speed = Math.random() * speed; // Speed of horizontal movement
        this.color = color; // Color of the particle
        this.size = Math.random() * 1.5 + 0.5; // Size of the particle
        this.alpha = Math.random() * 0.5 + 0.5; // Transparency
        this.x = startX; // Initial X-coordinate
        this.startX = startX; // Used to reset position when wrapping
        this.direction = direction; // Direction of the wave (+1 or -1)
    }

    draw() {
        ctx.beginPath();
        ctx.fillStyle = `rgba(${this.color.r}, ${this.color.g}, ${this.color.b}, ${this.alpha})`;
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2, false);
        ctx.fill();
    }

    update(time) {
        // Update the horizontal position (constant speed)
        this.x += this.speed;

        // Wrap around the canvas when the particle moves off-screen
        if (this.x > canvas.width) this.x = 0;
        if (this.x < 0) this.x = canvas.width;

        // Calculate oscillating Y position based on sine wave
        const oscillationY = Math.sin(this.frequency * (this.x + time) + this.phaseOffset) * this.amplitude;
        this.y = this.baseY + this.direction * oscillationY; // Apply the vertical oscillation
        this.draw();
    }
}

// Generate sine waves
const particles = [];
const numWaves = 5; // Number of sine waves per group
const particlesPerWave = 400; // Particles per sine wave
const waveAmplitude = 30; // Amplitude of each wave (vertical extent)
const waveFrequency = 0.01; // Frequency of oscillation
const waveGap = 20; // Vertical gap between waves
const waveSpeed = 0.1; // Speed of particles moving along the sine wave

function createWaveParticles() {
    const colors = [
        { r: 255, g: 200, b: 200 }, // Soft red
        { r: 200, g: 255, b: 200 }, // Soft green
        { r: 200, g: 200, b: 255 }, // Soft blue
    ];

    // Create top waves
    for (let w = 0; w < numWaves; w++) {
        const waveY = waveGap * w + 50; // Top group starts near the top of the screen
        const direction = Math.random() > 0.5 ? 1 : -1; // Randomize wave direction
        const color = colors[w % colors.length]; // Cycle through colors

        for (let i = 0; i < particlesPerWave; i++) {
            const startX = (canvas.width / particlesPerWave) * i; // Distribute particles horizontally
            const phaseOffset = Math.random() * Math.PI * 2; // Randomize phase offset
            const speed = waveSpeed * (Math.random() * 0.5 + 0.5); // Slight variation in speed
            particles.push(new Particle(startX, waveY, waveAmplitude, waveFrequency, phaseOffset, speed, direction, color));
        }
    }

    // Create bottom waves
    for (let w = 0; w < numWaves; w++) {
        const waveY = canvas.height - waveGap * w - 50; // Bottom group starts near the bottom of the screen
        const direction = Math.random() > 0.5 ? 1 : -1; // Randomize wave direction
        const color = colors[w % colors.length]; // Cycle through colors

        for (let i = 0; i < particlesPerWave; i++) {
            const startX = (canvas.width / particlesPerWave) * i; // Distribute particles horizontally
            const phaseOffset = Math.random() * Math.PI * 2; // Randomize phase offset
            const speed = waveSpeed * (Math.random() * 0.5 + 0.5); // Slight variation in speed
            particles.push(new Particle(startX, waveY, waveAmplitude, waveFrequency, phaseOffset, speed, direction, color));
        }
    }
}

// Animation loop
function animate(time) {
    ctx.fillStyle = "rgba(0, 0, 0, 0.1)"; // Subtle trail effect
    ctx.fillRect(0, 0, canvas.width, canvas.height); // Clear canvas with transparency

    particles.forEach(particle => {
        particle.update(time * 0.01); // Update particle position
    });

    requestAnimationFrame(animate);
}

// Initialize particles and start animation
createWaveParticles();
animate(0);
