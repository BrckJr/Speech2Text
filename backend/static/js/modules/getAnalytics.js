// Add a variable to set dropdown back to last valid selection when selecting nothing and hitting get analysis
let lastValidSelectedAudioFile = null;

// Function to handle the logic when the "Get Analysis" button is clicked
export async function setAnalytics() {
    try {
        const audioFileDropdown = document.getElementById('audioFile-dropdown');
        const selectedAudioFile = audioFileDropdown.value;

        if (!selectedAudioFile) {
            showErrorModal();
            // Reset the dropdown to the last valid value
            if (lastValidSelectedAudioFile !== null) { audioFileDropdown.value = lastValidSelectedAudioFile; }
            return;
        }

        // Store the current valid selection
        lastValidSelectedAudioFile = selectedAudioFile;

        // Send the selected recording to the backend
        const response = await fetch('/get-analytics', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                recording: selectedAudioFile, // Send selected recording to server
            }),
        });

        // Handle the response from the server
        const result = await response.json();

        if (result.success) {
            // Extract the graphic path
            let speechSpeedGraphicPath = result.speech_speed_graphic_path;

            if (speechSpeedGraphicPath) {
                // Create an img element
                const imgElement = document.createElement('img');
                imgElement.src = speechSpeedGraphicPath.replace('backend/', ''); // Set the src to the graphic path
                imgElement.alt = 'Speech Speed Analysis';
                imgElement.style.maxWidth = '100%'; // Ensure it fits within the panel
                imgElement.style.position = 'relative'; // Ensure it respects the layout flow
                imgElement.style.zIndex = '10'; // Ensure it appears above other elements

                // Find the "Speech rate" panel in the grid
                const speechRatePanel = document.querySelector('.analytics-panel[data-i18n="speech_rate"]');
                if (speechRatePanel) {
                    // Clear any previous images and add the new image under the existing text
                    speechRatePanel.querySelectorAll('img').forEach(img => img.remove());
                    speechRatePanel.appendChild(imgElement);
                } else {
                    console.error('Speech rate panel not found.');
                }
            } else {
                console.error('No speech speed graphic path provided in response.');
            }
        } else {
            console.error('Error analyzing recording:', result.error);
            showErrorModal();
        }
    } catch (err) {
        console.error('Error during fetch operation in setAnalytics:', err);
        showErrorModal();
    }
}


// Function to setup the event listener for the "Get Analysis" button
export function setupAnalysisButton(analysisButton) {
    // Check if the button exists to avoid errors
    if (analysisButton) {
        // Add event listener to the button
        analysisButton.addEventListener('click', setAnalytics);
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
