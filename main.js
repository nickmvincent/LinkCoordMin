'use strict';
const puppeteer = require('puppeteer');
const fs = require('fs');
const mkdirp = require('mkdirp');
// utilities: get <a> positions, sleep, scrollDown, random interval
const utils = require('./utils');
// default mobile devices and custom "desktop devices"
const emulatedDevices = require('./emulatedDevices');


const outDir = 'output';
const sleepRange = [15, 30];
let curDir = '';


const myArgs  = process.argv.slice(2);
let devicesSelected = [];
if (myArgs[0] == 'allDevices'){
    console.log('Using all devices specifide in emulatedDevices.js');
    for (const key of Object.keys(emulatedDevices)) {
        devicesSelected.push(emulatedDevices[key]);
        console.log(emulatedDevices[key]);
    }
} else {
    devicesSelected.push(emulatedDevices[myArgs[0]])
}
const platform = myArgs[1];
const queryCat = myArgs[2];
const queryFile = myArgs[3];

const target_file = `search_queries/prepped/${queryCat}/${queryFile}.txt`;
const text = fs.readFileSync(target_file, "utf-8");
const targets = text.split("\n").filter(Boolean);// removes empty strings

/*=====
If we are scraping search engines, we need to make our keywords into URLs
If we are scraping other sites, the "keywords" should already be full urls
=====*/
let startStr = '';
if (['google', 'bing', 'duckduckgo'].includes(platform)) {
    startStr = {
        google: 'https://www.google.com/search?q=',
        bing: 'https://www.bing.com/search?q=',
        duckduckgo: 'https://www.duckduckgo.com/?q=',
    }[platform]
}
const links = [];
for (const x of targets) {
    links.push(`${startStr}${x}`);
}

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

console.log(devicesSelected);
const results = {};
(async () => {
    const date = new Date();
    const dateStr = date.toString().replace(/:/g, '-');
    for await (const device of devicesSelected) {
        results[device.name] = {};
        for await (const link of links) {
            const ret = await scrape(link, device, dateStr);
            results[device.name][link] = {};
            results[ret.device.name][ret.link][ret.dateStr] = ret.links;
            const sleepSecs = utils.randomIntFromInterval(sleepRange[0], sleepRange[1]);
            console.log(`Sleeping for ${sleepSecs} seconds!`);
            await utils.sleep(sleepSecs * 1000);
        }
    }
    const json = JSON.stringify(results);
    const curDir = `${outDir}/${dateStr}`;
    mkdirp(curDir);
    fs.writeFile(`${curDir}/links.json`, json, 'utf8', () => console.log('Finished collecting data!'));
})();