// ==UserScript==
// @name         YouTube Chapter to Discord RPC (Tab Focus Only)
// @namespace    http://tampermonkey.net/
// @version      2.0
// @description  Sends YouTube chapters to Discord RPC ONLY when YouTube tab is in focus
// @match        *://www.youtube.com/watch*
// @grant        GM_xmlhttpRequest
// @run-at       document-start
// ==/UserScript==

(function() {
    'use strict';

    let lastChapter = '';
    let lastData = null;
    let tabVisible = true;

    // Detect when tab becomes visible/hidden
    document.addEventListener('visibilitychange', function() {
        tabVisible = !document.hidden;
        console.log('[Tampermonkey] YouTube tab ' + (tabVisible ? 'focused' : 'hidden'));
    });

    function getChapter() {
        try {
            const el = document.querySelector('.ytp-chapter-title-content, .ytp-chapter-title');
            if (!el) return '';

            let t = el.textContent.trim()
                .replace(/^•\s*/, '')
                .replace(/^(\d+\.)\s*/, '$1 ')
                .replace(/["""'']/g, '');

            t = t.replace(/\s*\([^)]*\)/g, '').trim();
            return t;
        } catch (e) {
            return '';
        }
    }

    function getChannel() {
        try {
            const selectors = [
                '#owner-name a',
                'ytd-channel-name a#channel-name',
                'a#owner-name',
                'ytd-channel-name a'
            ];

            for (const sel of selectors) {
                const el = document.querySelector(sel);
                if (el) {
                    const text = el.textContent.trim();
                    if (text.length > 0) return text;
                }
            }
            return '';
        } catch (e) {
            return '';
        }
    }

    function formatTime(seconds) {
        if (isNaN(seconds) || seconds < 0) return '0:00';
        const hrs = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        if (hrs > 0) return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    function sendUpdate() {
        try {
            const video = document.querySelector('video');
            if (!video || isNaN(video.duration) || video.duration === 0) return;

            const currentTime = formatTime(video.currentTime);
            const duration = formatTime(video.duration);
            const chapter = getChapter();
            const channel = getChannel();
            const title = document.title;
            const url = window.location.href;

            // Store data regardless of tab visibility
            lastData = {
                title: title,
                url: url,
                chapter: chapter,
                channel: channel,
                currentTime: currentTime,
                duration: duration
            };

            // ONLY SEND if tab is visible (focused)
            if (tabVisible && chapter !== lastChapter) {
                lastChapter = chapter;
                console.log(`[Tampermonkey] Sending update (tab visible): Chapter: ${chapter || '(none)'}`);

                GM_xmlhttpRequest({
                    method: 'POST',
                    url: 'http://localhost:5000/update',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    data: JSON.stringify(lastData),
                    onload: () => {
                        console.log('[Tampermonkey] Update sent');
                    },
                    onerror: (err) => {
                        console.error('[Tampermonkey] Error:', err);
                    }
                });
            } else if (!tabVisible) {
                console.log('[Tampermonkey] Tab hidden - data stored but not sent');
            }
        } catch (e) {
            console.error('[Tampermonkey] Error:', e);
        }
    }

    // Check every 500ms
    setInterval(sendUpdate, 500);

    // When tab becomes visible again, send one update
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden && lastData) {
            console.log('[Tampermonkey] Tab refocused - sending stored data');
            GM_xmlhttpRequest({
                method: 'POST',
                url: 'http://localhost:5000/update',
                headers: {
                    'Content-Type': 'application/json'
                },
                data: JSON.stringify(lastData),
                onload: () => {
                    console.log('[Tampermonkey] Refocus update sent');
                },
                onerror: (err) => {
                    console.error('[Tampermonkey] Refocus error:', err);
                }
            });
        }
    });

    console.log('[Tampermonkey] YouTube Chapter RPC (Tab Focus Mode) loaded');
})();
