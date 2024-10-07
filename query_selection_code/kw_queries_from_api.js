const googleTrends = require('google-trends-api');
const fs = require('fs');

const today = new Date();
const niceDateStr = today.toString().replace(/:/g, '-'); // (nice for Windows filesystem)

// Function to get related queries for a keyword
function getRelatedQueries(keyword) {
    return googleTrends.relatedQueries({keyword: keyword, geo: 'US'}) //startTime is an optional parameter that lets us choose timerange
        .then((results) => {
            const data = JSON.parse(results);
            // Check if 'rankedList' exists and has data
            if (data.default && data.default.rankedList.length > 0) {
                const relatedQueries = data.default.rankedList[0].rankedKeyword.map(query => query.query);
                return { keyword, relatedQueries };
            } else {
                console.warn(`No related queries found for "${keyword}".`);
                return { keyword, relatedQueries: [] }; // Return empty array if no queries found
            }
        })
        .catch((err) => {
            console.error(`Error fetching related queries for "${keyword}":`, err);
            return { keyword, relatedQueries: [] }; // Return empty array on error
        });
}

(async function() {
    const filePath = process.argv[2]; // First argument: path to the input .txt file
    const outputFilePath = process.argv[3]; // Second argument: output file name

    if (!filePath || !outputFilePath) {
        console.error('Please provide both the input .txt file and the output file name as arguments.');
        process.exit(1);
    }

    try {
        const fileContent = fs.readFileSync(filePath, 'utf-8');
        const keywords = fileContent.split('\n').filter(Boolean); // Split into lines and remove empty lines

        const relatedQueriesList = [];

        for (let keyword of keywords) {
            const result = await getRelatedQueries(keyword.trim());
            relatedQueriesList.push(result);

            // Delay between requests to avoid hitting the API too fast
            //await new Promise(resolve => setTimeout(resolve, 2000)); // 2 seconds delay
        }

        // Write the result to the specified JSON file
        fs.writeFileSync(outputFilePath, JSON.stringify(relatedQueriesList, null, 2)); // Pretty-print with 2-space indentation
        console.log(`Related queries saved to ${outputFilePath}`);

    } catch (err) {
        console.error('Error reading the file or processing keywords:', err);
    }
})();