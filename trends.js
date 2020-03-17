const googleTrends = require('google-trends-api');
const fs = require('fs');



const today = new Date();
const niceDateStr = today.toString().replace(/:/g, '-'); // (nice for Windows filesystem)

googleTrends.dailyTrends({
    trendDate: today,
    geo: 'US',
}, function (err, results) {
    if (err) {
        console.log(err);
    } else {
        const jsonPath = `search_queries/script_generated/dailyTrends_raw_${niceDateStr}.json`;
        fs.writeFile(jsonPath, results, 'utf8', () => console.log(`Wrote to ${jsonPath}`));
    }
});

googleTrends.relatedQueries({
    keyword: 'coronavirus'
})
.then((results) => {
    const jsonPath = `search_queries/script_generated/relatedQueries_raw_coronavirus_${niceDateStr}.json`;
    fs.writeFile(jsonPath, results, 'utf8', () => console.log(`Wrote to ${jsonPath}`));
})
.catch((err) => {
    console.log(err);
})


googleTrends.relatedQueries({
    keyword: 'COVID-19'
})
.then((results) => {
    const jsonPath = `search_queries/script_generated/relatedQueries_raw_COVID-19_${niceDateStr}.json`;
    fs.writeFile(jsonPath, results, 'utf8', () => console.log(`Wrote to ${jsonPath}`));
})
.catch((err) => {
    console.log(err);
})

