let fileToDeletePath = '';

export function showDeleteConfirmationModal(filePath) {
    const modal = document.getElementById('delete-single-confirmation-modal');
    if (modal) { // Only proceed if the modal exists
        modal.style.display = 'block';
        fileToDeletePath = filePath;
    }
}

function closeModal() {
    const modal = document.getElementById('delete-single-confirmation-modal');
    if (modal) { // Only proceed if the modal exists
        modal.style.display = 'none';
    }
}

// Initialize event listeners only if the required DOM elements exist
document.addEventListener('DOMContentLoaded', () => {
    const confirmDeleteButton = document.getElementById('confirm-delete-single');
    const cancelDeleteButton = document.getElementById('cancel-delete-single');

    if (confirmDeleteButton) {
        confirmDeleteButton.onclick = async () => {
            if (!fileToDeletePath) return;

            try {
                const response = await fetch('/delete-file', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ filePath: fileToDeletePath }),
                });

                const result = await response.json();
                if (result.success) {
                    location.reload();
                } else {
                    alert('Failed to delete file');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred');
            }

            closeModal();
        };
    }

    if (cancelDeleteButton) {
        cancelDeleteButton.onclick = () => {
            closeModal();
        };
    }
});
