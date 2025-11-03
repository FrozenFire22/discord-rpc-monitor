// YouTube content script - With proper chapter detection
// Uses YouTube player's built-in chapter element

console.log('[YouTube RPC] Content.js loaded');

let lastSentTime = '';

function formatTime(seconds) {
    if (isNaN(seconds) || seconds < 0) return '0:00';
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    if (hrs > 0) return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function stripParens(text) {
    return text.replace(/\s*\([^)]*\)/g, '').trim();
}

function getChapter() {
    try {
        // YouTube player chapter title element
        const el = document.querySelector('.ytp-chapter-title-content, .ytp-chapter-title');
        if (!el) {
            return '';
        }
        
        let t = el.textContent.trim()
            .replace(/^•\s*/, '')
            .replace(/^(\d+\.)\s*/, '$1 ')
            .replace(/["""'']/g, '');
        
        t = stripParens(t).trim();
        if (t.length > 0) {
            console.log(`[YouTube] Chapter found: ${t}`);
            return t;
        }
        
        return '';
    } catch (e) {
        console.error('[YouTube] Chapter error:', e);
        return '';
    }
}

function getChannel() {
    try {
        // Try multiple selectors
        const selectors = [
            '#owner-name a',
            'ytd-channel-name#channel-name yt-formatted-string',
            '#text-container yt-formatted-string',
            'ytd-channel-name a#channel-name',
            'a#owner-name',
            'ytd-channel-name a'
        ];
        
        for (const sel of selectors) {
            const el = document.querySelector(sel);
            if (el && el.textContent.trim()) {
                const text = el.textContent.trim();
                if (text.length > 0) {
                    return text;
                }
            }
        }
        
        return '';
    } catch (e) {
        return '';
    }
}

function getData() {
    try {
        const video = document.querySelector('video');
        if (!video || isNaN(video.duration) || video.duration === 0) {
            return null;
        }
        
        const chapter = getChapter();
        const channel = getChannel();
        
        return {
            currentTime: formatTime(video.currentTime),
            duration: formatTime(video.duration),
            chapter: chapter,
            channel: channel,
            title: document.title,
            url: window.location.href
        };
    } catch (e) {
        return null;
    }
}

// Respond to background.js requests
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getMetadata') {
        const data = getData();
        if (data) {
            sendResponse({
                chapter: data.chapter,
                channel: data.channel,
                currentTime: data.currentTime,
                duration: data.duration
            });
        } else {
            sendResponse({ chapter: '', channel: '', currentTime: '0:00', duration: '0:00' });
        }
    }
});

// Send own updates every 500ms
setInterval(() => {
    try {
        const data = getData();
        if (!data) return;
        
        // Always send (no comparison check)
        fetch('http://localhost:5000/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).catch(() => {});
        
    } catch (e) {}
}, 500);

console.log('[YouTube] Ready - chapter detection active');
