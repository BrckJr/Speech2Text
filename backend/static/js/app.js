// app.js

import { loadAudioFiles } from './modules/audioFileLoader.js';
import { loadTranscriptionFiles } from './modules/transcriptionFileLoader.js';
import { setupControlButtons } from './modules/controlButtons.js';
import { setupDeleteButton } from './modules/deleteFiles.js';
import { setupCanvas } from './modules/backgroundCanvas.js';

document.addEventListener('DOMContentLoaded', () => {
    const startButton = document.getElementById('start');
    const pauseButton = document.getElementById('pause');
    const stopButton = document.getElementById('stop');
    const deleteButton = document.querySelector('.delete-btn');

    // Initialize functionalities
    loadAudioFiles();
    loadTranscriptionFiles();
    setupControlButtons(startButton, pauseButton, stopButton);
    setupDeleteButton(deleteButton);
    setupCanvas();
});
