# Known issues with location spoofing
## Google
### Desktop
* Occasionally, it uses IP address instead of javascript geolocation.
* see output/Chrome on Windows/https---www.google.com-search?q=coronavirus local news/Sat Mar 14 2020 16-21-36 GMT-0500 (Central Daylight Time).png
* Happened on desktop only
### Mobile
* mobile seems to work great

## Bing
### Desktop
* To get location to work on desktop, you need to run a script emulating mobile first, then Bing seems to use the cookies from that script for desktop queries after. This is very weird and feels magical - not great!
* Desktop location spoofing is very inconsistent! Sometimes works when running repeat sessions (headless or non headless) but not in a replicable manner.
* I can't even get location to work for desktop SERPs using the console. The "Accept" button throws an error!
* Note: one thing that works using dev console is to (1) make a query that triggers maps, (2) change location by entering a place name, then (3) make a new query.
* this works programmatically as well!
### Mobile
* Mobile results seem to work, but when emulating location (through clicking the "Change" button), the full page of results don't load!
* ^ fixed by
* If the SERP doesn't have a "Change" button (because Bing thinks it isn't a "local" query?), this doesn't work at all.


## Duckduckgo
### Desktop
* Screenshots are messed up? So is mhtml files.
* Results with maps seems to work. For results without maps, its unclear that the location was used!
### Mobile
* Locations w/ maps look good... but screenshots are messed up here as well!