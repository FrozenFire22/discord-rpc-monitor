// ==UserScript==
// @name         Discord Channel Info to RPC
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Sends current Discord channel/server to localhost:5000
// @match        *://discord.com/*
// @grant        GM_xmlhttpRequest
// @run-at       document-start
// ==/UserScript==

(function() {
    'use strict';

    let lastChannelInfo = '';

    function getDiscordContext() {
        try {
            // Try to get channel name from DOM
            let channelName = '';

            // Try multiple selectors for channel name
            let elem = document.querySelector('[aria-label*="channel"]');
            if (elem) {
                channelName = elem.textContent.trim();
            }

            if (!channelName) {
                elem = document.querySelector('.theme-light [role="heading"]');
                if (elem) {
                    channelName = elem.textContent.trim();
                }
            }

            if (!channelName) {
                elem = document.querySelector('[class*="header"]');
                if (elem) {
                    channelName = elem.textContent.trim();
                }
            }

            // Try to get server name
            let serverName = '';
            elem = document.querySelector('[aria-label*="Server guide"]');
            if (elem) {
                serverName = elem.textContent.trim();
            }

            if (!serverName) {
                elem = document.querySelector('nav [role="button"]');
                if (elem) {
                    serverName = elem.getAttribute('aria-label') || elem.textContent.trim();
                }
            }

            const context = channelName || serverName || document.title;
            return context.substring(0, 100);
        } catch (e) {
            return document.title;
        }
    }

    function sendChannelInfo() {
        try {
            const context = getDiscordContext();

            // Only send if changed
            if (context === lastChannelInfo) return;
            lastChannelInfo = context;

            console.log('[Discord RPC] Current channel: ' + context);

            GM_xmlhttpRequest({
                method: 'POST',
                url: 'http://localhost:5000/discord-context',
                headers: {
                    'Content-Type': 'application/json'
                },
                data: JSON.stringify({
                    context: context,
                    title: document.title
                }),
                onload: () => {
                    console.log('[Discord RPC] Context sent');
                },
                onerror: (err) => {
                    console.error('[Discord RPC] Error:', err);
                }
            });
        } catch (e) {
            console.error('[Discord RPC] Error:', e);
        }
    }

    // Check every 1 second
    setInterval(sendChannelInfo, 1000);

    console.log('[Discord RPC] Channel info sender loaded');
})();