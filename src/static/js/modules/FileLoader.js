import { showDeleteConfirmationModal } from './deleteSingleFile.js';

// Function to load and display audio and transcription files and populate dropdown menu
export async function loadFileList() {
    try {
        // Fetch the list of audio and transcription files from the server
        const response = await fetch('/list-files');
        const data = await response.json();

        // Handle potential errors from the server
        if (data.error) {
            console.error(data.error);
            return;
        }

        // Get the container element to display the file list
        const fileList = document.querySelector('#raw-audio-files .file-list');
        fileList.innerHTML = ''; // Clear existing content in the list

        // Get the dropdown element
        const dropdown = document.getElementById('audioFile-dropdown');
        dropdown.innerHTML = ''; // Clear existing options in the dropdown

        // Create a default "Select a recording" option for the dropdown
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = '-';
        dropdown.appendChild(defaultOption);

        // Ensure both lists have the same length (assumes data correspondence is guaranteed)
        const { audio_files, transcription_files } = data;
        if (audio_files.length !== transcription_files.length) {
            console.error('Mismatch between audio files and transcription files.');
            return;
        }

        // Loop through the lists and dynamically generate file rows
        audio_files.forEach((audioPath, index) => {
            const transcriptionPath = transcription_files[index];

            // Create a container for each file entry (using CSS Grid)
            const listItem = document.createElement('div');
            listItem.className = 'file-item';

            // Create the delete button
            const deleteButton = document.createElement('button');
            deleteButton.className = 'delete-btn';
            deleteButton.textContent = '🗑️';
            deleteButton.onclick = () => showDeleteConfirmationModal(audioPath);

            // Create the audio file link
            const audioLink = document.createElement('a');
            audioLink.className = 'audio-link';
            audioLink.href = `${audioPath.replace('src/', '')}`;
            audioLink.textContent = audioPath.split('/').pop();
            audioLink.target = '_blank';

            // Create the transcription file link
            const transcriptionLink = document.createElement('a');
            transcriptionLink.className = 'transcription-link';
            transcriptionLink.href = `${transcriptionPath.replace('src/', '')}`;
            transcriptionLink.textContent = transcriptionPath.split('/').pop();
            transcriptionLink.target = '_blank';

            // Append elements in their respective positions
            listItem.appendChild(deleteButton);
            listItem.appendChild(audioLink);
            listItem.appendChild(transcriptionLink);

            // Append to fileList
            fileList.appendChild(listItem);

            // Add audio option to the dropdown
            const option = document.createElement('option');
            option.value = audioPath;
            option.textContent = audioPath.split('/').pop();
            dropdown.appendChild(option);
        });
    } catch (err) {
        console.error('Error loading files:', err);
    }
}