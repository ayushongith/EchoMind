document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const voiceBtn = document.getElementById('voice-btn');
    const chatContainer = document.getElementById('chat-container');
    const audioPlayer = document.getElementById('audio-player');
    
    let mediaRecorder = null;
    let audioChunks = [];
    let isRecording = false;
    let statusIndicator = null;
    let audioStream = null;
    
    // Check for MediaRecorder support
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia && MediaRecorder) {
        // Browser supports audio recording
        console.log('MediaRecorder API supported');
    } else {
        console.warn('MediaRecorder API not supported in this browser');
        voiceBtn.disabled = true;
        voiceBtn.title = 'Audio recording not supported in your browser';
        voiceBtn.classList.add('opacity-50', 'cursor-not-allowed');
    }
    
    // Event Listeners
    sendBtn.addEventListener('click', () => {
        const text = userInput.value.trim();
        if (text) {
            processUserInput(text);
            userInput.value = '';
        }
    });
    
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            const text = userInput.value.trim();
            if (text) {
                processUserInput(text);
                userInput.value = '';
            }
        }
    });
    
    // Keyboard shortcut: Space bar to toggle voice (when input is not focused)
    document.addEventListener('keydown', (e) => {
        if (e.code === 'Space' && document.activeElement !== userInput && !e.target.matches('input, textarea, button')) {
            e.preventDefault();
            toggleVoiceRecording();
        }
    });
    
    voiceBtn.addEventListener('click', toggleVoiceRecording);
    
    // Functions
    async function toggleVoiceRecording() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert('Audio recording is not supported in your browser. Please use a modern browser like Chrome, Edge, or Firefox.');
            return;
        }
        
        if (isRecording) {
            // Stop recording
            stopRecording();
        } else {
            // Start recording
            await startRecording();
        }
    }
    
    async function startRecording() {
        try {
            updateStatusIndicator('Requesting microphone access...', 'info');
            
            // Request microphone access
            audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Create MediaRecorder
            const options = { mimeType: 'audio/webm' };
            if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                options.mimeType = 'audio/webm;codecs=opus';
                if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                    options.mimeType = ''; // Use browser default
                }
            }
            
            mediaRecorder = new MediaRecorder(audioStream, options);
            audioChunks = [];
            
            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };
            
            mediaRecorder.onstop = async () => {
                // Process the recorded audio
                await processRecordedAudio();
                
                // Stop all tracks
                if (audioStream) {
                    audioStream.getTracks().forEach(track => track.stop());
                    audioStream = null;
                }
            };
            
            mediaRecorder.onerror = (event) => {
                console.error('MediaRecorder error:', event.error);
                updateStatusIndicator('Recording error. Please try again.', 'error');
                stopRecording();
            };
            
            // Start recording
            mediaRecorder.start();
            isRecording = true;
            updateVoiceButtonState(true);
            updateStatusIndicator('Recording... Speak now! (Click stop when done)', 'listening');
            
        } catch (error) {
            console.error('Error starting recording:', error);
            let errorMsg = 'Failed to start recording. ';
            if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
                errorMsg += 'Microphone permission denied. Please allow microphone access.';
            } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
                errorMsg += 'No microphone found. Please connect a microphone.';
            } else {
                errorMsg += error.message || 'Please try again.';
            }
            updateStatusIndicator(errorMsg, 'error');
            updateVoiceButtonState(false);
        }
    }
    
    function stopRecording() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            isRecording = false;
            updateVoiceButtonState(false);
            updateStatusIndicator('Processing audio...', 'info');
        }
    }
    
    async function processRecordedAudio() {
        if (audioChunks.length === 0) {
            updateStatusIndicator('No audio recorded. Please try again.', 'error');
            return;
        }
        
        try {
            // Create blob from audio chunks
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            
            // Send to backend for transcription
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');
            
            updateStatusIndicator('Transcribing audio...', 'info');
            
            const response = await fetch('/transcribe_audio', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `Server error: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            if (data.text && data.text.trim()) {
                // Set transcribed text in input field
                userInput.value = data.text.trim();
                updateStatusIndicator('Transcription complete! Click send or record again.', 'info');
                
                // Auto-submit after a short delay
                setTimeout(() => {
                    if (userInput.value.trim()) {
                        processUserInput(userInput.value.trim());
                        userInput.value = '';
                    }
                }, 1000);
            } else {
                updateStatusIndicator('No speech detected. Please try again.', 'error');
            }
            
        } catch (error) {
            console.error('Error processing audio:', error);
            updateStatusIndicator(`Error: ${error.message}`, 'error');
        } finally {
            // Clear audio chunks for next recording
            audioChunks = [];
        }
    }
    
    function updateVoiceButtonState(recording) {
        isRecording = recording;
        if (recording) {
            voiceBtn.innerHTML = '<i class="fas fa-stop"></i>';
            voiceBtn.classList.remove('bg-indigo-500', 'hover:bg-indigo-600');
            voiceBtn.classList.add('bg-red-500', 'hover:bg-red-600', 'animate-pulse');
            voiceBtn.title = 'Click to stop recording';
        } else {
            voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            voiceBtn.classList.remove('bg-red-500', 'hover:bg-red-600', 'animate-pulse');
            voiceBtn.classList.add('bg-indigo-500', 'hover:bg-indigo-600');
            voiceBtn.title = 'Click to start voice input';
        }
    }
    
    function updateStatusIndicator(message, type = 'info') {
        // Remove existing status indicator
        const existing = document.getElementById('voice-status');
        if (existing) {
            existing.remove();
        }
        
        // Create new status indicator
        statusIndicator = document.createElement('div');
        statusIndicator.id = 'voice-status';
        statusIndicator.className = `voice-status ${type} mb-2 p-2 rounded text-sm`;
        
        let icon = '';
        let bgColor = 'bg-blue-100 text-blue-800';
        
        if (type === 'listening') {
            icon = '<i class="fas fa-circle text-red-500 animate-pulse mr-2"></i>';
            bgColor = 'bg-red-100 text-red-800';
        } else if (type === 'error') {
            icon = '<i class="fas fa-exclamation-circle mr-2"></i>';
            bgColor = 'bg-red-100 text-red-800';
        } else {
            icon = '<i class="fas fa-info-circle mr-2"></i>';
        }
        
        statusIndicator.className += ` ${bgColor}`;
        statusIndicator.innerHTML = icon + message;
        
        // Insert before the input field container
        const inputContainer = userInput.parentElement;
        inputContainer.parentElement.insertBefore(statusIndicator, inputContainer);
        
        // Auto-hide info messages after 5 seconds
        if (type === 'info') {
            setTimeout(() => {
                if (statusIndicator && statusIndicator.parentElement) {
                    statusIndicator.remove();
                }
            }, 5000);
        }
    }
    
    async function processUserInput(text) {
        if (!text || !text.trim()) {
            return;
        }
        
        const inputText = text.trim();
        
        // Add user message to chat
        addMessageToChat('user', inputText);
        
        // Clear input field
        userInput.value = '';
        
        // Remove status indicator
        const status = document.getElementById('voice-status');
        if (status) status.remove();
        
        // Show typing indicator
        const typingIndicator = showTypingIndicator();
        
        try {
            // Send to server for processing
            const response = await fetch('/process_input', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ input: inputText })
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `Server error: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Remove typing indicator
            typingIndicator.remove();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Add AI response to chat
            addMessageToChat('ai', data.text);
            
            // Play the audio response automatically
            if (data.audio) {
                audioPlayer.src = `data:audio/mp3;base64,${data.audio}`;
                audioPlayer.play().catch(e => {
                    console.error('Error playing audio:', e);
                    updateStatusIndicator('Audio playback failed. Text response is available above.', 'error');
                });
            } else {
                updateStatusIndicator('Response received (no audio)', 'info');
            }
            
        } catch (error) {
            console.error('Error:', error);
            // Remove typing indicator
            typingIndicator.remove();
            // Show error message
            const errorMsg = error.message || 'Sorry, I encountered an error. Please try again.';
            addMessageToChat('ai', `Error: ${errorMsg}`);
            updateStatusIndicator(errorMsg, 'error');
        }
    }
    
    function addMessageToChat(sender, text) {
        // Remove the initial placeholder message if it exists
        const placeholder = chatContainer.querySelector('.text-center.text-gray-500');
        if (placeholder) {
            placeholder.remove();
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message mb-3`;
        
        // Add timestamp
        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const timeSpan = document.createElement('span');
        timeSpan.className = 'text-xs opacity-70 ml-2';
        timeSpan.textContent = timestamp;
        
        // Add message text
        const textNode = document.createTextNode(text);
        messageDiv.appendChild(textNode);
        messageDiv.appendChild(timeSpan);
        
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        chatContainer.appendChild(typingDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        return typingDiv;
    }
});
