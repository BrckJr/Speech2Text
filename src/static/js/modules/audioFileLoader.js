import { showDeleteConfirmationModal } from './deleteSingleFile.js'

// Function to load and display audio files and populate dropdown menu
// noinspection DuplicatedCode
export async function loadAudioFiles() {
    try {
        // Fetch the list of audio files from the server
        const response = await fetch('/list-audio-files');
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

        // Loop through the list of audio file paths and create clickable links
        data.files.forEach(filePath => {
            // Create a container for each file entry
            const listItem = document.createElement('div');
            listItem.className = 'file-item';
            listItem.style.display = 'flex'; // Align elements side by side

            // Create the audio file link
            const fileLink = document.createElement('a');
            fileLink.href = `${filePath.replace('src/', '')}`;
            fileLink.textContent = filePath.split('/').pop();
            fileLink.target = '_blank';
            fileLink.style.flexGrow = '1';

            // Create the delete button
            const deleteButton = document.createElement('button');
            deleteButton.className = 'delete-btn';
            deleteButton.textContent = '🗑️';

            // Set up event listener for the delete button
            deleteButton.onclick = () => showDeleteConfirmationModal(filePath);

            // Append elements
            listItem.appendChild(deleteButton);
            listItem.appendChild(fileLink);
            fileList.appendChild(listItem);

            // Create an option element for the dropdown
            const option = document.createElement('option');
            option.value = filePath;
            option.textContent = filePath.split('/').pop();

            dropdown.appendChild(option);
        });
    } catch (err) {
        console.error('Error loading audio files:', err);
    }
}
