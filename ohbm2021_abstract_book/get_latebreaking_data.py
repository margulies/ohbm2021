"""
Grab late breaking data and transform to the same format as the existing ones
Notes
For the links, poster ics links are:
https://firebasestorage.googleapis.com/v0/b/sparkle-ohbm.appspot.com/o/assets%2Fcalendars%2Fposters%2Fposter[SUBMISSION_ID].ics?alt=media

The venue links are:
https://ohbm.sparkle.space/in/poster[SUBMISSION_ID]

The poster and video links (pre-generated) are located in the enclosed .csv file.
"""
import os
import re
import pandas as pd
import numpy as np
from pandas.io.parsers import read_csv

from parser_web import main as parser


cols = ['submissionNumber', 'title', 'authors','institution', 'previewurl']

def authro_index_ref(df_accepted):
    """Create authro index reference."""
    authors = {}
    for i, row in df_accepted.iterrows():
        for speaker in row['speakers']['speaker']:
            speaker_id = int(speaker['@id'])
            if speaker_id not in authors:
                authors[speaker_id] = {'firstname': speaker['firstname'],
                                        'middlename': speaker['middlename'],
                                        'lastname': speaker['lastname'],
                                        'submissionNumber': set()}  # use set to prevent duplication
            if type(row['submissionNumber']) is list:
                for s in row['submissionNumber']:
                    authors[speaker_id]['submissionNumber'].add(s)
            else:
                authors[speaker_id]['submissionNumber'].add(row['submissionNumber'])
    return authors


def capitalise_name(x):
    """Capitalise names."""
    x = " ".join(i.capitalize() for i in x.split(" "))
    if len(x.split("-")) > 1:
        x = "-".join(i.capitalize() for i in x.split("-"))
    return x


def load_latebreaking():
    """Load late breaking abstract index or run the web parser."""
    if os.path.isfile("./latebreak_abstracts_content.pkl"):
        df_accepted = pd.read_pickle("latebreak_abstracts_content.pkl")
    else:
        df_accepted = parser(late_break=True)
    return df_accepted


def get_categories(df_accepted):
    """Get primary and secondary category numbers for posters."""
    df_accepted['primary_category'] = None
    df_accepted['secondary_category'] = None
    pc, sc = None, None
    for idx, row in df_accepted.iterrows():
        for cat in row["categories"]['category']:
            if cat['priorityOrder'] == '1':
                pc = _parse_category_name(cat['name'])
            elif cat['priorityOrder'] == '2':
                sc = _parse_category_name(cat['name'])
        df_accepted.loc[idx, 'primary_category'] = pc
        df_accepted.loc[idx, 'secondary_category'] = sc
    return df_accepted.loc[:, ['submissionNumber', 'primary_category', 'secondary_category']]


def _parse_category_name(name):
    """Some weird names"""
    if name == 'Informatics Other':
        return 'Neuroinformatics and Data Sharing Other'
    return name.replace('’', "'").replace(' La', 'La').replace(' Ea', 'Ea')


def load_categories():
    """Load the existing categories"""
    df_cat_exist = pd.read_csv("firstsubmission_categories_index.csv",
                               sep="€", header=None)
    df_cat_exist.columns = ["category", "poster_no"]
    poster_categories = {}
    for idx, row in df_cat_exist.iterrows():
        if not isinstance(row["poster_no"], str):
            poster_categories[row["category"]] = {}
            parent = row["category"]
        else:
            poster_categories[parent][row["category"]] = set(row["poster_no"].split(","))

    categories = {}
    for parent in poster_categories:
        sub_cats = poster_categories[parent].keys()
        for sub in sub_cats:
            if sub == "Other":
                categories[f"{parent} {sub}"] = parent
            else:
                categories[f"{sub}"] = parent
    return categories, poster_categories


def _update_categores(df_accepted, test=False):
    """Add category info from a new set of entries"""
    categories_finder, poster_categories = load_categories()
    df_latebreak_categories = get_categories(df_accepted)
    if test:
        poster_categories = {}

    for _, row in df_latebreak_categories.iterrows():
        # only using primary categories
        parent_cat = categories_finder[row["primary_category"]]

        if "Other" in row["primary_category"]:
            child_cat = "Other"
        else:
            child_cat = row["primary_category"]

        if parent_cat not in poster_categories:
            poster_categories[parent_cat] = {}
        if child_cat not in poster_categories[parent_cat]:
            poster_categories[parent_cat][child_cat] = set()
        poster_categories[parent_cat][child_cat].add(row["submissionNumber"])

    return poster_categories

def category_to_df(df_accepted, test=False):
    poster_categories = _update_categores(df_accepted, test=test)
    df_cat = pd.DataFrame()
    for key in poster_categories:
        sub_cats = {key: None}
        for sk in poster_categories[key]:
            sub_cats[sk] = ",".join(poster_categories[key][sk])
        df = pd.DataFrame(sub_cats, index=range(1)).T
        df_cat = pd.concat([df_cat, df], axis=0)
    return df_cat.reset_index()


if __name__ == "__main__":
    # create all files separately first
    df_accepted = load_latebreaking()
    df_accepted_late = df_accepted.loc[:, cols]
    df_accepted_late.to_csv("latebreaking_abstracts.csv", index=False,sep="€")
    df_abstract = pd.read_csv("firstsubmission_abstracts.csv", sep="€", header=None)
    df_abstract = pd.concat([df_abstract, df_accepted_late], axis=0)
    df_abstract.to_csv("2021_abstracts.csv", index=False,sep="€")

    poster_categories = category_to_df(df_accepted, test=False)
    poster_categories.to_csv("2021_categories_index.csv", index=False, sep="€")

    full_accepted = parser(late_break=False)
    authors = authro_index_ref(full_accepted)
    with open("2021_authors_index.csv","w", encoding='utf8') as f:
        for author in authors.values():
            if author['middlename'] is None:  # no mi
                f.write("%s€%s€%s\n" % (capitalise_name(author['lastname']),
                            capitalise_name(author['firstname']),
                            ",".join(author['submissionNumber'])))
            else:
                f.write("%s€%s %s€%s\n" % (capitalise_name(author['lastname']),
                                        capitalise_name(author['firstname']),
                                        capitalise_name(author['middlename']),
                                        ",".join(author['submissionNumber'])))
