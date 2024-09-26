const googleTrends = require('google-trends-api');
const fs = require('fs');

const today = new Date();
const niceDateStr = today.toString().replace(/:/g, '-'); // (nice for Windows filesystem)

async function get_trends_schema() {
    const trends_typology_url="https://trends.google.com/trends/api/explore/pickers/category?hl=en-US&tz=240"
    try{
	const response = await fetch(trends_typology_url);
	if (!response.ok) {
	    throw new Error(`HTTP error! Status: ${response.status}`);
	}
	const data = await response.text(); // Parse the response as JSON
	// Split the text into lines and skip the first line
	const lines = data.split('\n').slice(1).join('\n');
	const jsonData = JSON.parse(lines);
	return jsonData;
    
    } catch(error) {
	console.error('There was a problem with the fetch operation:', error);
    };
};

function replaceNameValue(obj) {
    const prop_names = Object.getOwnPropertyNames(obj)
    for (let idx in prop_names) {
	name = prop_names[idx]
	if (name == 'query') {
	    obj.query = obj.query + " Reddit";
	}
	// If the value is an object or array, recurse into it
	if (typeof obj[name] === "object" && obj[name] !== null) {
            replaceNameValue(obj[name]);
	}
    }
}

async function get_category_trends(name, id){
    try {
	results = await googleTrends.dailyTrends({
            trendDate: today,
            geo: 'US',
	    category: id
	});

	const jsonPath = `search_queries/script_generated/${name}_raw_${niceDateStr}.json`;
	const redditJsonPath = `search_queries/script_generated/${name}_reddit_raw_${niceDateStr}.json`;
	fs.writeFile(jsonPath, results, 'utf8', () => console.log(`Wrote to ${jsonPath}`));
	reddit_results = JSON.parse(results);
	replaceNameValue(reddit_results);
	fs.writeFile(redditJsonPath, JSON.stringify(reddit_results), 'utf8', () => console.log(`Wrote to ${redditJsonPath}`));
	console.log(reddit_results);

	return([
	    {
		name: name,
		date: today,
		raw: jsonPath,
		id: id
	    },
	    {
		name: name + " reddit",
		date: today,
		raw: redditJsonPath,
		id: id
	    }]);
    } catch (err) {
        console.log(err);
    };
};

queryCats = [];
(async () => {
    try{
	jsonData = await get_trends_schema();
	queryCatrg = await get_category_trends(jsonData.name.replace(" & ", "_"),
					 jsonData.id);
	queryCats.push(queryCatrg[0]);
	queryCats.push(queryCatrg[1]);
	for (var idx in jsonData.children){
	    category = jsonData.children[idx];
	    queryCatrg = await get_category_trends(category.name.replace(" & ","_"),
						 category.id);
	    queryCats.push(queryCatrg[0]);
	    queryCats.push(queryCatrg[1]);
	};

    } catch (error) {
	console.error(error);
    }
    const jsonPath = `search_queries/script_generated/${niceDateStr}_metadata.json`;
    fs.writeFile(jsonPath, JSON.stringify(queryCats), 'utf8', () => console.log(`Wrote to ${jsonPath}`));
})();
    
