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

const sleep = (millis) => {
    return new Promise(resolve => setTimeout(resolve, millis));
}

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

module.exports = {
    getPos,
    sleep,
    scrollDown,
};