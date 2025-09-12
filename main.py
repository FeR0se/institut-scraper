import csv
import argparse
import datetime
from os import PathLike
from pathlib import Path
from collections import defaultdict

from tqdm.contrib.concurrent import process_map

from scraper import Query, Institute, Scraper


def load_links(filepath: str | PathLike):
    filepath = Path(filepath)
    with filepath.open("r", encoding="utf-8-sig") as fp:
        file = fp.read().splitlines()

    reader = csv.DictReader(file, delimiter=";")
    return [row for row in reader]


def export_to_csv(data: list[Query], export_path: str | PathLike):
    u"""Export data to CSV file"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    export_path = Path(export_path)
    export_path.mkdir(parents=True, exist_ok=True)
    export_path = export_path.joinpath(f"contact_export{timestamp}.csv")

    with export_path.open("w", encoding="utf-8") as fp:
        columns = ("super_category", "category_id", "category_name", "institute_name", "emails", "phone_numbers")
        writer = csv.DictWriter(fp, fieldnames=columns)
        writer.writeheader()
        for q in data:
            institutes = q.institutes
            for institute in institutes:
                name = institute.name
                # transform all scraped emails and phone numbers to single string
                emails, phone_numbers = "", ""
                for mail in institute.email:
                    emails += mail + "; "
                for phone in institute.phone:
                    phone_numbers += phone + "; "

                row = {
                    "super_category": q.super_category,
                    "category_id": q.category_id,
                    "category_name": q.category_name,
                    "institute_name": name,
                    "emails": emails,
                    "phone_numbers": phone_numbers
                }
                writer.writerow(row)



if __name__ == "__main__":
    """parser = argparse.ArgumentParser(description="Scrape contact information from miz.org")
    parser.add_argument("links", nargs=1, help="CSV containing the links to scrape")
    parser.add_argument("output_path", nargs=1, help="Path to output CSV")
    args = parser.parse_args()"""
    inst = Institute("Testinstitut", frozenset(["mail@testinstitut.de", "kontakt@testinstitut.de"]), frozenset([]))
    q = Query("Test super", "TS1", "Testkategorie", frozenset([inst]))
    export_to_csv([q], "/Users/felix/Software/institut-scraper")