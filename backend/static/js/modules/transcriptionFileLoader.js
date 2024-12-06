// Function to load and display transcription files
// noinspection DuplicatedCode

export async function loadTranscriptionFiles() {
    try {
        // Fetch the list of transcription files from the server
        const response = await fetch('/list-transcription-files');
        const data = await response.json();  // Parse the response as JSON

        if (data.error) {
            console.error(data.error);  // Log an error if one exists in the response
            return;
        }

        const fileList = document.querySelector('#transcribed-files .file-list');
        fileList.innerHTML = ''; // Clear existing content from the file list

        // Loop through the list of transcription file paths and create clickable links
        data.files.forEach(filePath => {
            const listItem = document.createElement('div');  // Create a new list item for each file
            listItem.className = 'file-item';  // Add a class for styling

            // Create a clickable link for each transcription file
            const fileLink = document.createElement('a');
            fileLink.href = `${filePath.replace('backend/', '')}`;  // Use the relative path to the static folder
            fileLink.textContent = filePath.split('/').pop();  // Display only the file name (not the full path)
            fileLink.target = '_blank';  // Open the link in a new tab

            // Append the link to the list item and the list item to the file list
            listItem.appendChild(fileLink);
            fileList.appendChild(listItem);
        });
    } catch (err) {
        console.error('Error loading transcription files:', err);  // Log any errors during the fetch operation
    }
}
