import requests

# NOTE: This script is not used in our pipeline. 
# We do not fetch wiki articles automatically.

def fetch_wikipedia_article(title):
    """
    Extracts the text of a Wikipedia article and saves it to a text file.
    """
    URL = "https://en.wikipedia.org/w/api.php"
    PARAMS = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "extracts",
        "explaintext": True,
    }

    response = requests.get(URL, params=PARAMS)
    data = response.json()
    page = next(iter(data['query']['pages'].values()))
    return page['extract']

def save_text_to_file(text, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(text)
