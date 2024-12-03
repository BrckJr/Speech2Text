// Function to load and display audio files and populate dropdown menu
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
        const dropdown = document.getElementById('recordings-dropdown');
        dropdown.innerHTML = ''; // Clear existing options in the dropdown

        // Create a default "Select a recording" option for the dropdown
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = '-';
        dropdown.appendChild(defaultOption);

        // Loop through the list of audio file paths and create clickable links
        data.files.forEach(filePath => {
            // Create a clickable link for each audio file
            const listItem = document.createElement('div');
            listItem.className = 'file-item';  // Add class to each list item

            const fileLink = document.createElement('a');
            fileLink.href = `/static/${filePath}`;  // Use relative path to the static folder
            fileLink.textContent = filePath.split('/').pop();  // Display only the file name (not the full path)
            fileLink.target = '_blank';  // Ensure the link opens in a new tab

            listItem.appendChild(fileLink); // Append the link to the list item
            fileList.appendChild(listItem); // Add the list item to the file list container

            // Create an option element for the dropdown
            const option = document.createElement('option');
            option.value = filePath;
            option.textContent = filePath.split('/').pop(); // Display file name in the dropdown

            // Append the option to the dropdown
            dropdown.appendChild(option);
        });
    } catch (err) {
        // Log any errors that occur during the fetch or processing
        console.error('Error loading audio files:', err);
    }
}
