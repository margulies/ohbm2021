import os
import requests
import pandas as pd
from bs4 import BeautifulSoup as Soup
import xmltodict
from decouple import config


df_cols = [
    "abstractNumber",
    "submissionNumber",
    "abstractType",
    "authors",
    "institution",
    "title",
    "purpose",
    "materialsMethods",
    "results",
    "conclusion",
    "reference",
    "latebreakingFlag",
    "acceptedFlag",
    "completedFlag",
    "categories",
    "previewurl",
    "speakers",
    "figures",
]


def compile_pd_dict(input_dict, instance_dict):
    while input_dict:
        key, item = input_dict.popitem()
        k = key.replace("@", "")
        if k in df_cols:
            if isinstance(item, dict):
                if "speaker" in item:
                    speakers = item["speaker"].copy()
                    if type(speakers) == list:
                        item.update({"speaker": speakers})
                    else:
                        item.update({"speaker": [speakers]})
            instance_dict[k] = item
    return instance_dict, input_dict


def web2list():
    apiKey = config("AI_API_KEY")  # Key in .env
    # For references and additional content, add the following after getAbstracts
    # (may be necessary to call each poster individually):
    # &includeAbstractFormData=1
    response = requests.get(
        f"https://ww4.aievolution.com/hbm2101/?do=cnt.getservice&service=getAbstracts&apiKey={apiKey}"
    )
    res = response.text
    soup = Soup(res, "xml")  # or use: Soup(res, 'html.parser')
    res_text = soup.prettify()

    o = xmltodict.parse(res_text)  # INPUT: XML_STRING
    return o["rst"]["abstracts"]["abstract"]


def read_poster_list(poster_id_file):
    with open(poster_id_file, "r") as f:
        abstract_id = [item.split()[0] for item in f.readlines()]
    return abstract_id


def main(late_break=False):
    late_abstract_list = read_poster_list("data/latebreaking_abstracts_list.csv")
    first_abstract_list = read_poster_list(
        "data/firstsubmission_abstracts_list.csv"
    )
    print(f"number of late breaking: {len(late_abstract_list)}")
    print(f"number of first batch: {len(first_abstract_list)}")

    if os.path.isfile("data/abstracts_content.pkl"):
        df = pd.read_pickle("data/abstracts_content.pkl")
    else:
        abstract_list = web2list()
        consolidated_dict = {}
        print(len(abstract_list))
        for original in abstract_list:
            current = original.copy()
            instance_dict, _ = compile_pd_dict(current, {})
            if original.get("@id") not in consolidated_dict:
                consolidated_dict.update(
                    {original.get("@id"): instance_dict.copy()}
                )
            else:
                print("ID exist...")
        df = pd.DataFrame(consolidated_dict).T
        df = df[df_cols]
        df.to_pickle("data/abstracts_content.pkl")

    bool_late = df["abstractNumber"].isin(late_abstract_list)
    bool_first = df["abstractNumber"].isin(first_abstract_list)
    missing = set(first_abstract_list) - set(
        df["abstractNumber"][bool_first].tolist()
    )
    if late_break:
        df_late = df[bool_late]
        df_late.to_pickle("data/latebreak_abstracts_content.pkl")
        return df_late
    else:
        df_accepted = pd.concat([df[bool_first], df[bool_late]], axis=0)

        print(f"After filtering: {df_accepted.shape[0]}")
        print("Missing from database:")
        print(missing)
        return df_accepted


if __name__ == "__main__":
    main()


def test_match_unparsed():  # comment out this test as I don't have the band width
    """Check if the data were missed during recursion."""
    abstract_list = web2list()
    df = pd.read_pickle("data/abstracts_content.pkl")
    assert len(abstract_list) == len(df)


def test_match_submission_id():
    """Check submissionNumber against 'Poster No' in the parsed dataset."""
    df = pd.read_pickle("data/abstracts_content.pkl")
    ref = pd.read_csv(
        "abstracts_with_keywords_and_categories.csv"
    ).sort_values("Poster No")
    ref_sub = set(ref["Poster No"].apply(str).tolist())
    target_sub_raw = set(df["submissionNumber"].tolist())
    missing = ref_sub - target_sub_raw
    assert len(missing) == 0

    # Filter by labels provide by the web
    df_filtered = df[
        (df["abstractType"] == "Abstract Submission")
        & (df["acceptedFlag"] == "Yes")
        & (df["completedFlag"] == "Yes")
    ]
    target_sub_filtered = set(df_filtered["submissionNumber"].tolist())
    assert ref_sub == target_sub_filtered
    assert len(ref_sub) == len(target_sub_filtered)
