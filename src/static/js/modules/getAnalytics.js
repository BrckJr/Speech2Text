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

        // Send the selected recording to the src
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
            // Extract all information from the response
            let speechSpeedGraphicPath = result.speech_speed_graphic_path;
            let pitchGraphicPath = result.pitch_graphic_path;
            let title = result.recording_title;
            let language = result.recording_language;
            let audio_length = result.audio_length;
            let word_count = result.word_count;
            let summary = result.text_summary;

            // Update the analytics panels with new information
            updatePanels(speechSpeedGraphicPath, pitchGraphicPath, title, language, audio_length, word_count, summary)

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

function updatePanels(speechSpeedGraphicPath, pitchGraphicPath, title, language, audio_length, word_count, summary) {
    // Activate the text in the overview panel
    document.getElementById('panel-topic').style.display = 'block';
    document.getElementById('panel-language').style.display = 'block';
    document.getElementById('panel-audio-length').style.display = 'block';
    document.getElementById('panel-word-count').style.display = 'block';

    // Activate the text in the summary panel
    document.getElementById('panel-summary').style.display = 'block';

    // Format audio length
    if (audio_length < 60) {
        // Less than a minute, show seconds with two decimal places
        audio_length = `${audio_length.toFixed(2)} seconds`;
    } else {
        // Convert to minutes and seconds
        let minutes = Math.floor(audio_length / 60);
        let seconds = (audio_length % 60).toFixed(2); // Keep two decimal places for seconds
        audio_length = `${minutes} minutes ${seconds} seconds`;
    }

    // Set the dynamic values in the overview panel
    document.getElementById("topic").textContent = title;
    document.getElementById("language").textContent = language;
    document.getElementById("audio-length").textContent = audio_length;
    document.getElementById("word-count").textContent = word_count;

    // Set the dynamic values in the summary panel
    document.getElementById("transcription_summary").textContent = summary;

    // Update graphic of speech speed
    if (speechSpeedGraphicPath) {
        // Create an img element
        const imgElement = document.createElement('img');
        imgElement.src = speechSpeedGraphicPath.replace('src/', ''); // Set the src to the graphic path
        imgElement.alt = 'Speech Speed Analysis';
        imgElement.style.maxWidth = '100%'; // Ensure it fits within the panel
        imgElement.style.position = 'relative'; // Ensure it respects the layout flow
        imgElement.style.zIndex = '10'; // Ensure it appears above other elements

        // Find the "Speech rate" panel in the grid
        const speechRatePanel = document.getElementById('speech-rate-panel');
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


    if (pitchGraphicPath) {
        // Create an img element
        const imgElement = document.createElement('img');
        imgElement.src = pitchGraphicPath.replace('src/', ''); // Set the src to the graphic path
        imgElement.alt = 'Pitch Analysis';
        imgElement.style.maxWidth = '100%'; // Ensure it fits within the panel
        imgElement.style.position = 'relative'; // Ensure it respects the layout flow
        imgElement.style.zIndex = '10'; // Ensure it appears above other elements

        // Find the "Speech rate" panel in the grid
        const speechRatePanel = document.getElementById('pitch-panel');
        if (speechRatePanel) {
            // Clear any previous images and add the new image under the existing text
            speechRatePanel.querySelectorAll('img').forEach(img => img.remove());
            speechRatePanel.appendChild(imgElement);
        } else {
            console.error('Pitch panel not found.');
        }
    } else {
        console.error('No pitch graphic path provided in response.');
    }
}


