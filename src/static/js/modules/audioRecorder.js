// Module for managing frontend audio recording
import { loadFileList } from './FileLoader.js';
import { setAnalytics } from './getAnalytics.js';

export function setupAudioRecording(startButton, pauseButton, stopButton, audioFileDropdown) {
    let mediaRecorder; // MediaRecorder instance for managing audio recording
    let audioChunks = []; // Array to store recorded audio data

    // Helper function to start recording
    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);

            // Event listener to store audio data chunks
            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            // Start recording
            mediaRecorder.start();
        } catch (error) {
            console.error('Error accessing microphone:', error);
            alert('Unable to access microphone. Please check your device settings.');
        }
    };

    // Helper function to pause recording
    const pauseRecording = () => {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.pause();
        }
    };

    // Helper function to stop recording and handle actions via modal
    const stopRecording = () => {
        if (mediaRecorder && (mediaRecorder.state === 'recording' || mediaRecorder.state === 'paused')) {
            mediaRecorder.stop();

            mediaRecorder.onstop = () => {
                // Combine audio chunks into a single Blob
                const audioBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType });

                // Show modal for user to choose save or discard
                showStopOptionsModal(audioBlob);

                // Reset audioChunks for the next recording session
                audioChunks = [];
            };
        }
    };

    // Function to show modal with stop options (e.g., save or delete)
    function showStopOptionsModal(audioBlob) {
        const modal = document.getElementById('stop-options-modal');
        modal.style.display = 'block'; // Show the modal

        // Add event listeners for modal buttons to handle the selected stop action
        document.getElementById('save-audio-analyze').onclick = () => {
            const filename = document.getElementById('filename') ? document.getElementById('filename').value.trim() : '';

            if (!filename) {
                alert('Please enter a valid filename.');
                return;
            }

            handleStopAction('save_audio_and_analyze', audioBlob, filename); // Save audio only
            modal.style.display = 'none'; // Close the modal
        };

        document.getElementById('delete-audio').onclick = () => {
            handleStopAction('delete_audio'); // Discard audio
            modal.style.display = 'none'; // Close the modal
        };
    }

    function handleStopAction(action, audioBlob = null, filename = '') {
        showLoadingOverlay(); // Show loading overlay

        if (action === 'save_audio_and_analyze' && audioBlob) {
            // Send audio Blob to the backend
            const formData = new FormData();
            formData.append('audio', audioBlob, filename); // Send original format

            fetch('/store_and_analyze', {
                method: 'POST',
                body: formData,
            })
                .then(response => {
                    hideLoadingOverlay(); // Hide overlay after response

                    if (response.ok) {
                        return response.json().then(async data => {
                            await loadFileList();

                            // Set the new dropdown value to be able to call analytics on new recording
                            if (data.dropdown_value && audioFileDropdown) {
                                audioFileDropdown.value = data.dropdown_value;
                            }
                            await setAnalytics();

                        });
                    } else if (response.status === 404) {
                        alert('Audio format could not be converted appropriately. Please contact the developer of this website.');
                    } else if (response.status === 422) {
                        alert('No audio was recorded. Is your microphone on and working? If the error persists, please contact the developer of this website.');
                    } else if (response.status === 401) {
                        alert('You are not authorized to perform this action.');
                    } else {
                        console.error('Error uploading audio file:', response.statusText);
                        alert('An error occurred while uploading the audio file.');
                    }
                })
                .catch(error => {
                    hideLoadingOverlay(); // Hide overlay on error
                    console.error('Error uploading audio file:', error);
                    alert('An error occurred while uploading the audio file.');
                });
        } else if (action === 'delete_audio') {
            hideLoadingOverlay(); // Hide overlay immediately for discard action
            alert('Audio recording has been discarded.');
        }
    }

    function showLoadingOverlay() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = 'flex'; // Show overlay
    }

    function hideLoadingOverlay() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = 'none'; // Hide overlay
    }

    // Attach event listeners to buttons
    startButton.addEventListener('click', () => {
        startRecording();
        startButton.disabled = true;
        pauseButton.disabled = false;
        stopButton.disabled = false;
    });

    pauseButton.addEventListener('click', () => {
        pauseRecording();
        startButton.disabled = false;
        pauseButton.disabled = true;
    });

    stopButton.addEventListener('click', () => {
        stopRecording();
        startButton.disabled = false;
        pauseButton.disabled = true;
        stopButton.disabled = true;
    });
}
