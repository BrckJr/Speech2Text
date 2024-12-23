import { showDeleteConfirmationModal } from './deleteSingleFile.js';

// Function to load and display audio, transcription, improved text, and date-time files
export async function loadFileList() {
    try {
        // Fetch the list of files from the server
        const response = await fetch('/list-files');
        const data = await response.json();

        // Handle potential errors from the server
        if (data.error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again later.' +
             'If the error persists, please contact the developer of this website.');  // Alert the user if there's an error
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

        // Ensure all lists have the same length (from the data object)
        const { audio_files, transcription_files, improved_text_files, date_times } = data.data; // Updated to access 'data' object
        if (
            audio_files.length !== transcription_files.length ||
            audio_files.length !== improved_text_files.length ||
            audio_files.length !== date_times.length
        ) {
            console.error('Mismatch between audio, transcription, improved text files, and date-times.');
            return;
        }

        // Loop through the lists and dynamically generate file rows
        audio_files.forEach((audioPath, index) => {
            const transcriptionPath = transcription_files[index];
            const improvedTextPath = improved_text_files[index];
            const dateTime = date_times[index];

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

            // Create the improved text file link
            const improvedTextLink = document.createElement('a');
            improvedTextLink.className = 'improved-text-link';
            improvedTextLink.href = `${improvedTextPath.replace('src/', '')}`;
            improvedTextLink.textContent = improvedTextPath.split('/').pop();
            improvedTextLink.target = '_blank';

            // Create a span element for date/time
            const dateTimeElement = document.createElement('span');
            dateTimeElement.className = 'date-time';
            dateTimeElement.textContent = dateTime;

            // Append elements to the listItem
            listItem.appendChild(deleteButton);
            listItem.appendChild(audioLink);
            listItem.appendChild(transcriptionLink);
            listItem.appendChild(improvedTextLink);
            listItem.appendChild(dateTimeElement);

            // Append the entire item to the file list
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