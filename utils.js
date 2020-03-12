// see https://developer.mozilla.org/en-US/docs/Web/API/Element/getBoundingClientRect for 
// more on getBoundingClientRect
const getPos = (links) => {
    const ret = []
    links.forEach((link) => {
        const {
            top,
            left,
            bottom,
            right
        } = link.getBoundingClientRect();
        ret.push({
            top,
            left,
            bottom,
            right,
            'href': link.href,
            'parentText': link.parentElement.textContent,
            'parentClasses': link.parentElement.className.split(' '),
            'classes': link.className.split(' '),
            'text': link.textContent,
        });
    });
    return ret;
};

// modified from here: https://stackoverflow.com/a/53590610
const sleep = (millis) => {
    return new Promise(resolve => setTimeout(resolve, millis));
}

// from here: https://stackoverflow.com/a/53527984
const scrollDown = async (page) => {
    await page.evaluate(async () => {
        await new Promise((resolve, reject) => {
            var totalHeight = 0;
            var distance = 100;
            var timer = setInterval(() => {
                var scrollHeight = document.body.scrollHeight;
                window.scrollBy(0, distance);
                totalHeight += distance;

                if (totalHeight >= scrollHeight) {
                    clearInterval(timer);
                    resolve();
                }
            }, 100);
        });
    });
}

https://stackoverflow.com/a/7228322
function randomIntFromInterval(min, max) { // min and max included 
    return Math.floor(Math.random() * (max - min + 1) + min);
}

module.exports = {
    getPos,
    sleep,
    scrollDown,
    randomIntFromInterval
};