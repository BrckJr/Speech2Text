// Get button elements
const startButton = document.getElementById('start');
const pauseButton = document.getElementById('pause');
const stopButton = document.getElementById('stop');
const deleteButton = document.querySelector('.delete-btn');

// Function to load audio file paths from the database
// Function to load audio files from the server
async function loadAudioFiles() {
    try {
        const response = await fetch('/list-audio-files');
        const data = await response.json();

        if (data.error) {
            console.error(data.error);
            return;
        }

        const fileList = document.querySelector('#raw-audio-files .file-list');
        fileList.innerHTML = ''; // Clear existing content

        // Loop through the list of audio file paths and create links
        data.files.forEach(filePath => {
            const listItem = document.createElement('div');
            listItem.className = 'file-item';

            // Create a clickable link for each audio file
            const fileLink = document.createElement('a');
            fileLink.href = `/static/${filePath}`;  // Use relative path to static folder
            fileLink.textContent = filePath.split('/').pop();  // Display only the file name
            fileLink.target = '_blank';  // Open in a new tab

            // Append the link to the list item
            listItem.appendChild(fileLink);
            fileList.appendChild(listItem);
        });
    } catch (err) {
        console.error('Error loading audio files:', err);
    }
}


// Function to load transcription files from the server
// Function to load transcription files from the server
async function loadTranscriptionFiles() {
    try {
        const response = await fetch('/list-transcription-files');
        const data = await response.json();

        if (data.error) {
            console.error(data.error);
            return;
        }

        const fileList = document.querySelector('#transcribed-files .file-list');
        fileList.innerHTML = ''; // Clear existing content

        // Loop through the list of transcription file paths and create links
        data.files.forEach(filePath => {
            const listItem = document.createElement('div');
            listItem.className = 'file-item';

            // Create a clickable link for each transcription file
            const fileLink = document.createElement('a');
            fileLink.href = `/static/${filePath}`;  // Use relative path to static folder
            fileLink.textContent = filePath.split('/').pop();  // Display only the file name
            fileLink.target = '_blank';  // Open in a new tab

            // Append the link to the list item
            listItem.appendChild(fileLink);
            fileList.appendChild(listItem);
        });
    } catch (err) {
        console.error('Error loading transcription files:', err);
    }
}

// Load audio files on page load
document.addEventListener('DOMContentLoaded', loadAudioFiles);

// Load transcription files on page load
document.addEventListener('DOMContentLoaded', loadTranscriptionFiles);

// Event listener for Start button
startButton.addEventListener('click', () => {
    console.log('Start clicked');
    // Send request to the backend to start recording
    fetch('/start', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
            startButton.disabled = true;
            pauseButton.disabled = false;
            stopButton.disabled = false;
        })
        .catch(error => console.error('Error:', error));
});

// Event listener for Pause button
pauseButton.addEventListener('click', () => {
    console.log('Pause clicked');
    // Send request to the backend to pause recording
    fetch('/pause', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
        })
        .catch(error => console.error('Error:', error));
});

// Event listener for Stop button
stopButton.addEventListener('click', () => {
    console.log('Stop clicked');

    // Check if the user wants a transcription of the recording
    const userConfirmed = confirm("Do you want to transcribe the recorded audio file?");

    // Send request to the backend to stop recording
    fetch('/stop', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ transcribe: userConfirmed }) // Pass the user's choice
    })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);

            // Disable the buttons as needed
            startButton.disabled = false;
            pauseButton.disabled = true;
            stopButton.disabled = true;

            // Refresh the file lists
            loadAudioFiles();
            loadTranscriptionFiles();
        })
        .catch(error => console.error('Error:', error));
});

// Event listener for Delete button
deleteButton.addEventListener('click', () => {
    console.log('Delete all files clicked');
    // Display the confirmation prompt
    const userConfirmed = confirm("Are you sure you want to delete all files? This action cannot be undone.");

    if (userConfirmed) {
        // If confirmed, send an AJAX request to the backend to delete the files
        fetch('/delete-all-files', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ action: 'delete' })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('All files deleted successfully!');
                location.reload(); // Reload the page to reflect the changes
            } else {
                alert('Failed to delete files. Please try again later.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again later.');
        });
    } else {
        // If not confirmed, do nothing
        console.log("File deletion cancelled.");
    }
});

/*
* THIS SECTION IS TO PROVIDE A DYNAMIC BACKGROUND IMAGE
*/


// Create a canvas and get the context
const canvas = document.querySelector('canvas');
const ctx = canvas.getContext('2d');

// Set canvas size to match window size
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

// Single complex wave class
class ComplexWave {
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
            const amplitude = Math.random() * (this.amplitudeRange.max - this.amplitudeRange.min) + this.amplitudeRange.min;
            const frequency = Math.random() * (this.frequencyRange.max - this.frequencyRange.min) + this.frequencyRange.min;
            const phase = Math.random() * Math.PI * 2; // Random phase offset
            components.push({ amplitude, frequency, phase });
        }
        return components;
    }

    draw(time) {
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

    wave.draw(time * 0.01); // Draw the wave with slow horizontal motion

    requestAnimationFrame(animate);
}

// Start animation
animate(0);
