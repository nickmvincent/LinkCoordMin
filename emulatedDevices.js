
const devices = require('puppeteer/DeviceDescriptors');


// common web browser, platform, and screen resolutions: https://www.w3counter.com/globalstats.php
// user agents: https://www.whatismybrowser.com/guides/the-latest-user-agent/chrome

module.exports = {
    'iphonex': devices['iPhone X'],
    'galaxys5': devices['Galaxy S5'],
    'chromewindows': {
        name: 'Chrome on Windows',
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        viewport: {
            width: 1024, 
            height: 768,
        },
    },
    'chromemac': {
        name: 'Chrome on Mac',
        userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        viewport: {
            width: 1024,
            height: 768,
        },
    },
};