import os
import re

from pathlib import Path


def clean_html(raw_html: str):
    """Clean HTML elements"""
    cleanr = re.compile(
        "<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});|(?:\n|\t|\r|\xa0)"
    )
    cleantext = re.sub(cleanr, "", raw_html)
    cleantext = cleantext.replace(
        "(adsbygoogle = window.adsbygoogle || []).push({});", ""
    )
    return cleantext


def write_report_txt(filename: str, report: dict):
    """Write"""

    parent_dir = Path(__file__).resolve().parent
    download_location = os.path.join(parent_dir, "datasets")
    os.makedirs(download_location, exist_ok=True)

    file = os.path.join(download_location, filename)
    with open(file, "w") as f:
        f.write(report["title"])
        f.write("\n\n")
        f.writelines("\n".join(report["body"]))
