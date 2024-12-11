import { loadFileList } from './modules/FileLoader.js';
import { setupControlButtons } from './modules/controlButtons.js';
import { setupDeleteButton } from './modules/deleteFiles.js';
import { setupCanvas } from './modules/backgroundCanvas.js';
import { setupLangSwitcherButtons } from './modules/langSwitcher.js';
import { setupAnalysisButton } from './modules/getAnalytics.js';
import { animateSpeedometer } from './modules/speedometer.js';
import { setupMicrophoneAnimation } from './modules/microphoneAnimation.js';

// Function to display webpage
document.addEventListener('DOMContentLoaded', () => {
    const page = document.body.dataset.page;

    // Common functionality (e.g., background, footer) for all pages
    setupCanvas();

    const en_button = document.getElementById('btn_en')
    const de_button = document.getElementById('btn_de')
    const es_button = document.getElementById('btn_es')
    setupLangSwitcherButtons(en_button, de_button, es_button)

    // Logic for the dashboard page
    if (page === 'dashboard') {
        const startButton = document.getElementById('start');
        const pauseButton = document.getElementById('pause');
        const stopButton = document.getElementById('stop');
        const deleteButton = document.querySelector('.delete-btn');
        const analysisButton = document.getElementById('get-analysis-btn');
        const audioFileDropdown = document.getElementById('audioFile-dropdown');
        const recordingAnimationCanvas = document.getElementById('visualizer');

        // Loading all files of a respective user at start and let it listen to updates during runtime
        loadFileList();

        // Logic for control, delete and recording analysis buttons
        setupAnalysisButton(analysisButton);
        setupControlButtons(startButton, pauseButton, stopButton, audioFileDropdown);
        setupDeleteButton(deleteButton);

        // Setup microphone animation
        setupMicrophoneAnimation(recordingAnimationCanvas, startButton, pauseButton, stopButton);
    }
});
