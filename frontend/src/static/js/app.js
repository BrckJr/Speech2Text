import { loadFileList } from './modules/FileLoader.js';
import { setupDeleteButton } from './modules/deleteFiles.js';
import { setupCanvas } from './modules/backgroundCanvas.js';
import { setupLangSwitcherButtons } from './modules/langSwitcher.js';
import { setupAnalysisButton } from './modules/getAnalytics.js';
import { setupMicrophoneAnimation } from './modules/microphoneAnimation.js';
import { setupAudioRecording } from './modules/audioRecorder.js';
import { setupHeadingAnimation } from './modules/headingAnimation.js';

// Function to display webpage
document.addEventListener('DOMContentLoaded', () => {
    const page = document.body.dataset.page;

    // Common functionality (e.g., background, footer) for all pages
    setupCanvas();

    const en_button = document.getElementById('btn_en');
    const de_button = document.getElementById('btn_de');
    const es_button = document.getElementById('btn_es');
    setupLangSwitcherButtons(en_button, de_button, es_button);

    // Typing animation for the headline (common or specific pages)
    const headline = document.getElementById('headline');
    if (headline) {
        setupHeadingAnimation(headline, 'Presentable', 400);
    }

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

        // Logic for all buttons
        setupAnalysisButton(analysisButton);
        setupDeleteButton(deleteButton);
        setupAudioRecording(startButton, pauseButton, stopButton, audioFileDropdown);
        setupMicrophoneAnimation(recordingAnimationCanvas, startButton, pauseButton, stopButton);
    }
});