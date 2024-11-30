import { loadAudioFiles } from './modules/audioFileLoader.js';
import { loadTranscriptionFiles } from './modules/transcriptionFileLoader.js';
import { setupControlButtons } from './modules/controlButtons.js';
import { setupDeleteButton } from './modules/deleteFiles.js';
import { setupCanvas } from './modules/backgroundCanvas.js';

// Function to display webpage
document.addEventListener('DOMContentLoaded', () => {
    const page = document.body.dataset.page;
    // console.log('Currently running page: ' + page);

    // Common functionality (e.g. background, footer) for all pages
    setupCanvas();

    // Logic for the dashboard page
    if (page === 'dashboard') {
        const startButton = document.getElementById('start');
        const pauseButton = document.getElementById('pause');
        const stopButton = document.getElementById('stop');
        const deleteButton = document.querySelector('.delete-btn');

        // Loading all files of a respective user at start
        loadAudioFiles();
        loadTranscriptionFiles();

        // Logic for control and delete buttons
        setupControlButtons(startButton, pauseButton, stopButton);
        setupDeleteButton(deleteButton);
    }

    // Logic for the login page
    // if (page === 'login') {}

    // Logic for the registration page
    // if (page === 'register') {}
});