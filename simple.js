'use strict';
const puppeteer = require('puppeteer');
const fs = require('fs');
const mkdirp = require('mkdirp');
const devices = require('puppeteer/DeviceDescriptors');
const utils = require('./utils');


const outDir = 'output';
let curDir = '';

const scrape = async (link, isMobile) => {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.setViewport({
        width: 1440, //13 in full screen firefox
        height: 806,
    });
    if (isMobile) {
        await page.emulate(devices['iPhone X']);
        curDir = `${outDir}/mobile`;
    } else {
        curDir = `${outDir}/desktop`;
    }
    mkdirp(curDir);
    await page.goto(link);
    await utils.sleep(1000);
    await utils.scrollDown(page);
    await page.screenshot({
        path: `${curDir}/full.png`,
        fullPage: true
    });
    
    const links = await page.$$eval('a', utils.getPos);
    await browser.close();
    return links;
}

const link = 'https://www.nytimes.com/';
const results = {};
(async () => {
    results[link] = {}
    results[link]['desktop'] = await scrape(link, false);
    results[link]['mobile'] = await scrape(link, true);

    const json = JSON.stringify(results);
    fs.writeFile(`${outDir}/links.json`, json, 'utf8', () => console.log('printed'));
})();