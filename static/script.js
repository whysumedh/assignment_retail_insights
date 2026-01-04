// Modern Chat interface JavaScript

const chatMessages = document.getElementById('chatMessages');
const questionInput = document.getElementById('questionInput');
const sendBtn = document.getElementById('sendBtn');
const getSummaryBtn = document.getElementById('getSummaryBtn');
const clearChatBtn = document.getElementById('clearChatBtn');
const loadingOverlay = document.getElementById('loadingOverlay');
const suggestionButtons = document.querySelectorAll('.suggestion-btn');

// Send message on button click
sendBtn.addEventListener('click', sendMessage);

// Send message on Enter key
questionInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Suggestion buttons
suggestionButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const question = btn.getAttribute('data-question');
        questionInput.value = question;
        sendMessage();
    });
});

// Dataset summary
getSummaryBtn.addEventListener('click', async () => {
    showLoading();
    try {
        const response = await fetch('/api/summary');
        const data = await response.json();
        
        if (data.error) {
            addMessage('assistant', `Error: ${data.error}`);
        } else {
            addSummaryCard(data.summary);
        }
    } catch (error) {
        addMessage('assistant', `Error: ${error.message}`);
    } finally {
        hideLoading();
    }
});

// Reset interface
clearChatBtn.addEventListener('click', () => {
    chatMessages.innerHTML = `
        <div class="welcome-hero">
            <div class="hero-icon">🔎</div>
            <h1>How can I help with your retail data?</h1>
            <p>Ask about platform pricing, product categories, or market trends.</p>
        </div>
    `;
});

async function sendMessage() {
    const question = questionInput.value.trim();
    
    if (!question) return;
    
    addMessage('user', question);
    questionInput.value = '';
    showLoading();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question })
        });
        
        const data = await response.json();
        if (data.error) {
            addMessage('assistant', `Error: ${data.error}`);
        } else {
            addMessage('assistant', data.answer);
        }
    } catch (error) {
        addMessage('assistant', `Error: ${error.message}`);
    } finally {
        hideLoading();
    }
}

function addMessage(sender, content) {
    const welcomeHero = chatMessages.querySelector('.welcome-hero');
    if (welcomeHero) welcomeHero.remove();
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const label = document.createElement('div');
    label.className = 'message-label';
    label.textContent = sender === 'user' ? 'You' : 'Assistant';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    
    messageDiv.appendChild(label);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Smooth scroll
    chatMessages.scrollTo({
        top: chatMessages.scrollHeight,
        behavior: 'smooth'
    });
}

function addSummaryCard(summary) {
    const welcomeHero = chatMessages.querySelector('.welcome-hero');
    if (welcomeHero) welcomeHero.remove();
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    
    const label = document.createElement('div');
    label.className = 'message-label';
    label.textContent = 'Dataset Summary';
    
    const card = document.createElement('div');
    card.className = 'summary-card';
    
    const text = document.createElement('p');
    text.textContent = summary;
    
    card.appendChild(text);
    messageDiv.appendChild(label);
    messageDiv.appendChild(card);
    chatMessages.appendChild(messageDiv);
    
    chatMessages.scrollTo({
        top: chatMessages.scrollHeight,
        behavior: 'smooth'
    });
}

function showLoading() {
    loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    loadingOverlay.style.display = 'none';
}
