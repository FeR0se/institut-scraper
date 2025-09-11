import urllib.parse as urlparse
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup, ResultSet

@dataclass(frozen=True)
class Institute:
    name: str
    email: frozenset
    phone: frozenset

@dataclass(frozen=True)
class Query:
    category: str
    category_name: str
    institutes: frozenset[Institute]

class Scraper:
    def load_search_results(self, base_url: str) -> ResultSet:
        u"""Load search results from URL."""
        # Copied this hack directly from the show all results button on the website 🙃
        url = f"{base_url}?{urlparse.urlencode({"rows": 1000})}"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        return soup.select(".search-result-list__item")

    def load_institute_page(self, institute_url: str) -> tuple[BeautifulSoup, str]:
        u"""Load institute page."""
        page = requests.get(institute_url)
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

    def scrape(self, super_category: str, category_id: str, category_name: str, query_url: str) -> Query:
        u"""Scrape contact information for a given search query."""
        results = self.load_search_results(base_url)
        for result in results:
            result_url = result.div.get("data-result-url")
            institute_page = self.load_institute_page(base_url + result_url)
            contact_info = self.extract_contact_info(institute_page)


if __name__ == "__main__":
    scraper = Scraper()
    base_url = "https://miz.org/de/musikleben/institutionen/orchester/oeffentlich-finanzierte-sinfonieorchester"
    results = scraper.load_search_results(base_url)
    result_url = results[0].div.get("data-result-url")
    institute_page, institute_name = scraper.load_institute_page(base_url + result_url)
    infoboxes = institute_page.select("page-layout--24c")