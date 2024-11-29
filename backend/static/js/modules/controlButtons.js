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

    // Function to show the modal
    function showStopOptionsModal() {
        const modal = document.getElementById('stop-options-modal');
        modal.style.display = 'block';

        // Add event listeners for modal buttons
        document.getElementById('save-audio-only').onclick = () => {
            handleStopAction('save_audio_only');
            modal.style.display = 'none';
        };

        document.getElementById('save-audio-transcribe').onclick = () => {
            handleStopAction('save_audio_and_transcribe');
            modal.style.display = 'none';
        };

        document.getElementById('delete-audio').onclick = () => {
            handleStopAction('delete_audio');
            modal.style.display = 'none';
        };
    }

    // Function to handle the selected action
    function handleStopAction(action) {
        console.log('Stop clicked with action:', action);

        fetch('/stop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ action }), // Pass the selected action
        })
            .then(response => {
                if (response.status === 204) {
                    // Action was delete_audio, no content expected
                    console.log('Recording deleted successfully.');
                    updateButtonStates(false, true, true); // Enable Start, disable Pause and Stop
                } else if (response.status === 201) {
                    // Action was save or save-and-transcribe, process JSON response
                    return response.json().then(data => {
                        console.log('Audio saved successfully.');
                        if (action === 'save_audio_and_transcribe') {
                            console.log('Transcription saved at:', data.transcription_path);
                        }
                        loadAudioFiles();
                        loadTranscriptionFiles();
                        updateButtonStates(false, true, true); // Enable Start, disable Pause and Stop
                    });
                } else if (response.status === 401) {
                    // User is not authenticated
                    alert('You are not authorized to perform this action.');
                } else {
                    // Handle other errors
                    console.error('Failed to perform action. Status:', response.status);
                    alert('An error occurred while stopping the recording. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An unexpected error occurred. Please try again.');
            });
    }

    // Attach modal trigger to the Stop button
    stopButton.addEventListener('click', () => {
        showStopOptionsModal();
    });

}