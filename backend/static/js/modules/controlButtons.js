import { loadAudioFiles } from './audioFileLoader.js';
import { loadTranscriptionFiles } from './transcriptionFileLoader.js';
import { setAnalytics } from './getAnalytics.js'

// Function to set up control buttons (Start, Pause, Stop) with event listeners
export function setupControlButtons(startButton, pauseButton, stopButton, recordingsDropdown) {

    // Helper function to update button states (enable/disable)
    const updateButtonStates = (startState, pauseState, stopState) => {
        startButton.disabled = startState;  // Enable/Disable Start button
        pauseButton.disabled = pauseState;  // Enable/Disable Pause button
        stopButton.disabled = stopState;    // Enable/Disable Stop button

        // Optional: Reset inline background color to let CSS handle it
        startButton.style.background = '';
        pauseButton.style.background = '';
        stopButton.style.background = '';
    };

    // Event listener for Start button: Starts the recording or process
    startButton.addEventListener('click', () => {
        console.log('Start clicked');

        // Send POST request to server to start the process
        fetch('/start', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);  // Log server response message
                updateButtonStates(true, false, false); // Disable Start, enable Pause and Stop
            })
            .catch(error => console.error('Error:', error)); // Handle any errors
    });

    // Event listener for Pause button: Pauses the ongoing process
    pauseButton.addEventListener('click', () => {
        console.log('Pause clicked');

        // Send POST request to server to pause the process
        fetch('/pause', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);  // Log server response message
                updateButtonStates(false, true, false); // Enable Start and Stop, disable Pause
            })
            .catch(error => console.error('Error:', error)); // Handle any errors
    });

    // Function to show modal with stop options (e.g., save or delete)
    function showStopOptionsModal() {
        const modal = document.getElementById('stop-options-modal');
        modal.style.display = 'block'; // Show the modal

        // Add event listeners for modal buttons to handle the selected stop action
        document.getElementById('save-audio-analyze').onclick = () => {
            handleStopAction('save_audio_and_analyze');  // Save audio only
            modal.style.display = 'none'; // Close the modal
        };

        /*
        document.getElementById('save-audio-transcribe').onclick = () => {
            handleStopAction('save_audio_and_transcribe');  // Save audio and transcription
            modal.style.display = 'none'; // Close the modal
        };
        */

        document.getElementById('delete-audio').onclick = () => {
            handleStopAction('delete_audio');  // Delete audio
            modal.style.display = 'none'; // Close the modal
        };
    }

    // Function to handle the selected stop action (save or delete)
    function handleStopAction(action) {
        console.log('Stop clicked with action:', action);

        // Send POST request to stop the process and perform the selected action
        fetch('/stop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ action }), // Send selected action as JSON body
        })
            .then(response => {
                if (response.status === 204) {
                    // Action was 'delete_audio', no content expected from server
                    console.log('Audio discarded successfully.');
                    updateButtonStates(false, true, true); // Enable Start, disable Pause and Stop
                } else if (response.status === 201) {
                    // Action was 'save_audio_and_analyse
                    return response.json().then(async data => {
                        console.log('Audio and Transcription saved successfully.');

                        // Refresh the audio files list and wait until it is finished to be able to
                        // select the value in the 'save_audio_and_analyze' action
                        await loadAudioFiles();
                        await loadTranscriptionFiles();

                        updateButtonStates(false, true, true); // Enable Start, disable Pause and Stop000);

                        // If save-audio-analyze is selected, trigger the update of the analytics section
                        // by setting the dropdown value and triggering the setAnalytics() from getAnalytics.js
                        if (action === 'save_audio_and_analyze') {
                            // If the response carries the dropdown_value, set the dropdown value
                            if (data.dropdown_value) {
                                if (recordingsDropdown) {
                                    recordingsDropdown.value = data.dropdown_value; // Set the dropdown value
                                    await setAnalytics()
                                }
                            }
                            console.log('Analysis done successfully.');
                        }
                    });
                } else if (response.status === 401) {
                    // Handle case when user is not authenticated
                    alert('You are not authorized to perform this action.');
                } else {
                    // Handle any other error responses
                    console.error('Failed to perform action. Status:', response.status);
                    alert('An error occurred while stopping the recording. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An unexpected error occurred. Please try again.');
            });
    }

    // Attach modal trigger to Stop button
    stopButton.addEventListener('click', () => {
        showStopOptionsModal();  // Show stop options modal when Stop is clicked
    });
}