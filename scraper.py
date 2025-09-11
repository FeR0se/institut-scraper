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
        # Load all search results and extract direct links
        results = self.load_search_results(query_url)
        print(f"Found {len(results)} institutes for category \"{category_name}\"")

        # Extract information from all institute pages
        institutes = set()
        for result in results:
            result_url = result.div.get("data-result-url")
            institute_page, institute_name = self.load_institute_page("https://miz.org" + result_url)
            emails, phone_numbers = self.extract_contact_info(institute_page)

            # Aggregate extracted data
            institutes.add(Institute(name=institute_name, email=emails, phone=phone_numbers))

        print(f"Collected data for {len(institutes)} institutes for {category_name}")
        query = Query(category=super_category, category_name=category_name, institutes=frozenset(institutes))
        return query


if __name__ == "__main__":
    scraper = Scraper()
    base_url = "https://miz.org/de/musikleben/institutionen/orchester/oeffentlich-finanzierte-sinfonieorchester"
    query = scraper.scrape("Klangkörper", "KK1", "Öffentlich finanzierte Sinfonieorchester", base_url)