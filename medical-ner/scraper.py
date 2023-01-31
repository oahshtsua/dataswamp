import requests
from bs4 import BeautifulSoup, element

from utils import clean_html, write_report_txt

BASE_URL = "https://medical-transcription-sample-reports.blogspot.com/"

archive_urls = []
reports = []


def scrape():
    base_page = BeautifulSoup(requests.get(BASE_URL).text, "html.parser")
    archive_div = base_page.find(id="BlogArchive1_ArchiveMenu")
    archive_options = archive_div.find_all("option")

    for option in archive_options[1:]:
        archive_urls.append(option["value"])

    for url in archive_urls:
        scrape_page(url)

    for i, report in enumerate(reports):
        write_report_txt(f"report_{i}.txt", report)

    return reports


def scrape_page(page_url: str):
    """Scrape Archive Page for articles"""

    print(page_url)

    archive_page = BeautifulSoup(requests.get(page_url).text, "html.parser")
    articles = archive_page.find_all("div", "post hentry uncustomized-post-template")

    for article in articles:
        reports.append(scrape_article(article))


def scrape_article(article: element.Tag) -> dict:
    """Scrape individual Article"""

    title = clean_html(article.find("h3").text)
    print(title)

    old_style = article.find(
        "span", attrs={"style": "font-family: Arial, Helvetica, sans-serif;"}
    )
    mid_style = article.find("div", attrs={"style": "text-align: left;"})
    new_style = article.find("p")

    if old_style != None:
        paras = article.find_all("span")
    elif mid_style != None and old_style == None:
        paras = article.find("div", attrs={"style": "text-align: left;"}).contents
    elif new_style != None:
        paras = article.find_all("p")
    else:
        paras = [article]

    body = []

    for para in paras:
        if (
            old_style
            and para.has_attr("style")
            and para["style"] == "color: blue;"
            and para.has_attr("class")
            and para["class"] == "post-author vcard"
        ):
            break

        cleaned_text = clean_html(para.text)
        body.append(cleaned_text) if cleaned_text != "" else None

    return {"title": title, "body": body}


if __name__ == "__main__":
    r = scrape()
    print("Done")
