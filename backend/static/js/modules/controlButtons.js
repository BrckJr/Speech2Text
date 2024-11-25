import { loadAudioFiles } from './audioFileLoader.js';
import { loadTranscriptionFiles } from './transcriptionFileLoader.js';

export function setupControlButtons(startButton, pauseButton, stopButton) {
    // Helper function to update button states and styles
    const updateButtonStates = (startState, pauseState, stopState) => {
        startButton.disabled = startState;
        pauseButton.disabled = pauseState;
        stopButton.disabled = stopState;

        // Optional: Reset the inline background color to let CSS handle it
        startButton.style.background = '';
        pauseButton.style.background = '';
        stopButton.style.background = '';
    };

    // Event listener for Start button
    startButton.addEventListener('click', () => {
        console.log('Start clicked');
        fetch('/start', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                updateButtonStates(true, false, false); // Disable Start, enable Pause and Stop
            })
            .catch(error => console.error('Error:', error));
    });

    // Event listener for Pause button
    pauseButton.addEventListener('click', () => {
        console.log('Pause clicked');
        fetch('/pause', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                updateButtonStates(false, true, false); // Enable Start and Stop, disable Pause
            })
            .catch(error => console.error('Error:', error));
    });

    // Event listener for Stop button
    stopButton.addEventListener('click', () => {
        console.log('Stop clicked');

        const userConfirmed = confirm('Do you want to transcribe the recorded audio file?');

        fetch('/stop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ transcribe: userConfirmed }), // Pass the user's choice
        })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                updateButtonStates(false, true, true); // Enable Start, disable Pause and Stop
                loadAudioFiles();
                loadTranscriptionFiles();
            })
            .catch(error => console.error('Error:', error));
    });
}