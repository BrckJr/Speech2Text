export function setupMicrophoneAnimation(canvas, startButton, pauseButton, stopButton) {
    const ctx = canvas.getContext('2d');
    const durationInSeconds = 5;
    const sampleRate = 30;
    const totalSamples = durationInSeconds * sampleRate * 2;
    let historyBuffer = new Array(totalSamples).fill(0);

    let isRecording = false;
    let isPaused = false;
    let audioContext, analyser, source, dataArray;

    function draw() {
        if (!isRecording) return; // Stop drawing if recording is stopped

        if (isPaused) {
            // If paused, skip this frame and wait for next animation frame
            requestAnimationFrame(draw);
            return;
        }

        requestAnimationFrame(draw);

        analyser.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
        const normalizedValue = average / 255;

        historyBuffer.push(normalizedValue);
        if (historyBuffer.length > totalSamples) historyBuffer.shift();

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = 'white';
        for (let i = 0; i < canvas.width; i = i + 2) {
            const sampleIndex = Math.floor(i * (totalSamples / canvas.width));
            const value = historyBuffer[sampleIndex];
            const barHeight = (value * canvas.height / 2) * 1.5;

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

    function startRecording() {
        if (isRecording) return;

        isRecording = true;
        updateButtonStates(true, false, false);

        navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            analyser = audioContext.createAnalyser();
            source = audioContext.createMediaStreamSource(stream);
            source.connect(analyser);

            analyser.fftSize = 128;
            const bufferLength = analyser.frequencyBinCount;
            dataArray = new Uint8Array(bufferLength);

            draw(); // Start the animation
        }).catch(err => {
            console.error('Error accessing the microphone:', err);
        });
    }

    function pauseRecording() {
        if (!isRecording) return;
        isPaused = true;
        updateButtonStates(false, true, false);
    }

    function resumeRecording() {
        if (!isRecording || !isPaused) return;
        isPaused = false;
        updateButtonStates(true, false, false);
        draw(); // Resume drawing the waveform
    }

    function stopRecording() {
        if (!isRecording) return;

        isRecording = false;
        isPaused = false;

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        historyBuffer = new Array(totalSamples).fill(0);
        dataArray = new Uint8Array(analyser.frequencyBinCount);

        // Stop and close the audio context
        if (audioContext) {
            audioContext.close().then(() => {
                console.log('Audio context closed');
            });
            audioContext = null; // Clear the reference to the audio context
        }

        // Stop the media stream and disconnect the microphone
        if (source && source.mediaStream) {
            source.mediaStream.getTracks().forEach(track => {
                track.stop();
                console.log('Media stream track stopped:', track);
            });
            source = null; // Clear the reference to the source
        }

        // Update button states to reflect the stopped state
        updateButtonStates(false, true, true); // Enable Start, Disable Pause, Disable Stop
    }


    function updateButtonStates(startState, pauseState, stopState) {
        startButton.disabled = startState;
        pauseButton.disabled = pauseState;
        stopButton.disabled = stopState;
    }

    startButton.addEventListener('click', () => {
        if (isPaused) {
            resumeRecording();
        } else {
            startRecording();
        }
    });

    pauseButton.addEventListener('click', pauseRecording);
    stopButton.addEventListener('click', stopRecording);
}
