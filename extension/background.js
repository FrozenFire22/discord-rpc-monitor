// Background script - Always send data, even when not focused
// This keeps Discord updated even when switching tabs

console.log('[Discord RPC] Background.js loaded');

async function sendToServer(title, url, chapter = '', channel = '', currentTime = '0:00', duration = '0:00') {
    try {
        await fetch('http://localhost:5000/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, url, chapter, channel, currentTime, duration })
        });
    } catch (error) {
        // Silently fail
    }
}

async function getMetadataFromContent(tabId, url) {
    if (!url.includes('youtube.com')) {
        return { chapter: '', channel: '', currentTime: '0:00', duration: '0:00' };
    }
    
    return new Promise((resolve) => {
        try {
            chrome.tabs.sendMessage(tabId, { action: 'getMetadata' }, { frameId: 0 }, (response) => {
                if (chrome.runtime.lastError) {
                    resolve({ chapter: '', channel: '', currentTime: '0:00', duration: '0:00' });
                } else {
                    resolve(response || { chapter: '', channel: '', currentTime: '0:00', duration: '0:00' });
                }
            });
        } catch (error) {
            resolve({ chapter: '', channel: '', currentTime: '0:00', duration: '0:00' });
        }
    });
}

async function updateYouTube() {
    try {
        // Query for YouTube tab (any YouTube tab, not just active)
        const tabs = await new Promise((resolve) => {
            chrome.tabs.query({ url: '*://*.youtube.com/*' }, resolve);
        });
        
        if (tabs.length === 0) return;
        
        // Send from ALL YouTube tabs (not just active one)
        for (const tab of tabs) {
            try {
                const metadata = await getMetadataFromContent(tab.id, tab.url);
                await sendToServer(tab.title, tab.url, metadata.chapter, metadata.channel, metadata.currentTime, metadata.duration);
            } catch (e) {
                // Continue to next tab
            }
        }
        
    } catch (error) {
        // Silently fail
    }
}

async function updateOtherTabs() {
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (!tab || !tab.url) return;
        
        // Skip YouTube - it's handled by updateYouTube
        if (tab.url.includes('youtube.com')) return;
        
        if (tab.url.startsWith('chrome://') || tab.url.startsWith('chrome-extension://')) return;

        await sendToServer(tab.title || 'Unknown', tab.url);

    } catch (error) {
        // Silently fail
    }
}

async function updateAll() {
    await updateYouTube();
    await updateOtherTabs();
}

// Tab changed
chrome.tabs.onActivated.addListener(updateAll);

// Tab updated
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' || changeInfo.title) {
        updateAll();
    }
});

// Send EVERY 1 second - ALWAYS
setInterval(updateAll, 1000);

// Handle messages from content.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getMetadata') {
        sendResponse(request);
    }
});

console.log('[Discord RPC] Ready - sending every 1 second');
