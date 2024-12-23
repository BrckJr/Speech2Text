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
            if (lastValidSelectedAudioFile !== null) {
                audioFileDropdown.value = lastValidSelectedAudioFile;
            }
            return;
        }

        // Store the current valid selection
        lastValidSelectedAudioFile = selectedAudioFile;

        // Send the selected recording to the server
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
            // Extract the analytics data from result.data
            const params = result.data; // Accessing the dictionary under "data"

            // Update the analytics panels with new information
            await updatePanels(params);

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

async function updatePanels(params) {
    const {
        created_at,
        transcribed_text_path,
        speech_speed_graphic_path,
        pitch_graphic_path,
        energy_graphic_path,
        improved_text_path,
        recording_title,
        recording_language,
        audio_length,
        word_count,
        text_summary
    } = params;


    // Get the improved text from local storage and display it in the panel
    console.log(improved_text_path);
    // loadTextPanel(transcribed_text_path, 'transcribed');
    loadTextPanel(improved_text_path, 'improved');

    // Activate the text in the overview panel
    document.getElementById('panel-topic').style.display = 'block';
    document.getElementById('panel-language').style.display = 'block';
    document.getElementById('panel-audio-length').style.display = 'block';
    document.getElementById('panel-word-count').style.display = 'block';
    document.getElementById('panel-created-at').style.display = 'block';

    // Activate the text in the summary panel
    document.getElementById('panel-summary').style.display = 'block';

    // Format audio length
    let formattedAudioLength;
    if (audio_length < 60) {
        // Less than a minute, show seconds with two decimal places
        formattedAudioLength = `${audio_length.toFixed(2)} seconds`;
    } else {
        // Convert to minutes and seconds
        let minutes = Math.floor(audio_length / 60);
        let seconds = (audio_length % 60).toFixed(2); // Keep two decimal places for seconds
        formattedAudioLength = `${minutes} minutes ${seconds} seconds`;
    }

    // Set the dynamic values in the overview panel
    document.getElementById("topic").textContent = recording_title;
    document.getElementById("language").textContent = recording_language;
    document.getElementById("audio-length").textContent = formattedAudioLength;
    document.getElementById("word-count").textContent = word_count;
    document.getElementById("created-at").textContent = created_at;

    // Set the dynamic values in the summary panel
    document.getElementById("transcription_summary").textContent = text_summary;

    // Update graphics dynamically
    updateGraphic('speech-rate-panel', speech_speed_graphic_path, 'Speech Speed Analysis');
    updateGraphic('pitch-panel', pitch_graphic_path, 'Pitch Analysis');
    updateGraphic('energy-panel', energy_graphic_path, 'Energy Analysis');
}

function updateGraphic(panelId, graphicPath, altText) {
    if (graphicPath) {
        // Create an img element
        const imgElement = document.createElement('img');
        imgElement.src = graphicPath.replace('src/', ''); // Set the src to the graphic path
        imgElement.alt = altText;
        imgElement.style.maxWidth = '100%'; // Ensure it fits within the panel
        imgElement.style.position = 'relative'; // Ensure it respects the layout flow
        imgElement.style.zIndex = '10'; // Ensure it appears above other elements

        // Find the panel in the grid
        const panel = document.getElementById(panelId);
        if (panel) {
            // Clear any previous images and add the new image under the existing text
            panel.querySelectorAll('img').forEach(img => img.remove());
            panel.appendChild(imgElement);
        } else {
            console.error(`${panelId} not found.`);
        }
    } else {
        console.error(`No graphic path provided for ${altText}.`);
    }
}

function loadTextPanel(textFilePath, category) {
    let elementID = '';
    let spanID = '';

    // Determine the panel and span IDs based on the category
    if (category === 'improved') {
        elementID = 'improved-text-panel';
        spanID = 'improved_text';
    } else if (category === 'transcribed') {
        elementID = 'transcribed-text-panel';
        spanID = 'transcribed_text';
    } else {
        console.error('No valid category provided.');
        return;
    }

    if (textFilePath) {
        textFilePath = textFilePath.replace('src', '');
        fetch(textFilePath)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Failed to load file: ${response.statusText}`);
                }
                return response.text();
            })
            .then(textContent => {
                // Find the panel and span in the DOM
                const textPanel = document.getElementById(elementID);
                const textSpan = document.getElementById(spanID);

                if (textPanel && textSpan) {
                    // Activate the panel
                    textPanel.style.display = 'block';

                    // Update the span content with the fetched text
                    textSpan.textContent = textContent;
                    console.log(textContent);
                } else {
                    console.error('Text panel or span not found.');
                }
            })
            .catch(error => {
                console.error('Error loading the text file:', error);
            });
    } else {
        console.error('No valid text file path provided.');
    }
}
