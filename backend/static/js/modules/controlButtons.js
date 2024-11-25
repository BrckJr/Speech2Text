// controlButtons.js

import { loadAudioFiles } from './audioFileLoader.js';
import { loadTranscriptionFiles } from './transcriptionFileLoader.js';

export function setupControlButtons(startButton, pauseButton, stopButton) {
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
}
