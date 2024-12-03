// Function to setup the event listener for the "Get Analysis" button
export function setupAnalysisButton(analysisButton) {

    // Check if the button exists to avoid errors
    if (analysisButton) {
        // Add event listener to the button
        analysisButton.addEventListener('click', async () => {
            try {
                // Perform the necessary logic when the button is clicked
                // Example: Call a controller in Python via fetch

                const selectedRecording = document.getElementById('recordings-dropdown').value;

                if (!selectedRecording) {
                    showErrorModal();
                    return;
                }

                // Send the selected recording to the backend (controller.py)
                const response = await fetch('/process-recording', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        recording: selectedRecording, // Send selected recording to server
                    }),
                });

                // Handle the response from the server
                const result = await response.json();

                if (result.success) {
                    console.log('Recording processed successfully:', result);

                } else {
                    console.error('Error processing recording:', result.error);
                    // Show error modal with the error message from the backend
                    showErrorModal();
                }
            } catch (err) {
                console.error('Error during fetch operation:', err);
                // Show error modal with a generic error message
                showErrorModal();
            }
        });
    }
}

// Function to show the error modal with a custom message
function showErrorModal(message) {
    const modal = document.getElementById('analysis-selection-modal');

    // Show the modal
    modal.style.display = 'block';

    // Close the modal when the user clicks the "OK" button
    document.getElementById('close-error-modal').onclick = () => {
        modal.style.display = 'none'; // Close the modal
    };
}
