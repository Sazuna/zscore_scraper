# zscore_scraper
Scrap a web page's main content based on the z-score (abnormally big paragraphs compared to menus etc will be caught by this method)

## Usage
```python zscore_scraper [url] [z-score|clustering]```
- Use z-score for an optimized result.
- Clustering attempts to cluster paths into relevant path or irrelevant paths based on their mean lenghts. This method is not as effective as z-score.
- Do not use the main method twice if you attend to call it from another python program (I will fix that I promise)

## Returns
- title (if any is found by beautifulsoup)
- publication datetime (if any is found by beautifulsoup)
- page's content.

Feel free to reuse this code in your projects :)

### Time optimization :
Use curl instead of selenium, as selenium is time-consuming. We use selenium to 'accept cookies' and scrap page content even if the content is dynamically loaded by JavaScript or other dynamic languages. We set a timer of total of 0.4s, which can be increased by the time of page loading.
