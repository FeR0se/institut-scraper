import csv
import argparse
from os import PathLike
from pathlib import Path
from collections import defaultdict

from tqdm.contrib.concurrent import process_map

def load_links(filepath: str | PathLike):
    filepath = Path(filepath)
    with filepath.open("r", encoding="utf-8-sig") as fp:
        file = fp.read().splitlines()

    reader = csv.DictReader(file, delimiter=";")
    return [row for row in reader]

def export_to_csv(filepath: Path):
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape contact information from miz.org")

