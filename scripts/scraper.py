import requests
from bs4 import BeautifulSoup


class Scraper:
    def __init__(self, url, headers):
        self.url = url
        self.soup = None
        self.headers = headers

    def fetch(self):
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            self.soup = response.text
            # self.soup = BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {self.url}: {e}")

    # def extract_features(self):
    #     # Implement feature extraction logic here
    #     # For example, extracting titles, headings, paragraphs, etc.
    #     if self.soup:
    #         title = self.soup.title.text if self.soup.title else 'No title'
    #         headings = [h.text for h in self.soup.find_all(['h1', 'h2', 'h3'])]
    #         paragraphs = [p.text for p in self.soup.find_all('p') if p.text != 'Our editors will review what you’ve submitted and determine whether to revise the article.']
    #         return {
    #             'title': title,
    #             'headings': headings,
    #             'paragraphs': paragraphs
    #         }
    #     else:
    #         return "No content to extract features from"


if __name__ == "__main__":
    headers = {
        'User-Agent': 'Mozilla/5.0',
        # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        # 'Accept-Language': 'en-US,en;q=0.9',
        # 'Accept-Encoding': 'gzip, deflate, br',
        # 'DNT': '1',  # Do Not Track Request Header
        # 'Connection': 'keep-alive'
    }
    url = 'https://www.gov.il/he/departments/ministry_of_environmental_protection/govil-landing-page'
    scraper = Scraper(url, headers=headers)
    scraper.fetch()
    print(scraper.soup)
    # features = scraper.extract_features()
    # print(features)