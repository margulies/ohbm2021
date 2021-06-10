"""Parse poster info to a json
"""
import json
import re
from parser_web import main as parser
import utils as ut
import pandas as pd


def get_categories(categories):
    for cat in categories:
        if cat["priorityOrder"] == "1":
            pc = ut._parse_category_name(cat["name"])
        elif cat["priorityOrder"] == "2":
            sc = ut._parse_category_name(cat["name"])
    return [pc, sc]


def get_author_names(speakers):
    """Get author names"""
    authors = re.findall(r'\<[\/sup]*\>[, ]*([A-Za-z -.üÁ]*)\<[\/sup]*\>', speakers)
    return [auth for auth in authors if auth != '']


def find_pdf(row, media_links):
    title_web = row['title']
    email = row["speakers"]["speaker"][0]["email"]
    mask = media_links["Email"].isin([email]) & media_links["Title"].isin([title_web])
    if sum(mask) != 1:
        mask = media_links["Title"].isin([title_web])
    if sum(mask) != 1:
        mask = media_links["Email"].isin([email])
    if sum(mask) != 1:
        print(f"Cannot find relevant links for: {title_web}")
    return media_links.loc[mask, ['PDF Link', 'Thumbnail Link']].values.tolist()[0]


data = parser()
media_links = pd.read_csv("data/ohbm-ALL-poster-links.csv")
posters = {}
for idx, row in data.iterrows():
    pdf, thumbnail = find_pdf(row, media_links)
    current_poster = {
        'title': row['title'],
        'authorName': ",".join(get_author_names(row['authors'])),
        'authors': get_author_names(row['authors']),
        'introduction': row['purpose'],
        'methods': row['materialsMethods'],
        'results': row['results'],
        'conclusions': row['conclusion'],
        'iframeUrl': pdf,
        'thumbnailUrl': thumbnail,
        'category': get_categories(row["categories"]["category"]),
        'previewurl': row['previewurl'],
        }
    posters[f"poster{row['abstractNumber']}"] = current_poster

print(posters["poster1051"]['methods'])
with open("posters.json", 'w', encoding='utf8') as file:
    json.dump(posters, file, indent=2, ensure_ascii=False)
