'use strict';
const puppeteer = require('puppeteer');
const fs = require('fs');
const mkdirp = require('mkdirp');
const devices = require('puppeteer/DeviceDescriptors');
const utils = require('./utils');


const outDir = 'output';
let curDir = '';

const scrape = async (link, device, dateStr) => {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.emulate(device);
    const niceLink = link.replace(/\//g, "-").replace(/:/g, '-');
    curDir = `${outDir}/${device.name}/${niceLink}`;
    mkdirp(curDir);
    await page.goto(link);
    await utils.sleep(1000);
    await utils.scrollDown(page);
    
    console.log(`${curDir}/${dateStr}.png`);
    await page.screenshot({
        path: `${curDir}/${dateStr}.png`,
        fullPage: true
    });
    
    const links = await page.$$eval('a', utils.getPos);
    await browser.close();
    return {
        links, device, link, dateStr
    }
}

const links = [
    //'https://www.nytimes.com/',
    'https://www.google.com/search?q=basketball',
    'https://www.bing.com/search?q=basketball',
];


// common web browser, platform, and screen resolutions: https://www.w3counter.com/globalstats.php
// user agents: https://www.whatismybrowser.com/guides/the-latest-user-agent/chrome
const emulatedDevices = [
    devices['iPhone X'],
    //devices['Galaxy S5'],
    {
        name: 'Chrome on Windows',
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        viewport: {
            width: 1024, 
            height: 768,
        }
    },
    {
        name: 'Chrome on Mac',
        userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        viewport: {
            width: 1024,
            height: 768,
        },
    },
];
// todo add delays between calls.
const results = {};
(async () => {
    const date = new Date();
    const dateStr = date.toString().replace(/:/g, '-');
    const promises = [];
    for await (const device of emulatedDevices) {
        results[device.name] = {};
        for await (const link of links) {
            /*results[device.name][link] = {};
            promises.push(scrape(link, device, dateStr));*/
            const ret = await scrape(link, device, dateStr);
            results[device.name][link] = {};
            results[ret.device.name][ret.link][ret.dateStr] = ret.links;
        }
    }
    /*await Promise.all(promises).then(rets => {
        for (const ret of rets) {
            results[ret.device.name][ret.link][ret.dateStr] = ret.links;
        };
    });*/
    const json = JSON.stringify(results);
    const curDir = `${outDir}/${dateStr}`;
    mkdirp(curDir);
    fs.writeFile(`${curDir}/links.json`, json, 'utf8', () => console.log('Finished collecting data!'));
})();