// deleteFiles.js

export function setupDeleteButton(deleteButton) {
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
}
