'use strict';
// puppeteer + stealth
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth')
puppeteer.use(StealthPlugin())

// arg parsing
const argv = require('yargs')
    .default('headless', true)
    .describe('f', 'Use headless browsing')
    .default('sleepMin', 15)
    .default('sleepMax', 30)
    .default('geoName', 'None')
    .default('outDir', 'outdir')
    .default('queryDir', 'search_queries/prepped')
    .help('h')
    .alias('h', 'help')
    //.default('devicesSelected', 'chromewindows')
    .argv;
console.log(argv);


const fs = require('fs');
const mkdirp = require('mkdirp');
// utilities: get <a> positions, sleep, scrollDown, random interval
const utils = require('./utils');
// default mobile devices and custom "desktop devices"
const emulatedDevices = require('./emulatedDevices');

const sleepRange = [15, 30];
const headless = true;
let curDir = '';

//const myArgs = process.argv.slice(2);
const deviceArg = argv.device;
let devicesSelected = [];
if (deviceArg == 'allDevices') {
    console.log('Using all devices specifide in emulatedDevices.js');
    for (const key of Object.keys(emulatedDevices)) {
        devicesSelected.push(emulatedDevices[key]);
        console.log(emulatedDevices[key]);
    }
} else {
    devicesSelected.push(emulatedDevices[deviceArg])
}
const platform = argv.platform;
const queryCat = argv.queryCat;
const queryFile = argv.queryFile;
const geoName = argv.geoName;
const outDir = argv.outDir;
const queryDir = argv.queryDir;

const target_file = `${queryDir}/${queryCat}/${queryFile}.txt`;
const text = fs.readFileSync(target_file, "utf-8");
const targets = text.split("\n").filter(Boolean); // removes empty strings

/*=====
If we are scraping search engines, we need to make our keywords into URLs
If we are scraping other sites, the "keywords" should already be full urls
=====*/
let startStr = '';
if (['google', 'bing', 'duckduckgo', 'yahoo'].includes(platform)) {
    startStr = {
        google: 'https://www.google.com/search?q=',
        bing: 'https://www.bing.com/search?q=',
        duckduckgo: 'https://www.duckduckgo.com/?q=',
        yahoo: 'https://search.yahoo.com/search?p='
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
        zip: 60611,
    },
    uw: {
        lat: 47.655548,
        long: -122.303200,
        zip: '98195',
    }
}
const scrape = async (linkObj, device, platform, queryCat, dateStr, queryFile) => {
    const niceLink = linkObj.link.replace(/\//g, "-").replace(/:/g, '-'); // (nice for Windows filesystem)
    const niceDateStr = dateStr.replace(/:/g, '-'); // (nice for Windows filesystem)

    curDir = `${outDir}/${device.name}/${niceLink}`;
    mkdirp(curDir);

    const browser = await puppeteer.launch({
        args: ['--no-sandbox', ],
        headless: headless
    });
    const context = browser.defaultBrowserContext();
    context.clearPermissionOverrides();
    await context.overridePermissions(linkObj.link, ['geolocation']);
    const page = await context.newPage();
    await page.setCacheEnabled(false);

    const cdp = await page.target().createCDPSession();

    await page.emulate(device);
    if (geoName !== 'None') {
        await page.setGeolocation({
            latitude: coords[geoName]['lat'],
            longitude: coords[geoName]['long'],
            //accuracy: 100,
        });
    } 
    

    page.on('dialog', async dialog => {
        console.log(dialog.message());
        await dialog.accept();
    });

    console.log('Browser launched and page loaded');
    await page.goto(linkObj.link, {
        waitUntil: 'networkidle2'
    });
    // var cookies = await page.cookies();
    // console.log(cookies);
    await context.overridePermissions(page.url(), ['geolocation']);
    await utils.sleep(2000);

    if (geoName !== 'None') {
        let linkHandlers;
        if (platform === 'google') {
            linkHandlers = await page.$x('//a[contains(text(), "Use precise location")]');
        } else if (platform === 'duckduckgo') {
            linkHandlers = await page.$x('//a[contains(text(), "Enable Location")]');
        } else if (platform === 'bing' && !device.isMobile) {
            linkHandlers = await page.$x('//a[contains(text(), "Change")]');
        }
        if (linkHandlers.length > 0) {
            await linkHandlers[0].click();
            await page.waitFor(1000);
            if (platform === 'google') {
                await page.reload({
                    waitUntil: ["networkidle0", "domcontentloaded"]
                });
            } else if (platform === 'bing' && !device.isMobile) {
                await page.waitForSelector('input[name=geoname]');
                await page.type('input[name=geoname]', coords[geoName]['zip'], {delay: 50});
                await page.waitFor(1000);

                const sel = 'input[id=chlocman_sbChangeLocationLink]'
                await page.click(sel);
            }
        } else {
            console.log('no location link found');
        }

        console.log('sleeping...');
        await utils.sleep(3000);
    }

    if (platform != 'reddit') {
        await utils.scrollDown(page);
        
    }

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
            await scrape(link, device, platform, queryCat, dateStr, queryFile);
            //results[device.name][link] = {};
            //results[ret.device.name][ret.link][ret.dateStr] = ret.links;
            const sleepSecs = utils.randomIntFromInterval(sleepRange[0], sleepRange[1]);
            console.log(`Sleeping for ${sleepSecs} seconds!`);
            await utils.sleep(sleepSecs * 1000);
        }
    }
    // if you want to do something with the results json, can add code here. The data will have been written into different files in output/
})();