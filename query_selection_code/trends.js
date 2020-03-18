const googleTrends = require('google-trends-api');
const fs = require('fs');



const today = new Date();
const niceDateStr = today.toString().replace(/:/g, '-'); // (nice for Windows filesystem)

const queryCats = [];

(async () => {

    await googleTrends.dailyTrends({
            trendDate: today,
            geo: 'US',
        })
        .then((results) => {
            const jsonPath = `search_queries/script_generated/dailyTrends_raw_${niceDateStr}.json`;
            fs.writeFile(jsonPath, results, 'utf8', () => console.log(`Wrote to ${jsonPath}`));

            queryCats.push({
                name: 'dailyTrends',
                date: today,
                raw: jsonPath
            });

        })
        .catch((err) => {
            console.log(err);
        });

    await googleTrends.relatedQueries({
            keyword: 'coronavirus'
        })
        .then((results) => {
            const jsonPath = `search_queries/script_generated/relatedQueries_raw_coronavirus_${niceDateStr}.json`;
            fs.writeFile(jsonPath, results, 'utf8', () => console.log(`Wrote to ${jsonPath}`));
            queryCats.push({
                name: 'relatedQueries_coronavirus',
                date: today,
                raw: jsonPath
            });
        })
        .catch((err) => {
            console.log(err);
        });


    await googleTrends.relatedQueries({
            keyword: 'COVID-19'
        })
        .then((results) => {
            const jsonPath = `search_queries/script_generated/relatedQueries_raw_COVID-19_${niceDateStr}.json`;
            fs.writeFile(jsonPath, results, 'utf8', () => console.log(`Wrote to ${jsonPath}`));
            queryCats.push({
                name: 'relatedQueries_COVID-19',
                date: today,
                raw: jsonPath
            });
        })
        .catch((err) => {
            console.log(err);
        })

    const jsonPath = `metadata/query_cats/${niceDateStr}.json`
    fs.writeFile(jsonPath, JSON.stringify(queryCats), 'utf8', () => console.log(`Wrote to ${jsonPath}`));
})();