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
for (const target of targets) {
    links.push({
        platform,
        target,
        link: `${startStr}${target}`,
    });
}

const scrape = async (linkObj, device, dateStr, queryCat, queryFile) => {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.emulate(device);
    const niceLink = linkObj.link.replace(/\//g, "-").replace(/:/g, '-'); // (nice for Windows filesystem)
    curDir = `${outDir}/${device.name}/${niceLink}`;
    mkdirp(curDir);
    await page.goto(linkObj.link);
    await utils.sleep(1000);
    await utils.scrollDown(page);
    
    const niceDateStr = dateStr.replace(/:/g, '-'); // (nice for Windows filesystem)
    const pngPath = `${curDir}/${niceDateStr}.png`
    console.log(pngPath);
    await page.screenshot({
        path: pngPath,
        fullPage: true
    });
    
    const linkElements = await page.$$eval('a', utils.getPos);
    await browser.close();

    const output = {
        device,
        dateStr,
        linkElements,
        queryCat,
        queryFile,
        deviceName: device.name,
        link: linkObj.link,
        platform: linkObj.platform,
        target: linkObj.target,
        dateAtSave: new Date().toString(),
    };

    const json = JSON.stringify(output);
    const jsonPath = `${curDir}/${niceDateStr}.json`;
    fs.writeFile(jsonPath, json, 'utf8', () => console.log(`Wrote to ${jsonPath}`));
}

console.log(devicesSelected);
const results = {};
(async () => {
    const date = new Date();
    const dateStr = date.toString();
    for await (const device of devicesSelected) {
        results[device.name] = {};
        for await (const link of links) {
            await scrape(link, device, dateStr, queryCat, queryFile);
            //results[device.name][link] = {};
            //results[ret.device.name][ret.link][ret.dateStr] = ret.links;
            const sleepSecs = utils.randomIntFromInterval(sleepRange[0], sleepRange[1]);
            console.log(`Sleeping for ${sleepSecs} seconds!`);
            await utils.sleep(sleepSecs * 1000);
        }
    }
    // if you want to do something with the results json, now you can. The data will have been written into different files in output/
})();