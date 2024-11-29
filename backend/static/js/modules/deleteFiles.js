export function setupDeleteButton(deleteButton) {
    // Function to show the delete confirmation modal
    function showDeleteConfirmationModal() {
        const modal = document.getElementById('delete-confirmation-modal');
        modal.style.display = 'block';

        // Add event listeners for modal buttons
        document.getElementById('confirm-delete').onclick = () => {
            handleDeleteAllFiles();
            modal.style.display = 'none';
        };

        document.getElementById('cancel-delete').onclick = () => {
            console.log('File deletion cancelled.');
            modal.style.display = 'none';
        };
    }

    // Function to handle the delete action
    function handleDeleteAllFiles() {
        console.log('Confirmed delete all files');

        fetch('/delete-all-files', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ action: 'delete' }) // Sending an action payload
        })
            .then(response => {
                if (response.ok) {
                    location.reload(); // Reload the page to reflect the changes
                    return response.json();
                } else {
                    throw new Error('Failed to delete files.');
                }
            })
            .then(data => {
                if (!data.success) {
                    alert('Failed to delete files. Please try again later.');
                }
                // If success, do not show any prompts
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again later.');
            });
    }

    // Attach event listener to the delete button
    deleteButton.addEventListener('click', () => {
        console.log('Delete all files clicked');
        showDeleteConfirmationModal(); // Show the modal without the prompt
    });
}