const googleTrends = require('google-trends-api');
const fs = require('fs');






const today = new Date();
const niceDateStr = today.toString().replace(/:/g, '-'); // (nice for Windows filesystem)

const queryCats = [];

(async () => {

    const stem_file = `search_queries/prepped/covid_stems/0.txt`;
    const text = fs.readFileSync(stem_file, "utf-8");
    const targets = text.split("\n").filter(Boolean); // removes empty strings

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
    for await (const stem of targets) {
        await googleTrends.relatedQueries({
            keyword: stem
        })
        .then((results) => {
            const jsonPath = `search_queries/script_generated/relatedQueries_raw_${stem}_${niceDateStr}.json`;
            fs.writeFile(jsonPath, results, 'utf8', () => console.log(`Wrote to ${jsonPath}`));
            queryCats.push({
                name: `relatedQueries_${stem}`,
                date: today,
                raw: jsonPath
            });
        })
        .catch((err) => {
            console.log(err);
        });
    }

    const jsonPath = `search_queries/script_generated/${niceDateStr}_metadata.json`
    fs.writeFile(jsonPath, JSON.stringify(queryCats), 'utf8', () => console.log(`Wrote to ${jsonPath}`));
})();