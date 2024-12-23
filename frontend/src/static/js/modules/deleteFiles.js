// Function to set up delete button with event listener
export function setupDeleteButton(deleteButton) {
    // Function to show the delete confirmation modal when user clicks Delete button
    function showDeleteConfirmationModal() {
        const modal = document.getElementById('delete-confirmation-modal');
        modal.style.display = 'block';  // Show the modal for confirmation

        // Add event listener for the Confirm Delete button in the modal
        document.getElementById('confirm-delete').onclick = () => {
            handleDeleteAllFiles();  // Call the function to delete all files
            modal.style.display = 'none';  // Close the modal
        };

        // Add event listener for the Cancel Delete button in the modal
        document.getElementById('cancel-delete').onclick = () => {
            modal.style.display = 'none';  // Close the modal
        };
    }

    // Function to handle the actual deletion of all files
    function handleDeleteAllFiles() {
        // Send a POST request to delete all files from the server
        fetch('/delete-all-files', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ action: 'delete' })  // Sending an action payload indicating delete
        })
            .then(response => {
                if (response.ok) {
                    location.reload();  // Reload the page to reflect the changes
                    return response.json();
                } else {
                    throw new Error('Failed to delete files.');
                }
            })
            .catch(error => {
                console.error('Error:', error);  // Log any errors during the process
                alert('An error occurred. Please try again later.' +
                    'If the error persists, please contact the developer of this website.');  // Alert the user if there's an error
            });
    }

    // Attach event listener to the Delete button on the page
    deleteButton.addEventListener('click', () => {
        showDeleteConfirmationModal();  // Show the confirmation modal when delete is clicked
    });
}
