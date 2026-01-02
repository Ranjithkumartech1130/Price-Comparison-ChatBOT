let currentMode = 'general';
let chatHistory = [];
const API_BASE = 'http://localhost:8000/api';

document.addEventListener('DOMContentLoaded', () => {
    const apiKeyInput = document.getElementById('apiKeyInput');
    const storedKey = localStorage.getItem('gemini_api_key');
    if (storedKey) apiKeyInput.value = storedKey;

    apiKeyInput.addEventListener('change', (e) => {
        localStorage.setItem('gemini_api_key', e.target.value);
    });

    document.getElementById('generalBtn').addEventListener('click', () => setMode('general'));
    document.getElementById('priceBtn').addEventListener('click', () => setMode('price'));

    document.getElementById('sendBtn').addEventListener('click', sendMessage);
    document.getElementById('chatInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // Initial greeting
    addMessage('bot', "Hello! I'm your AI Assistant. You can chat with me generally, or switch to the 'Price Comparison' tab to search for products across the web.");
});

function setMode(mode) {
    currentMode = mode;
    document.getElementById('generalBtn').classList.toggle('active', mode === 'general');
    document.getElementById('priceBtn').classList.toggle('active', mode === 'price');

    document.getElementById('headerTitle').innerText = mode === 'general' ? 'General AI Chat' : 'Price Comparison';

    // Clear chat or keep it separate? User often likes context switch.
    // For simplicity, we just clear visuals to show separation of concern, 
    // or we could just append a system message "Switched to...".
    // Let's clear to avoid confusion.
    const container = document.getElementById('messages');
    container.innerHTML = '';

    if (mode === 'general') {
        addMessage('bot', "Switched to General Chat. How can I help you?");
    } else {
        addMessage('bot', "Switched to Price Comparison. Enter a product name (e.g., 'Sony WH-1000XM5 headphones') to compare prices.");
    }
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    const apiKey = localStorage.getItem('gemini_api_key');

    // Check local storage, but don't block if missing because server has env key

    if (!message) return;

    addMessage('user', message);
    input.value = '';

    // Show loading
    const loadingId = addMessage('bot', '<div class="spinner"></div>', true);

    try {
        let response;
        const headers = { 'Content-Type': 'application/json' };

        if (currentMode === 'general') {
            response = await fetch(`${API_BASE}/chat/general`, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({
                    message: message,
                    api_key: apiKey || null, // Pass null if empty so backend decides
                    history: chatHistory
                })
            });
        } else {
            response = await fetch(`${API_BASE}/chat/price`, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({
                    query: message,
                    api_key: apiKey || null
                })
            });
        }

        const data = await response.json();

        // Remove loading
        const loadingEl = document.getElementById(loadingId);
        if (loadingEl) loadingEl.remove();

        if (currentMode === 'general') {
            addMessage('bot', data.response);
            chatHistory.push({ role: 'user', content: message });
            chatHistory.push({ role: 'model', content: data.response });
        } else {
            // Price Comparison Format
            addMessage('bot', data.response);
            if (data.data && data.data.length > 0) {
                renderProducts(data.data);
            }
        }

    } catch (error) {
        const loadingEl = document.getElementById(loadingId);
        if (loadingEl) loadingEl.remove();
        addMessage('bot', `Error: ${error.message}. Is the backend running?`);
    }
}

function addMessage(role, content, isHtml = false) {
    const container = document.getElementById('messages');
    const div = document.createElement('div');
    div.className = `message ${role}`;
    div.id = 'msg-' + Date.now();

    if (isHtml) {
        div.innerHTML = content;
    } else {
        // Simple markdown parsing for bold/italic/code
        // We can use marked.js if we include it
        if (typeof marked !== 'undefined') {
            div.innerHTML = marked.parse(content);
        } else {
            div.innerText = content;
        }
    }

    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return div.id;
}

function renderProducts(products) {
    const container = document.getElementById('messages');
    const grid = document.createElement('div');
    grid.className = 'price-grid';

    products.forEach(p => {
        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `
            <div class="product-source">${p.source}</div>
            <div class="product-title">${p.title}</div>
            <div class="product-price">${p.price}</div>
            <a href="${p.link}" target="_blank" class="product-link">View Deal</a>
        `;
        grid.appendChild(card);
    });

    container.appendChild(grid);
    container.scrollTop = container.scrollHeight;
}
