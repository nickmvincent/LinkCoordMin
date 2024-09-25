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

async function get_category_trends(name, id){
    try {
	results = await googleTrends.dailyTrends({
            trendDate: today,
            geo: 'US',
	    category: id
	});
	console.log(name)
	const jsonPath = `search_queries/script_generated/${name}_raw_${niceDateStr}.json`;
	fs.writeFile(jsonPath, results, 'utf8', () => console.log(`Wrote to ${jsonPath}`));
	return({
            name: name,
            date: today,
            raw: jsonPath,
	    id: id
	});
    } catch (err) {
        console.log(err);
    };
};

queryCats = [];
(async () => {
    try{
	jsonData = await get_trends_schema();
	console.log(jsonData);
	
	queryCat = await get_category_trends(jsonData.name.replace(" & ", "_"),
					 jsonData.id);
	queryCats.push(queryCat);
	for (var idx in jsonData.children){
	    category = jsonData.children[idx];
	    queryCat = await get_category_trends(category.name.replace(" & ","_"),
						 category.id);
	    queryCats.push(queryCat);
	};

    } catch (error) {
	console.error(error);
    }
    const jsonPath = `search_queries/script_generated/${niceDateStr}_metadata.json`;
    fs.writeFile(jsonPath, JSON.stringify(queryCats), 'utf8', () => console.log(`Wrote to ${jsonPath}`));
})();
    
