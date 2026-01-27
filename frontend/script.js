/**
 * Frontend script for Price Comparison Chatbot.
 * Handles API communication and UI updates.
 */
let currentMode = 'general';
let chatHistory = [];
const API_BASE = 'http://localhost:8000/api';

// Location tracking
let userLocation = null;
let locationPermissionGranted = false;

// Basic country detection using timezone (Privacy friendly)
function detectCountry() {
    try {
        const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        if (timeZone.includes("Calcutta") || timeZone.includes("Kolkata") || timeZone.includes("India")) {
            return "IN";
        }
    } catch (e) { }
    return "US";
}

let userCountry = "US";

document.addEventListener('DOMContentLoaded', () => {
    userCountry = detectCountry();
    // Update Online status with country
    const statusText = document.querySelector('.header-status');
    if (statusText) {
        statusText.innerHTML = `<div class="dot"></div> Online (${userCountry})`;
    }

    const apiKeyInput = document.getElementById('apiKeyInput');
    const storedKey = localStorage.getItem('gemini_api_key');
    if (storedKey) apiKeyInput.value = storedKey;

    apiKeyInput.addEventListener('change', (e) => {
        localStorage.setItem('gemini_api_key', e.target.value);
    });

    document.getElementById('generalBtn').addEventListener('click', () => setMode('general'));
    document.getElementById('priceBtn').addEventListener('click', () => setMode('price'));
    document.getElementById('nearbyBtn').addEventListener('click', () => setMode('nearby'));

    document.getElementById('sendBtn').addEventListener('click', sendMessage);
    document.getElementById('clearBtn').addEventListener('click', clearChat);
    document.getElementById('chatInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // Initial greeting
    addMessage('bot', `Hello! I've detected your location as <strong>${userCountry}</strong>. I'll customize price comparisons for you.`);
});

function setMode(mode) {
    currentMode = mode;
    document.getElementById('generalBtn').classList.toggle('active', mode === 'general');
    document.getElementById('priceBtn').classList.toggle('active', mode === 'price');
    document.getElementById('nearbyBtn').classList.toggle('active', mode === 'nearby');

    let headerTitle = 'General AI Chat';
    if (mode === 'price') headerTitle = 'Price Comparison';
    if (mode === 'nearby') headerTitle = 'Nearby Stores';

    document.getElementById('headerTitle').innerText = headerTitle;

    const container = document.getElementById('messages');
    container.innerHTML = '';

    if (mode === 'general') {
        addMessage('bot', "Switched to General Chat. How can I help you?");
    } else if (mode === 'price') {
        addMessage('bot', "Switched to Price Comparison. Enter a product name (e.g., 'Sony WH-1000XM5 headphones') to compare prices.");
    } else if (mode === 'nearby') {
        requestLocationAccess();
    }
}

function requestLocationAccess() {
    addMessage('bot', `<div class="location-request">
        <i class="fas fa-map-marker-alt" style="font-size: 2em; color: var(--primary); margin-bottom: 10px;"></i>
        <h3>Enable Location Access</h3>
        <p>To find nearby stores, I need your location.</p>
        <div class="location-buttons" style="display:flex; gap:10px; justify-content:center; margin-top:15px;">
            <button onclick="getLocation()" class="location-btn">
                <i class="fas fa-location-arrow"></i> Auto-Detect
            </button>
            <button onclick="showManualLocationInput()" class="location-btn secondary" style="background:transparent; border:1px solid var(--primary); color:var(--text);">
                <i class="fas fa-search"></i> Enter Manually
            </button>
        </div>
    </div>`, true);
}

function getLocation() {
    if (!navigator.geolocation) {
        addMessage('bot', '❌ Geolocation is not supported by your browser. Please use a modern browser like Chrome, Firefox, or Safari.');
        return;
    }

    addMessage('bot', '<div class="spinner"></div> Getting your location...', true);

    navigator.geolocation.getCurrentPosition(
        (position) => {
            userLocation = {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
                accuracy: position.coords.accuracy
            };
            locationPermissionGranted = true;

            // Remove loading message
            const messages = document.getElementById('messages');
            const lastMsg = messages.lastElementChild;
            if (lastMsg && lastMsg.innerHTML.includes('spinner')) {
                lastMsg.remove();
            }

            // Use shared function
            showLocationControls();
        },
        (error) => {
            let errorMsg = '';
            switch (error.code) {
                case error.PERMISSION_DENIED:
                    errorMsg = '❌ Location access denied. Please enable location permissions in your browser settings and try again.';
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMsg = '❌ Location information is unavailable. Please check your device settings.';
                    break;
                case error.TIMEOUT:
                    errorMsg = '❌ Location request timed out. Please try again.';
                    break;
                default:
                    errorMsg = '❌ An unknown error occurred while getting your location.';
            }

            // Remove loading message
            const messages = document.getElementById('messages');
            const lastMsg = messages.lastElementChild;
            if (lastMsg && lastMsg.innerHTML.includes('spinner')) {
                lastMsg.remove();
            }

            addMessage('bot', errorMsg);
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}

function updateDistanceDisplay() {
    const minDist = document.getElementById('minDistance');
    const maxDist = document.getElementById('maxDistance');
    const minVal = document.getElementById('minDistValue');
    const maxVal = document.getElementById('maxDistValue');

    if (minDist && maxDist && minVal && maxVal) {
        minVal.textContent = minDist.value;
        maxVal.textContent = maxDist.value;

        // Ensure min is always less than max
        if (parseInt(minDist.value) >= parseInt(maxDist.value)) {
            maxDist.value = parseInt(minDist.value) + 1;
            maxVal.textContent = maxDist.value;
        }
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
        } else if (currentMode === 'price') {
            response = await fetch(`${API_BASE}/chat/price`, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({
                    query: message,
                    api_key: apiKey || null,
                    country_code: userCountry
                })
            });
        } else if (currentMode === 'nearby') {
            // Check if location is available
            if (!userLocation) {
                const loadingEl = document.getElementById(loadingId);
                if (loadingEl) loadingEl.remove();
                addMessage('bot', '❌ Please allow location access first by clicking the "Allow Location Access" button above.');
                return;
            }

            // Get distance range from sliders
            const minDistance = document.getElementById('minDistance')?.value || 0;
            const maxDistance = document.getElementById('maxDistance')?.value || 25;

            response = await fetch(`${API_BASE}/chat/nearby-stores`, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({
                    query: message,
                    latitude: userLocation.latitude,
                    longitude: userLocation.longitude,
                    min_distance: parseFloat(minDistance),
                    max_distance: parseFloat(maxDistance),
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
        } else if (currentMode === 'price') {
            // Price Comparison Format
            addMessage('bot', data.response);
            if (data.data && data.data.length > 0) {
                renderProducts(data.data);
            }
        } else if (currentMode === 'nearby') {
            // Nearby Stores Format
            addMessage('bot', data.response);
            if (data.data && data.data.length > 0) {
                renderNearbyStores(data.data);
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

    if (role === 'bot' && !isHtml) {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-btn';
        copyBtn.innerHTML = '<i class="far fa-copy"></i>';
        copyBtn.title = 'Copy to clipboard';
        copyBtn.onclick = () => {
            navigator.clipboard.writeText(content);
            copyBtn.innerHTML = '<i class="fas fa-check"></i>';
            setTimeout(() => { copyBtn.innerHTML = '<i class="far fa-copy"></i>'; }, 2000);
        };
        div.appendChild(copyBtn);
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

        let estimateHtml = p.is_estimate ?
            `<div class="estimate-badge"><i class="fas fa-info-circle"></i> Market Est.</div>` : '';

        // If we have an approximate conversion, show it
        if (p.approx_price) {
            estimateHtml += `<div class="estimate-badge" style="color:var(--primary)"><i class="fas fa-exchange-alt"></i> Approx ${p.approx_price}</div>`;
        }

        // Shipping Info
        const shippingHtml = p.shipping ? `<div class="shipping-info">${p.shipping}</div>` : '';

        const buttonText = p.is_estimate ? "Search Store" : "View Deal";
        const buttonIcon = p.is_estimate ? '<i class="fas fa-search"></i>' : '<i class="fas fa-external-link-alt"></i>';

        card.innerHTML = `
            <div class="product-source">${p.source}</div>
            <div class="product-title">${p.title}</div>
            <div class="product-price">
                ${p.price}
                <div style="font-size: 0.6em; font-weight: 400; opacity: 0.8">${shippingHtml}</div>
                ${estimateHtml}
            </div>
            <a href="${p.link}" target="_blank" class="product-link">${buttonIcon} ${buttonText}</a>
        `;
        grid.appendChild(card);
    });

    container.appendChild(grid);
    container.scrollTop = container.scrollHeight;
}

function renderNearbyStores(stores) {
    const container = document.getElementById('messages');

    // Check if data is simulated
    const isSimulated = stores.length > 0 && stores[0].is_real_data === false;

    if (isSimulated) {
        const warning = document.createElement('div');
        warning.className = 'demo-warning';
        warning.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <strong>Demo Mode:</strong> Showing simulated stores. 
            <br>Addresses are random. Configure Google Places API for real data.
        `;
        container.appendChild(warning);
    }

    const grid = document.createElement('div');
    grid.className = 'store-grid';

    stores.forEach(store => {
        const card = document.createElement('div');
        card.className = 'store-card';
        if (isSimulated) card.classList.add('simulated');


        // Stock level badge
        const stockClass = store.stock_level?.toLowerCase().includes('in stock') ? 'in-stock' : 'low-stock';
        const stockBadge = store.stock_level ?
            `<div class="stock-badge ${stockClass}"><i class="fas fa-box"></i> ${store.stock_level}</div>` : '';

        // Open/Closed status
        let statusBadge = '';
        if (store.open_now !== null) {
            statusBadge = store.open_now ?
                '<div class="status-badge open"><i class="fas fa-door-open"></i> Open Now</div>' :
                '<div class="status-badge closed"><i class="fas fa-door-closed"></i> Closed</div>';
        }

        // Rating display
        const ratingHtml = store.rating ?
            `<div class="store-rating">
                <i class="fas fa-star"></i> ${store.rating} 
                <span style="opacity: 0.6;">(${store.total_ratings} reviews)</span>
            </div>` : '';

        // Distance badge
        const distanceBadge = `<div class="distance-badge">
            <i class="fas fa-map-marker-alt"></i> ${store.distance} km away
        </div>`;

        // Price if available
        const priceHtml = store.price ?
            `<div class="store-price"><i class="fas fa-tag"></i> ${store.price}</div>` : '';

        // Map link
        const mapUrl = `https://www.google.com/maps/search/?api=1&query=${store.latitude},${store.longitude}`;

        card.innerHTML = `
            <div class="store-header">
                <div class="store-name">${store.name}</div>
                ${distanceBadge}
            </div>
            <div class="store-address"><i class="fas fa-location-dot"></i> ${store.address}</div>
            ${ratingHtml}
            ${priceHtml}
            <div class="store-badges">
                ${stockBadge}
                ${statusBadge}
            </div>
            <div class="store-actions">
                <a href="${mapUrl}" target="_blank" class="store-btn map-btn">
                    <i class="fas fa-map"></i> View on Map
                </a>
                ${store.phone !== 'N/A' ? `
                    <a href="tel:${store.phone}" class="store-btn phone-btn">
                        <i class="fas fa-phone"></i> Call
                    </a>
                ` : ''}
                ${store.website !== 'N/A' ? `
                    <a href="${store.website}" target="_blank" class="store-btn website-btn">
                        <i class="fas fa-globe"></i> Website
                    </a>
                ` : ''}
            </div>
        `;
        grid.appendChild(card);
    });

    container.appendChild(grid);
    container.scrollTop = container.scrollHeight;
}



function clearChat() {
    const container = document.getElementById('messages');
    container.innerHTML = '';
    chatHistory = [];
    addMessage('bot', "Chat cleared. How can I help you?");
}

// Manual Location Functions

function showManualLocationInput() {
    addMessage('bot', `<div class="manual-location-form">
        <h4>Enter Your Location</h4>
        <div class="input-group">
            <input type="text" id="manualLocationInput" placeholder="City, Zip, or Address..." onkeypress="handleLocationKey(event)">
            <button onclick="searchManualLocation()">Search</button>
        </div>
    </div>`, true);
}

function handleLocationKey(e) {
    if (e.key === 'Enter') searchManualLocation();
}

async function searchManualLocation() {
    const query = document.getElementById('manualLocationInput').value;
    if (!query) return;

    addMessage('bot', '<div class="spinner"></div> Finding location...', true);

    try {
        const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (data && data.length > 0) {
            const loc = data[0];
            userLocation = {
                latitude: parseFloat(loc.lat),
                longitude: parseFloat(loc.lon),
                accuracy: 0,
                displayName: loc.display_name
            };
            locationPermissionGranted = true;

            // Remove spinner
            const msgs = document.getElementById('messages');
            if (msgs.lastElementChild.innerHTML.includes('spinner')) msgs.lastElementChild.remove();

            showLocationControls(userLocation.displayName);
        } else {
            addMessage('bot', '❌ Location not found. Please try a different query.');
        }
    } catch (e) {
        console.error(e);
        addMessage('bot', '❌ Error finding location. Please try again.');
    }
}

function showLocationControls(addressOverride = null) {
    let addressDisplay = addressOverride || "Fetching address...";

    // If we have a stored displayName in userLocation, use it
    if (!addressOverride && userLocation.displayName) {
        addressDisplay = userLocation.displayName.split(',').slice(0, 3).join(',');
    }

    const uiHtml = `✅ Location set!<br>
        <div class="location-details" style="background: rgba(var(--primary-rgb), 0.1); padding: 10px; border-radius: 8px; margin-bottom: 10px; font-size: 0.9em;">
            <i class="fas fa-map-pin"></i> <strong>Current:</strong> <span id="locAddress">${addressDisplay}</span>
            <button class="edit-loc-btn" onclick="requestLocationAccess()" style="background:none; border:none; cursor:pointer; color:var(--primary); margin-left:10px;" title="Change Location"><i class="fas fa-edit"></i> Change</button>
        </div>

        <div class="distance-controls">
            <h4>Search Distance Range</h4>
            <div class="distance-slider-container">
                <label>Minimum: <span id="minDistValue">0</span> km</label>
                <input type="range" id="minDistance" min="0" max="20" value="0" step="1" oninput="updateDistanceDisplay()">
            </div>
            <div class="distance-slider-container">
                <label>Maximum: <span id="maxDistValue">25</span> km</label>
                <input type="range" id="maxDistance" min="5" max="50" value="25" step="1" oninput="updateDistanceDisplay()">
            </div>
        </div>

        Now enter a product name to find nearby stores!`;

    addMessage('bot', uiHtml, true);

    if (!addressOverride && !userLocation.displayName) {
        // Fetch address if not provided (Auto-detect case)
        fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${userLocation.latitude}&lon=${userLocation.longitude}`)
            .then(r => r.json())
            .then(d => {
                const addr = d.display_name.split(',').slice(0, 3).join(',');
                userLocation.displayName = d.display_name; // Store full name
                const addrEl = document.getElementById('locAddress');
                if (addrEl) addrEl.innerText = addr;
            })
            .catch(e => {
                const addrEl = document.getElementById('locAddress');
                if (addrEl) addrEl.innerText = `${userLocation.latitude.toFixed(4)}, ${userLocation.longitude.toFixed(4)}`;
            });
    }
}
