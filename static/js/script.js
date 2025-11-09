document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const voiceBtn = document.getElementById('voice-btn');
    const chatContainer = document.getElementById('chat-container');
    const audioPlayer = document.getElementById('audio-player');
    
    let recognition;
    let isListening = false;
    
    // Check for browser support for Web Speech API
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            userInput.value = transcript;
            processUserInput(transcript);
        };
        
        recognition.onerror = (event) => {
            console.error('Speech recognition error', event.error);
            updateVoiceButtonState(false);
        };
        
        recognition.onend = () => {
            updateVoiceButtonState(false);
        };
    } else {
        console.warn('Speech recognition not supported in this browser');
        voiceBtn.disabled = true;
        voiceBtn.title = 'Speech recognition not supported in your browser';
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
    
    voiceBtn.addEventListener('click', toggleVoiceRecognition);
    
    // Functions
    function toggleVoiceRecognition() {
        if (!recognition) return;
        
        if (isListening) {
            recognition.stop();
        } else {
            try {
                recognition.start();
                updateVoiceButtonState(true);
            } catch (error) {
                console.error('Error starting speech recognition:', error);
                updateVoiceButtonState(false);
            }
        }
    }
    
    function updateVoiceButtonState(listening) {
        isListening = listening;
        voiceBtn.innerHTML = listening ? 
            '<i class="fas fa-stop"></i>' : 
            '<i class="fas fa-microphone"></i>';
        voiceBtn.classList.toggle('bg-red-500', listening);
        voiceBtn.classList.toggle('hover:bg-red-600', listening);
        voiceBtn.classList.toggle('bg-indigo-500', !listening);
        voiceBtn.classList.toggle('hover:bg-indigo-600', !listening);
    }
    
    async function processUserInput(text) {
        // Add user message to chat
        addMessageToChat('user', text);
        
        // Show typing indicator
        const typingIndicator = showTypingIndicator();
        
        try {
            // Send to server for processing
            const response = await fetch('/process_input', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ input: text })
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            
            // Remove typing indicator
            typingIndicator.remove();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Add AI response to chat
            addMessageToChat('ai', data.text);
            
            // Play the audio response
            if (data.audio) {
                audioPlayer.src = `data:audio/mp3;base64,${data.audio}`;
                audioPlayer.play().catch(e => console.error('Error playing audio:', e));
            }
            
        } catch (error) {
            console.error('Error:', error);
            // Remove typing indicator
            typingIndicator.remove();
            // Show error message
            addMessageToChat('ai', 'Sorry, I encountered an error. Please try again.');
        }
    }
    
    function addMessageToChat(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message mb-3`;
        messageDiv.textContent = text;
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
