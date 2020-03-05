'use strict';

const puppeteer = require('puppeteer');
const fs = require('fs');
//const devices = require('puppeteer/DeviceDescriptors');

const getPos = (links) => {
    const ret = []
    links.forEach((link) => {
        const {top, left, bottom, right} = link.getBoundingClientRect();
        ret.push(
            {
                top, left, bottom, right,
                'href': link.href,
                'parentText': link.parentElement.textContent,
                'parentClasses': link.parentElement.className.split(' '),
                'classes': link.className.split(' '),
                'text': link.textContent,
            }
        );
    });
    return ret;
};

const sleep = (millis) => {
    return new Promise(resolve => setTimeout(resolve, millis));
}

(async() => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1040 });
  //await page.emulate(devices['iPhone 6']);
  await page.goto('https://www.nytimes.com/');
  await sleep(1000)
  const ret = await page.$$eval('a', getPos);
  const json = JSON.stringify(ret);
  fs.writeFile('links.json', json, 'utf8', () => console.log('printed'));

  await page.screenshot({path: 'full.png', fullPage: true});

  
  await browser.close();
})();


