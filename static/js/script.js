document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const calculateBtn = document.getElementById('calculate-btn');
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const distanceInput = document.getElementById('distance');
    const warpSpeedInput = document.getElementById('warp-speed');
    const subwarpSpeedInput = document.getElementById('subwarp-speed');
    const detonationTimeInput = document.getElementById('detonation-time');
    const alignAlertInput = document.getElementById('align-alert');
    const bombAlertInput = document.getElementById('bomb-alert');
    const timerElement = document.getElementById('timer');
    const statusElement = document.getElementById('status');
    const progressBar = document.getElementById('progress-bar');
    const resultsElement = document.getElementById('results');
    
    // Audio context for sound alerts
    let audioContext;
    try {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    } catch (e) {
        console.warn('Web Audio API is not supported in this browser');
    }
    
    // Variables for the timer
    let countdownInterval;
    let startTime;
    let totalTime;
    let launchTime;
    let alignAlertTime;
    let bombAlertTime;
    let alignAlertTriggered = false;
    let bombAlertTriggered = false;
    
    // Event listeners
    calculateBtn.addEventListener('click', calculate);
    startBtn.addEventListener('click', startCountdown);
    stopBtn.addEventListener('click', stopCountdown);
    
    // Calculate function
    function calculate() {
        // Get input values
        const inputData = {
            distance: parseFloat(distanceInput.value),
            warp_speed: parseFloat(warpSpeedInput.value),
            subwarp_speed: parseFloat(subwarpSpeedInput.value),
            detonation_time: parseFloat(detonationTimeInput.value)
        };
        
        // Validate inputs
        if (Object.values(inputData).some(isNaN) || Object.values(inputData).some(val => val <= 0)) {
            displayError('All inputs must be positive numbers');
            return;
        }
        
        // Send request to backend
        fetch('/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(inputData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                displayError(data.error);
                return;
            }
            
            displayResults(data);
            
            // Store values for countdown
            totalTime = data.countdown.total_time;
            launchTime = data.countdown.launch_time;
            
            // Enable timer controls
            startBtn.disabled = false;
            stopBtn.disabled = true;
            
            // Reset progress bar
            progressBar.style.width = '0%';
        })
        .catch(error => {
            console.error('Error:', error);
            displayError('An error occurred while calculating');
        });
    }
    
    // Display the calculation results
    function displayResults(data) {
        let resultsHTML = '';
        
        // Target information section
        resultsHTML += createSection('TARGET INFORMATION', [
            data.target_info.warp_distance,
            `Warp Speed: ${data.target_info.warp_speed}`,
            `Sub Warp Speed: ${data.target_info.subwarp_speed}`,
            `Bomb Detonation Time: ${data.target_info.detonation_time}`
        ]);
        
        // Warp time breakdown section
        resultsHTML += createSection('WARP TIME BREAKDOWN', [
            `Acceleration Phase: ${data.warp_time.accel_phase}`,
            `Cruise Phase: ${data.warp_time.cruise_phase}`,
            `Deceleration Phase: ${data.warp_time.decel_phase}`,
            ``,
            `Total Warp Time: ${data.warp_time.total_time}`
        ]);
        
        // Bomb launch timing section
        resultsHTML += createSection('BOMB LAUNCH TIMING', [
            `Launch Bomb at: ${data.bomb_timing.launch_time}`,
            `Which is ${data.bomb_timing.time_before_landing}`,
            ``,
            `Distance Remaining In warp at launch Time: ${data.bomb_timing.distance_remaining}`
        ]);
        
        resultsElement.innerHTML = resultsHTML;
    }
    
    // Create a formatted section
    function createSection(title, items) {
        let section = `<div class="section">
            <div class="section-title">${title}</div>
            <div class="section-content">`;
        
        items.forEach(item => {
            section += `<div>${item}</div>`;
        });
        
        section += `</div></div>`;
        return section;
    }
    
    // Display error message
    function displayError(message) {
        resultsElement.innerHTML = `<div class="error">${message}</div>`;
    }
    
    // Start the countdown timer
    function startCountdown() {
        if (!launchTime) {
            statusElement.textContent = 'Please calculate first';
            return;
        }
        
        // Initialize audio context on user interaction if needed
        if (!audioContext) {
            try {
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
            } catch (e) {
                console.warn('Web Audio API is not supported in this browser');
            }
        } else if (audioContext.state === 'suspended') {
            audioContext.resume();
        }
        
        alignAlertTime = parseFloat(alignAlertInput.value);
        bombAlertTime = parseFloat(bombAlertInput.value);
        
        startBtn.disabled = true;
        stopBtn.disabled = false;
        statusElement.textContent = 'Counting down...';
        timerElement.style.color = 'var(--accent-color)';
        
        startTime = Date.now();
        alignAlertTriggered = false;
        bombAlertTriggered = false;
        
        // Play start sound
        playSound('start');
        
        countdownInterval = setInterval(updateCountdown, 50);
    }
    
    // Update the countdown display
    function updateCountdown() {
        const elapsed = (Date.now() - startTime) / 1000;
        const remaining = Math.max(0, launchTime - elapsed);
        
        // Update progress bar
        const progressPercent = Math.min(100, (elapsed / totalTime) * 100);
        progressBar.style.width = `${progressPercent}%`;
        
        // Update timer display
        const hours = Math.floor(remaining / 3600);
        const minutes = Math.floor((remaining % 3600) / 60);
        const seconds = Math.floor(remaining % 60);
        const timeString = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        timerElement.textContent = timeString;
        
        // Check for alerts
        if (!alignAlertTriggered && remaining <= alignAlertTime) {
            triggerAlert('ALIGN NOW!', 'var(--warning-color)');
            alignAlertTriggered = true;
        }
        
        if (!bombAlertTriggered && remaining <= bombAlertTime) {
            triggerAlert('LAUNCH BOMB!', 'var(--success-color)');
            bombAlertTriggered = true;
        }
        
        // Check if timer is complete
        if (remaining <= 0) {
            triggerAlert('TARGET LANDING!', 'var(--warning-color)');
            stopCountdown();
        }
    }
    
    // Generate a sound with specified parameters
    function playSound(type) {
        if (!audioContext) return;
        
        // Resume audio context if it's suspended (browsers require user interaction)
        if (audioContext.state === 'suspended') {
            audioContext.resume();
        }
        
        // Create oscillator and gain nodes
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        // Set parameters based on alert type
        if (type === 'start') {
            // Startup sound
            oscillator.type = 'sine';
            oscillator.frequency.setValueAtTime(523.25, audioContext.currentTime); // C5 note
            oscillator.frequency.exponentialRampToValueAtTime(783.99, audioContext.currentTime + 0.2); // G5 note
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.4);
        } else if (type === 'align') {
            // Lower pitch warning sound
            oscillator.type = 'triangle';
            oscillator.frequency.setValueAtTime(440, audioContext.currentTime); // A4 note
            oscillator.frequency.exponentialRampToValueAtTime(880, audioContext.currentTime + 0.2); // Up to A5
            gainNode.gain.setValueAtTime(0.5, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
        } else if (type === 'bomb') {
            // Higher pitch alert sound
            oscillator.type = 'square';
            oscillator.frequency.setValueAtTime(880, audioContext.currentTime); // A5 note
            oscillator.frequency.exponentialRampToValueAtTime(440, audioContext.currentTime + 0.1); // Down to A4
            oscillator.frequency.exponentialRampToValueAtTime(880, audioContext.currentTime + 0.2); // Back to A5
            gainNode.gain.setValueAtTime(0.5, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
        } else if (type === 'landing') {
            // Target landing alarm
            oscillator.type = 'sawtooth';
            oscillator.frequency.setValueAtTime(660, audioContext.currentTime); // E5 note
            oscillator.frequency.exponentialRampToValueAtTime(330, audioContext.currentTime + 0.3); // Down to E4
            gainNode.gain.setValueAtTime(0.6, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.6);
        }
        
        // Connect the nodes
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        // Start and stop the sound
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 1);
    }
    
    // Trigger an alert
    function triggerAlert(message, color) {
        statusElement.textContent = message;
        timerElement.style.color = color;
        
        // Play appropriate sound based on the message
        if (message === 'ALIGN NOW!') {
            playSound('align');
        } else if (message === 'LAUNCH BOMB!') {
            playSound('bomb');
        } else if (message === 'TARGET LANDING!') {
            playSound('landing');
        }
    }
    
    // Stop the countdown timer
    function stopCountdown() {
        clearInterval(countdownInterval);
        startBtn.disabled = false;
        stopBtn.disabled = true;
        timerElement.textContent = '00:00:00';
        statusElement.textContent = 'Ready';
        progressBar.style.width = '0%';
        timerElement.style.color = 'var(--accent-color)';
    }
});