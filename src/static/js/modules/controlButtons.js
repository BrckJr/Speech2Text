import { loadFileList } from './FileLoader.js';
import { setAnalytics } from './getAnalytics.js'

// Function to set up control buttons (Start, Pause, Stop) with event listeners
export function setupControlButtons(startButton, pauseButton, stopButton, audioFileDropdown) {

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
        // Send POST request to server to start the process
        fetch('/start', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                // console.log(data.message);  // Log server response message
                updateButtonStates(true, false, false); // Disable Start, enable Pause and Stop
            })
            .catch(error => console.error('Error:', error)); // Handle any errors
    });

    // Event listener for Pause button: Pauses the ongoing process
    pauseButton.addEventListener('click', () => {
        // Send POST request to server to pause the process
        fetch('/pause', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                // console.log(data.message);  // Log server response message
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

        document.getElementById('delete-audio').onclick = () => {
            handleStopAction('delete_audio');  // Delete audio
            modal.style.display = 'none'; // Close the modal
        };
    }

    function handleStopAction(action) {
        const filename = document.getElementById('filename') ? document.getElementById('filename').value.trim() : '';

        if (action === 'save_audio_and_analyze' && !filename) {
            alert('Please enter a valid filename.');
            return;
        }

        // Show loading overlay
        showLoadingOverlay();

        // Send POST request to stop the process and perform the selected action
        fetch('/stop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ action, filename }),
        })
            .then(response => {
                hideLoadingOverlay(); // Hide overlay after response is received

                if (response.status === 204) {
                    updateButtonStates(false, true, true); // Enable Start, disable Pause and Stop
                } else if (response.status === 201) {
                    return response.json().then(async data => {
                        await loadFileList();
                        updateButtonStates(false, true, true);

                        if (action === 'save_audio_and_analyze') {
                            if (data.dropdown_value && audioFileDropdown) {
                                audioFileDropdown.value = data.dropdown_value;
                            }
                            await setAnalytics();
                        }
                    });
                } else if (response.status === 401) {
                    alert('You are not authorized to perform this action.');
                } else {
                    console.error('Failed to perform action. Status:', response.status);
                    alert('An error occurred while stopping the recording. Please try again.');
                }
            })
            .catch(error => {
                hideLoadingOverlay(); // Hide overlay even if there's an error
                console.error('Error:', error);
                alert('An unexpected error occurred. Please try again.');
            });
    }

    function showLoadingOverlay() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = 'flex'; // Show overlay
    }

    function hideLoadingOverlay() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = 'none'; // Hide overlay
    }

    // Attach modal trigger to Stop button
    stopButton.addEventListener('click', async () => {
        // Before showing Modal, pause the recording
        await fetch('/pause', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                // console.log(data.message);  // Log server response message
                updateButtonStates(true, true, true); // Enable Start and Stop, disable Pause
            })
            .catch(error => console.error('Error:', error)); // Handle any errors


        showStopOptionsModal();  // Show stop options modal when Stop is clicked
    });
}