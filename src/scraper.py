from bs4 import BeautifulSoup
import requests

def scrape_webpage(url, data_char_limit = 5000):
    '''
    This method is used for scraping the webpage represented by url.
    data_char_limit: maximum number of characters to be returned

    Returns: title and body of the webpage. If the connection times out, returns None for title and body.
    '''
    try:
        doc = requests.get(url, timeout = 5)
        soup = BeautifulSoup(doc.content, "html.parser")
        title = soup.title.text
        body = soup.body

        data = ''
        for string in body.strings:
            if(len(string) > 0):
                data += string.strip().strip('\t')
        
        return title, data[:data_char_limit]
    except:
        return None, None
