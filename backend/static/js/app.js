import { loadAudioFiles } from './modules/audioFileLoader.js';
import { loadTranscriptionFiles } from './modules/transcriptionFileLoader.js';
import { setupControlButtons } from './modules/controlButtons.js';
import { setupDeleteButton } from './modules/deleteFiles.js';
import { setupCanvas } from './modules/backgroundCanvas.js';

document.addEventListener('DOMContentLoaded', () => {
    const page = document.body.dataset.page;

    // Common functionality (e.g., background)
    setupCanvas();

    // Page-specific functionality
    if (page === 'dashboard') {
        const startButton = document.getElementById('start');
        const pauseButton = document.getElementById('pause');
        const stopButton = document.getElementById('stop');
        const deleteButton = document.querySelector('.delete-btn');

        loadAudioFiles();
        loadTranscriptionFiles();
        setupControlButtons(startButton, pauseButton, stopButton);
        setupDeleteButton(deleteButton);
    }

    if (page === 'login') {
        // Add login-specific JS modules or functions
    }

    if (page === 'register') {
        // Add register-specific JS modules or functions
    }
});