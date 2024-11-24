// Get button elements
const startButton = document.getElementById('start');
const pauseButton = document.getElementById('pause');
const stopButton = document.getElementById('stop');
const deleteButton = document.querySelector('.delete-btn');

// Function to load audio file paths from the database
// Function to load audio files from the server
async function loadAudioFiles() {
    try {
        const response = await fetch('/list-audio-files');
        const data = await response.json();

        if (data.error) {
            console.error(data.error);
            return;
        }

        const fileList = document.querySelector('#raw-audio-files .file-list');
        fileList.innerHTML = ''; // Clear existing content

        // Loop through the list of audio file paths and create links
        data.files.forEach(filePath => {
            const listItem = document.createElement('div');
            listItem.className = 'file-item';

            // Create a clickable link for each audio file
            const fileLink = document.createElement('a');
            fileLink.href = `/static/${filePath}`;  // Use relative path to static folder
            fileLink.textContent = filePath.split('/').pop();  // Display only the file name
            fileLink.target = '_blank';  // Open in a new tab

            // Append the link to the list item
            listItem.appendChild(fileLink);
            fileList.appendChild(listItem);
        });
    } catch (err) {
        console.error('Error loading audio files:', err);
    }
}


// Function to load transcription files from the server
// Function to load transcription files from the server
async function loadTranscriptionFiles() {
    try {
        const response = await fetch('/list-transcription-files');
        const data = await response.json();

        if (data.error) {
            console.error(data.error);
            return;
        }

        const fileList = document.querySelector('#transcribed-files .file-list');
        fileList.innerHTML = ''; // Clear existing content

        // Loop through the list of transcription file paths and create links
        data.files.forEach(filePath => {
            const listItem = document.createElement('div');
            listItem.className = 'file-item';

            // Create a clickable link for each transcription file
            const fileLink = document.createElement('a');
            fileLink.href = `/static/${filePath}`;  // Use relative path to static folder
            fileLink.textContent = filePath.split('/').pop();  // Display only the file name
            fileLink.target = '_blank';  // Open in a new tab

            // Append the link to the list item
            listItem.appendChild(fileLink);
            fileList.appendChild(listItem);
        });
    } catch (err) {
        console.error('Error loading transcription files:', err);
    }
}

// Load audio files on page load
document.addEventListener('DOMContentLoaded', loadAudioFiles);

// Load transcription files on page load
document.addEventListener('DOMContentLoaded', loadTranscriptionFiles);

// Event listener for Start button
startButton.addEventListener('click', () => {
    console.log('Start clicked');
    // Send request to the backend to start recording
    fetch('/start', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
            startButton.disabled = true;
            pauseButton.disabled = false;
            stopButton.disabled = false;
        })
        .catch(error => console.error('Error:', error));
});

// Event listener for Pause button
pauseButton.addEventListener('click', () => {
    console.log('Pause clicked');
    // Send request to the backend to pause recording
    fetch('/pause', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
        })
        .catch(error => console.error('Error:', error));
});

// Event listener for Stop button
stopButton.addEventListener('click', () => {
    console.log('Stop clicked');

    // Check if the user wants a transcription of the recording
    const userConfirmed = confirm("Do you want to transcribe the recorded audio file?");

    // Send request to the backend to stop recording
    fetch('/stop', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ transcribe: userConfirmed }) // Pass the user's choice
    })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);

            // Disable the buttons as needed
            startButton.disabled = false;
            pauseButton.disabled = true;
            stopButton.disabled = true;

            // Refresh the file lists
            loadAudioFiles();
            loadTranscriptionFiles();
        })
        .catch(error => console.error('Error:', error));
});

// Event listener for Delete button
deleteButton.addEventListener('click', () => {
    console.log('Delete all files clicked');
    // Display the confirmation prompt
    const userConfirmed = confirm("Are you sure you want to delete all files? This action cannot be undone.");

    if (userConfirmed) {
        // If confirmed, send an AJAX request to the backend to delete the files
        fetch('/delete-all-files', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ action: 'delete' })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('All files deleted successfully!');
                location.reload(); // Reload the page to reflect the changes
            } else {
                alert('Failed to delete files. Please try again later.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again later.');
        });
    } else {
        // If not confirmed, do nothing
        console.log("File deletion cancelled.");
    }
});
