const googleTrends = require('google-trends-api');
const fs = require('fs');

const today = new Date();
const niceDateStr = today.toString().replace(/:/g, '-'); // (nice for Windows filesystem)

const queryCats = [];

(async () => {

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
    const jsonPath = `search_queries/script_generated/${niceDateStr}_metadata.json`
    fs.writeFile(jsonPath, JSON.stringify(queryCats), 'utf8', () => console.log(`Wrote to ${jsonPath}`));
})();
