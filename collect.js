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
console.log('args', argv);


const fs = require('fs');
const mkdirp = require('mkdirp');
// utilities: get <a> positions, sleep, scrollDown, random interval
const utils = require('./utils');
// default mobile devices and custom "desktop devices"
const emulatedDevices = require('./emulatedDevices');

const sleepRange = [15, 30];
const headless = argv.headless;
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

// TODO: do we want to add more coords to spoof?
const coords = {
    hancock: {
        lat: 41.8988,
        long: -87.6229,
        zip: '60611',
    },
    uw: {
        lat: 47.655548,
        long: -122.303200,
        zip: '98195',
    }
}

const scrape = async (linkObj, device, platform, queryCat, dateStr, queryFile) => {
    let niceLink = linkObj.link.replace(/\//g, "-").replace(/:/g, '-'); // (nice for Windows filesystem)
    if (niceLink.length > 100) {
        niceLink = niceLink.substring(0, 100);
    }
    const niceDateStr = dateStr.replace(/:/g, '-'); // (nice for Windows filesystem)

    curDir = `${outDir}/${device.name}/${niceLink}`;
    mkdirp(curDir);



    const browser = await puppeteer.launch({
        args: [
            '--no-sandbox',
            `--proxy-server=your_proxy_ip:port`, // TODO: Add the proxy server address here
            ],
        headless: headless
    });
    const context = browser.defaultBrowserContext();
    //await context.clearPermissionOverrides();
    await context.overridePermissions(linkObj.link, ['geolocation']);
    //await context.overridePermissions(linkObj.link + '#', ['geolocation']);
    const page = await context.newPage();
    await page.setCacheEnabled(false);

    // Clearing cookies to try to improve our geolocation spoofing.
    await page.deleteCookie(...await page.cookies()); 

    // Add the navigator.permissions.query override here, also to try to improve geolocation spoofing...
    // Technically we already override the geolocation premission in line 111 at the browswer level, I think this does it on the site level.
    await page.evaluateOnNewDocument(() => {
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'geolocation' ?
            Promise.resolve({ state: 'granted' }) :
            originalQuery(parameters)
        );
    });

    const cdp = await page.target().createCDPSession();

    await page.emulate(device);
    
    if (geoName !== 'None') {
        await page.setGeolocation({
            latitude: coords[geoName]['lat'],
            longitude: coords[geoName]['long'],
        });
    }

    // Bing will open a dialog box for changing location. Below code will accept it.
    page.on('dialog', async dialog => {
        console.log(dialog.message());
        await dialog.accept();
    });

    // Launch and load the page.
    console.log('Browser launched and page loaded');
    try {
        await page.goto(linkObj.link, {
            waitUntil: 'networkidle2'
        });
    } catch (e) {
        console.log('err with page.goto!');
        const errPath = `${curDir}/ERR_${niceDateStr}.txt`;
        const err = {gotoErr: e}
        fs.writeFile(errPath, JSON.stringify(err), 'utf8', () => console.log(`Wrote err to ${errPath}`));
    }

    

    // Check geolocation permissions
    const granted = await page.evaluate(async () => {
        return (await navigator.permissions.query({name: 'geolocation'})).state;
    });
    console.log('Granted:', granted);
    console.log('device:', device)
    console.log('platform', platform, 'ismobile', device.viewport.isMobile);

    
    // To print cookies
    // var cookies = await page.cookies();
    // console.log('cookies');
    // console.log(cookies);
    //
    await utils.sleep(1000);


    if (geoName !== 'None') {
        let linkHandlers;
        let button;
        if (platform === 'google') {
            // FLAG: This will break if the "Use precise location" text changes.
            button = '//a[contains(text(), "Use precise location")]';
        } else if (platform === 'duckduckgo') {
            button = '//a[contains(text(), "Enable Location")]';
        } else if (platform === 'bing' && !device.viewport.isMobile) {
            button = '//a[contains(text(), "Change")]';
        }
        linkHandlers = await page.$x(button);
        if (linkHandlers.length > 0) {
            // click the link then wait 1 second
            console.log('clicking link')
            await page.setGeolocation({
                latitude: coords[geoName]['lat'],
                longitude: coords[geoName]['long'],
            });
            
            await linkHandlers[0].click(),
            await page.waitFor(3000);
            
            
            if (platform === 'google') {
                await page.reload({
                    waitUntil: ["networkidle0", "domcontentloaded"]
                });

            } else if (platform === 'bing' && !device.viewport.isMobile) {
                await page.waitForSelector('input[name=geoname]');
                await page.type('input[name=geoname]', coords[geoName]['zip'], {delay: 50});
                await page.waitFor(1000);

                const sel = 'input[id=chlocman_sbChangeLocationLink]'
                await page.click(sel);
            }
        } else {
            console.log('no location link found');
        }

        console.log('sleeping 3 seconds...');
        await utils.sleep(3000);
    }

    if (platform != 'reddit') {
        
        await utils.scrollDown(page);
        // if (platform === 'bing') {
        //     await page.waitForSelector('.b_mpref');
        // }

    }

    const pngPath = `${curDir}/${niceDateStr}.png`
    console.log(pngPath);
    await page.screenshot({
        path: pngPath,
        fullPage: true
    });

    let linkElements;
    let err = false;
    let errMsg = "";
    try {
        linkElements = await page.$$eval('a', utils.getPos);
    } catch (e) {
        console.log(e);
        err = true;
        errMsg = e;
    }

    const output = {
        device,
        dateStr,
        linkElements,
        queryCat,
        queryFile,
        errMsg,
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
    
    // TODO: error handling here.
    try {
        const {
            data
        } = await cdp.send('Page.captureSnapshot', {
            format: 'mhtml'
        });
        fs.writeFileSync(mhtmlPath, data);
    } catch (e) {
        console.log('err with mhtml');
        const errPath = `${curDir}/ERR_MHTML_${niceDateStr}.txt`;
        const err = {gotoErr: e}
        fs.writeFile(errPath, JSON.stringify(err), 'utf8', () => console.log(`Wrote err to ${errPath}`));
    }
    // === all done! == //
    await browser.close();
}

console.log('devices selected', devicesSelected);
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