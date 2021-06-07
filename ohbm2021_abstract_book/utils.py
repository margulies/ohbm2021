import pandas as pd


exeption_cat = {
    'Neuroanatomy Other': 'Neuroanatomy, Physiology, Metabolism and Neurotransmission Other',
    'Informatics Other': 'Neuroinformatics and Data Sharing Other',
    'Emotion and Motivation Other': 'Emotion, Motivation and Social Neuroscience Other',
    'Non-Invasive Stimulation Methods Other':'Non-Invasive Methods Other',
    'Invasive Stimulation Methods Other': 'Invasive Methods Other',
    'Perception and Attention Other':'Perception, Attention and Motor Behavior Other',
    'Other Methods':'Modeling and Analysis Methods Other',
    'Social Neuroscience Other': 'Emotion, Motivation and Social Neuroscience Other'
}


def add_urls(df_abstract, df_raw):
    """Add associated pdf and video link to abstract"""
    df_abstract["pdf"] = None
    df_abstract["video"] = None
    df_abstract = df_abstract.set_index('submissionNumber')
    df_raw = df_raw.set_index('submissionNumber')
    media_links = pd.read_csv("ohbm-ALL-poster-links.csv")
    media_links['Title'] = media_links['Title'].apply(str.lower)

    for idx, row in df_abstract.iterrows():
        if str(idx) in df_raw.index:
            speakers = df_raw.loc[str(idx), 'speakers']['speaker']
            email = speakers[0]['email']
            # if isinstance(speakers, list):
            #     email = speakers[0]['email']
            # else:
            #     email = speakers['email']
            title = str.lower(row['title'])
            # filter out people with more than one first author paper
            mask = media_links['Email'].isin([email]) & media_links['Title'].isin([title])
            # this is not entirely reliable
            if sum(mask) == 1:
                pdf, video = media_links.loc[mask, ['PDF Link', 'Thumbnail Link']].values.tolist()[0]
                df_abstract.loc[idx, "pdf"] = pdf
                df_abstract.loc[idx, "video"] = video
    return df_abstract.reset_index()


def compile_authros_index(df_accepted):
    authors = authro_index_ref(df_accepted)
    df_authors = pd.DataFrame(columns=['lastname', 'firstname', 'submissionNumber'])
    for author in authors.values():
        if author['middlename'] is None:
            df = pd.DataFrame([_capitalise_name(author['lastname']),
                               _capitalise_name(author['firstname']),
                               ",".join(sorted(author['submissionNumber']))],
                              index=['lastname', 'firstname', 'submissionNumber'])
        else:
            df = pd.DataFrame([_capitalise_name(author['lastname']),
                               f"{_capitalise_name(author['firstname'])} {_capitalise_name(author['middlename']).replace('.', '')}",
                               ",".join(sorted(author['submissionNumber']))],
                              index=['lastname', 'firstname', 'submissionNumber'])
        df_authors = pd.concat([df_authors, df.T], axis=0)
    df_authors = df_authors.sort_values('firstname').sort_values('lastname')
    return df_authors


def category_to_df(df_accepted, latebreaking_only=True):
    categories_finder, first_batch = _load_categories()
    categories_finder['Polarized light imaging (PLI)'] = 'Novel Imaging Acquisition Methods'
    categories_finder['Optical coherence tomography (OCT)'] = 'Novel Imaging Acquisition Methods'
    if latebreaking_only:
        poster_categories = _update_categores(df_accepted,
                                    categories_finder,
                                    {})
    else:
        poster_categories = _update_categores(df_accepted,
                                            categories_finder,
                                            first_batch)
    df_cat = pd.DataFrame()
    for key in poster_categories:
        sub_cats = {key: None}
        for sk in poster_categories[key]:
            sub_cats[sk] = ",".join(sorted(poster_categories[key][sk]))
        df = pd.DataFrame(sub_cats, index=range(1)).T
        index = df.index.tolist()
        if 'Other' in index and index[-1] != 'Other':
            index.remove('Other')
            index.append('Other')
        df_cat = pd.concat([df_cat, df.loc[index, :]], axis=0)
    return df_cat.reset_index()


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


def _capitalise_name(x):
    """Capitalise names."""
    x = " ".join(i.capitalize() for i in x.split(" "))
    if len(x.split("-")) > 1:
        x = "-".join(i.capitalize() for i in x.split("-"))
    return x


def _get_categories(df_accepted):
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
    return df_accepted.loc[:, ['submissionNumber', 'title', 'primary_category', 'secondary_category']]


def _parse_category_name(name):
    """Some weird names"""
    if name in exeption_cat:
        return exeption_cat[name]
    return name.replace('’', "'").replace(' La', 'La').replace(' Ea', 'Ea').replace("/ V", "/V")


def _load_categories():
    """Load the existing categories"""
    df_cat_exist = pd.read_csv("firstsubmission_categories_index.csv",
                               sep="€", header=None)
    df_cat_exist.columns = ["category", "poster_no"]
    poster_categories = {}
    for _, row in df_cat_exist.iterrows():
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


def _update_categores(df_accepted, categories_finder, poster_categories):
    """Add category info from a new set of entries"""
    update = poster_categories.copy()
    df_latebreak_categories = _get_categories(df_accepted)

    for _, row in df_latebreak_categories.iterrows():
        for cat in ["primary_category", "secondary_category"]:

            parent_cat = categories_finder.get(row[cat], False)
            if (
                "Other" in row[cat]
                and row[cat] == "Non-Invasive Methods Other"
                or "Other" not in row[cat]
            ):
                child_cat = row[cat]
            else:
                child_cat = "Other"

            if isinstance(parent_cat, str):
                if parent_cat not in update:
                    update[parent_cat] = {child_cat: set()}
                if child_cat not in update[parent_cat]:
                    update[parent_cat][child_cat] = set()
                update[parent_cat][child_cat].add(row["submissionNumber"])
            else:
                print(row["title"])
                print("cannot find:", row[cat])
                print("category info:", row[["primary_category", "secondary_category"]].tolist())
    return update
