// Get button elements
const startButton = document.getElementById('start');
const pauseButton = document.getElementById('pause');
const stopButton = document.getElementById('stop');
const deleteButton = document.querySelector('.delete-btn');

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
    // Send request to the backend to stop recording
    fetch('/stop', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
            startButton.disabled = false;
            pauseButton.disabled = true;
            stopButton.disabled = true;
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
        fetch('/delete_all_files', {
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
