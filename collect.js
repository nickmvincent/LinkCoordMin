'use strict';
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth')
puppeteer.use(StealthPlugin())

const fs = require('fs');
const mkdirp = require('mkdirp');
// utilities: get <a> positions, sleep, scrollDown, random interval
const utils = require('./utils');
// default mobile devices and custom "desktop devices"
const emulatedDevices = require('./emulatedDevices');


const outDir = 'output';
const sleepRange = [30, 60];
let curDir = '';


const myArgs = process.argv.slice(2);
let devicesSelected = [];
if (myArgs[0] == 'allDevices') {
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
const targets = text.split("\n").filter(Boolean); // removes empty strings

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
    } [platform]
}
const links = [];
for (const target of targets) {
    links.push({
        platform,
        target,
        link: `${startStr}${target}`,
    });
}

const coords = {
    hancock: {
        lat: 41.8988,
        long: -87.6229,
    },
    sf: {
        lat: 37.7749,
        long: -122.4194
    },
    uw: {
        lat: 47.655548,
        long: -122.303200
    }
}

const scrape = async (linkObj, device, dateStr, queryCat, queryFile) => {
    const niceLink = linkObj.link.replace(/\//g, "-").replace(/:/g, '-'); // (nice for Windows filesystem)
    const niceDateStr = dateStr.replace(/:/g, '-'); // (nice for Windows filesystem)

    curDir = `${outDir}/${device.name}/${niceLink}`;
    mkdirp(curDir);

    const browser = await puppeteer.launch({
        args: ['--no-sandbox'],
        headless: false
    });
    const context = browser.defaultBrowserContext();
    context.clearPermissionOverrides();
    await context.overridePermissions(linkObj.link, ['geolocation']);
    const page = await context.newPage();
    await page.emulate(device);
    await page.setGeolocation({
        latitude: coords['uw']['lat'],
        longitude: coords['uw']['long'],
        //accuracy: 100,
    });

    page.on('dialog', async dialog => {
        console.log(dialog.message());
        await dialog.accept();
    });
    page.on('console', consoleObj => console.log(consoleObj.text()));

    console.log('Browser launched and page loaded');
    // https://stackoverflow.com/a/51250754nom

    await page.goto(linkObj.link, {
        waitUntil: 'networkidle2'
    });
    await context.overridePermissions(page.url(), ['geolocation']);
    await utils.sleep(2000);

    let linkHandlers;
    if (linkObj.link.includes('google.com')) {
        linkHandlers = await page.$x('//a[contains(text(), "Use precise location")]');
    } else if (linkObj.link.includes('duckduckgo.com')) {
        linkHandlers = await page.$x('//a[contains(text(), "Enable Location")]');
    } else if (linkObj.link.includes('bing.com')) {
        linkHandlers = await page.$x('//a[contains(text(), "Change")]');
    }
    if (linkHandlers.length > 0) {
        await linkHandlers[0].click();
        utils.sleep(1000);
        if (linkObj.link.includes('google.com')) {
            await page.reload({
                waitUntil: ["networkidle0", "domcontentloaded"]
            });
        } else if (linkObj.link.includes('bing.com')) {
            const inputHandlers = await page.$x('//input[contains(text(), "Accept")]');
            if (inputHandlers.length > 0) {
                intputHandlers[0].click();
                console.log('clicked accept input');
            }
        }
    } else {
        console.log('no location link found');
    }

    console.log('sleeping...');
    await utils.sleep(2000);
    await utils.scrollDown(page);

    console.log('Loaded page, slept 1 sec, and scrolled down.');

    const pngPath = `${curDir}/${niceDateStr}.png`
    console.log(pngPath);
    await page.screenshot({
        path: pngPath,
        fullPage: true
    });

    let linkElements;
    try {
        linkElements = await page.$$eval('a', utils.getPos);
    } catch (e) {
        console.log(e);
    }

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

    const mhtmlPath = `${curDir}/${niceDateStr}.mhtml`;
    const cdp = await page.target().createCDPSession();
    const {
        data
    } = await cdp.send('Page.captureSnapshot', {
        format: 'mhtml'
    });
    fs.writeFileSync(mhtmlPath, data);

    // === all done! == //
    await browser.close();
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
    // if you want to do something with the results json, can add code here. The data will have been written into different files in output/
})();