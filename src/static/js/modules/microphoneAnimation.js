export function setupMicrophoneAnimation(canvas, startButton, pauseButton, stopButton) {
    const ctx = canvas.getContext('2d');
    const durationInSeconds = 5;
    const sampleRate = 30;
    const totalSamples = durationInSeconds * sampleRate * 2;
    let historyBuffer = new Array(totalSamples).fill(0); // Initialize once

    let isRecording = false; // To track whether the animation is running
    let isPaused = false;    // To track if it's paused
    let audioContext, analyser, source, dataArray;

    function startRecording() {
        if (isRecording) return;  // Prevent starting if already recording

        isRecording = true;
        updateButtonStates(true, false, false); // Disable Start, Enable Pause and Stop

        navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            analyser = audioContext.createAnalyser();
            source = audioContext.createMediaStreamSource(stream);
            source.connect(analyser);

            analyser.fftSize = 128;
            const bufferLength = analyser.frequencyBinCount;
            dataArray = new Uint8Array(bufferLength); // Initialize dataArray once

            function draw() {
                if (!isRecording) return; // Stop drawing if recording is stopped

                if (isPaused) {
                    // If paused, skip this frame and wait for next animation frame
                    requestAnimationFrame(draw);
                    return;
                }

                requestAnimationFrame(draw);

                analyser.getByteFrequencyData(dataArray);
                const average = dataArray.reduce((sum, value) => sum + value, 0) / bufferLength;
                const normalizedValue = average / 255;

                historyBuffer.push(normalizedValue);
                if (historyBuffer.length > totalSamples) historyBuffer.shift();

                ctx.clearRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = 'white';
                for (let i = 0; i < canvas.width; i = i + 2) {
                    const sampleIndex = Math.floor(i * (totalSamples / canvas.width));
                    const value = historyBuffer[sampleIndex];
                    const barHeight = (value * canvas.height / 2) * 1.5; // Scale to have bigger animation

                    const x = i;
                    const y = (canvas.height - barHeight) / 2;
                    ctx.fillRect(x, y, 1, barHeight);
                }

                ctx.strokeStyle = 'white';
                ctx.lineWidth = 0.5;
                ctx.beginPath();
                ctx.moveTo(0, canvas.height / 2);
                ctx.lineTo(canvas.width, canvas.height / 2);
                ctx.stroke();
            }

            draw(); // Start drawing the waveform
        }).catch(err => {
            console.error('Error accessing the microphone:', err);
        });
    }

    function pauseRecording() {
        if (!isRecording) return;  // If not recording, no need to pause
        isPaused = true;
        updateButtonStates(false, true, false); // Disable Pause, Enable Start and Stop
    }

    function resumeRecording() {
        if (!isRecording || !isPaused) return; // If not recording or already playing, don't resume
        isPaused = false;
        updateButtonStates(true, false, false); // Disable Start, Enable Pause and Stop
        draw(); // Resume the drawing of the waveform
    }

    function stopRecording() {
        if (!isRecording) return; // If not recording, no need to stop

        isRecording = false;
        isPaused = false; // Reset the paused state

        ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear the canvas

        // Reset the dataArray and historyBuffer when stopped
        historyBuffer = new Array(totalSamples).fill(0);
        dataArray = new Uint8Array(analyser.frequencyBinCount); // Reset the data array

        // Stop the audio context
        if (audioContext) {
            audioContext.close().then(() => {
                console.log('Audio context closed');
            });
        }

        // Stop the media stream
        if (source && source.mediaStream) {
            source.mediaStream.getTracks().forEach(track => track.stop());
            console.log('Media stream tracks stopped');
        }

        updateButtonStates(false, false, true); // Disable Start and Pause, Enable Stop
    }


    // Button states update function
    function updateButtonStates(startState, pauseState, stopState) {
        startButton.disabled = startState;
        pauseButton.disabled = pauseState;
        stopButton.disabled = stopState;
    }

    // Event listener for Start button
    startButton.addEventListener('click', () => {
        if (isPaused) {
            resumeRecording(); // If paused, resume recording
        } else {
            startRecording(); // Start recording if not already recording
        }
    });

    // Event listener for Pause button
    pauseButton.addEventListener('click', pauseRecording);

    // Event listener for Stop button
    stopButton.addEventListener('click', stopRecording);
}
