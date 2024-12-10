let fileToDeletePath = '';

export function showDeleteConfirmationModal(filePath) {
    const modal = document.getElementById('delete-single-confirmation-modal');
    modal.style.display = 'block';
    fileToDeletePath = filePath;
}

function closeModal() {
    const modal = document.getElementById('delete-single-confirmation-modal');
    modal.style.display = 'none';
}

document.getElementById('confirm-delete-single').onclick = async () => {
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

document.getElementById('cancel-delete-single').onclick = () => {
    closeModal();
};