import urllib.parse as urlparse
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup, ResultSet
from tqdm.contrib.concurrent import thread_map

from utils import get_url

@dataclass(frozen=True)
class Institute:
    name: str
    email: frozenset
    phone: frozenset

@dataclass(frozen=True)
class Query:
    super_category: str
    category_id: str
    category_name: str
    institutes: frozenset[Institute]

class Scraper:
    def load_search_results(self, base_url: str) -> ResultSet | None:
        u"""Load search results from URL."""
        if len(base_url) == 0:
            return None

        # Copied this hack directly from the show all results button on the website 🙃
        url = f"{base_url}?{urlparse.urlencode({"rows": 1000})}"
        try:
            parsed_url = urlparse.urlparse(url)
            all([parsed_url.scheme in ("http", "https"), parsed_url.netloc])
        except:
            print(f"Failed to parse {url}")
            raise Exception("Bad URL")
        page = get_url(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        results = soup.select(".search-result-list__item")

        # Handle more than 1000 results
        num_results = soup.select_one(".search-info__num-hits").text.split()[0]
        num_results = int(num_results) if num_results.isnumeric() else 0
        if num_results > 1000:
            session = requests.Session()
            results = []
            while True:
                response = session.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')

                # Collect current batch of results
                batch = soup.select(".search-result-list__item")
                results.extend(batch)

                # Load next batch
                loading_button = soup.select_one(".search-result-list__infinite-pagination-button--next")
                if not loading_button:
                    break # End loading of more results when all are loaded
                button_url = loading_button["href"]
                url = f"https://miz.org{button_url}"

        return results

    def load_institute_page(self, institute_url: str) -> tuple[BeautifulSoup, str]:
        u"""Load institute page."""
        page = get_url(institute_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        institute_name = soup.select_one(".page-header__title").text.strip("\n")
        return soup, institute_name

    def extract_contact_info(self, soup: BeautifulSoup) -> tuple[frozenset, frozenset]:
        u"""Extract the contact information from an HTML page."""
        contact_fields = soup.select(".page-layout--24c")
        mail_addresses = set()
        phone_numbers = set()
        for f in contact_fields:
            # handle email addresses
            for mailto_links in f.select('a[href^="mailto:"]'):
                mail_addresses.add(mailto_links.text)
            # handle phone numbers as fallback
            for phone_links in f.select('a[href^="tel:"]'):
                phone_numbers.add(phone_links['href'].lstrip('tel:'))


        return frozenset(mail_addresses), frozenset(phone_numbers)

    def scrape_institute(self, result: BeautifulSoup) -> Institute:
        u"""Scrape information for an institute."""
        result_url = result.div.get("data-result-url")
        institute_page, institute_name = self.load_institute_page("https://miz.org" + result_url)
        emails, phone_numbers = self.extract_contact_info(institute_page)

        return Institute(name=institute_name, email=emails, phone=phone_numbers)

    def scrape(self, super_category: str, category_id: str, category_name: str, url: str) -> Query:
        u"""Scrape contact information for a given search query."""
        # Load all search results and extract direct links
        results = self.load_search_results(url)
        if results is None:
            print(f"Found 0 institutes for category \"{category_name}\"")
            dummy_institute = Institute(name="keine", email=frozenset(["keine"]), phone=frozenset(["keine"]))
            return Query(super_category=super_category, category_id=category_id, category_name=category_name, institutes=frozenset([dummy_institute]))
        print(f"Found {len(results)} institutes for category \"{category_name}\"")

        # Extract information from all institute pages
        institutes = thread_map(self.scrape_institute, results)
        institutes = set(institutes)

        print(f"Collected data for {len(institutes)} institutes for {category_name}")
        query = Query(super_category=super_category, category_id=category_id, category_name=category_name, institutes=frozenset(institutes))
        return query


def scrape_query(query_params) -> Query:
    scraper = Scraper()
    return scraper.scrape(**query_params)


if __name__ == "__main__":
    scraper = Scraper()
    base_url = "https://miz.org/de/musikleben/institutionen/orchester/oeffentlich-finanzierte-sinfonieorchester"
    query = scraper.scrape("Klangkörper", "KK1", "Öffentlich finanzierte Sinfonieorchester", base_url)