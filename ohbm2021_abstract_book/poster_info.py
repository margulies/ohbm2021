"""Parse poster info to a json
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
from collections import Counter
from string import punctuation as PUNCTUATION


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


def get_author_names(authors):
    """Parse the 'author' field"""
    authors = re.findall(r'\<[\/sup]*\>[, ]*([\w -.]*)\<[\/sup]*\>', authors)
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


def clean_middlename(middlename):
    if isinstance(middlename, str):
        return "".join(re.findall("[A-Za-z ]+", middlename))
    else:
        return None


def clean_first_lastname(name):
    return ut._capitalise_name(name)


def get_author_info(speakers):
    all_speakers = {}
    for speak in speakers['speaker']:
        if speak['middlename']:
            name = [clean_first_lastname(speak['firstname']),
                    # clean_middlename(speak['middlename']),
                    clean_first_lastname(speak['lastname'])]
        else:
            name = [clean_first_lastname(speak['firstname']),
                    clean_first_lastname(speak['lastname'])]

        current_speaker = {
            'name': ' '.join(name),
            'affiliation':speak['company'],
            'presentingAuthor': speak['@role'] == 'AbsAuthor',
        }
        all_speakers[f"speaker{speak['@id']}"] = current_speaker
    return all_speakers


data = parser()
media_links = pd.read_csv("data/ohbm-ALL-poster-links.csv")
with open("abstract.json", "r") as f:
    abstract_keywords = json.load(f)

posters = {}
for idx, row in data.iterrows():
    pdf, thumbnail = find_pdf(row, media_links)
    speakers_details = get_author_info(row['speakers'])
    author_names = []
    for id in speakers_details:
        if speakers_details[id]['presentingAuthor']:
            presenter = speakers_details[id]['name']
        author_names.append(speakers_details[id]['name'])
    current_poster = {
        'title': row['title'],
        'authorName': ",".join(author_names),
        'authors': author_names,
        'introduction': row['purpose'],
        'methods': row['materialsMethods'],
        'results': row['results'],
        'conclusions': row['conclusion'],
        'iframeUrl': pdf,
        'thumbnailUrl': thumbnail,
        'category': get_categories(row["categories"]["category"]),
        'previewurl': row['previewurl'],
        'presenter': presenter
        }

    # for abstr in abstract_keywords:
    #     if abstr['number'] == int(row['abstractNumber']):
    #         current_poster['softwareDemo'] = abstr['software-demo']
    #         # current_poster['keywords'] = abstr['keywords'] + abstr['abstract']

    posters[f"poster{row['abstractNumber']}"] = current_poster

with open("posters.json", 'w', encoding='utf8') as file:
    json.dump(posters, file, indent=2, ensure_ascii=False)
