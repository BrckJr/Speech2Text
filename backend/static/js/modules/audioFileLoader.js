// Function to load and display audio files
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

        // Loop through the list of audio file paths and create clickable links
        data.files.forEach(filePath => {
            const listItem = document.createElement('div');
            listItem.className = 'file-item';  // Add class to each list item

            // Create a clickable link for each audio file
            const fileLink = document.createElement('a');
            fileLink.href = `/static/${filePath}`;  // Use relative path to the static folder
            fileLink.textContent = filePath.split('/').pop();  // Display only the file name (not the full path)
            fileLink.target = '_blank';  // Ensure the link opens in a new tab

            // Append the link to the list item
            listItem.appendChild(fileLink);

            // Add the list item to the file list container
            fileList.appendChild(listItem);
        });
    } catch (err) {
        // Log any errors that occur during the fetch or processing
        console.error('Error loading audio files:', err);
    }
}
