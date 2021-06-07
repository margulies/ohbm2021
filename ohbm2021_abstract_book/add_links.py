import pandas as pd
from parser_web import main as parser


def add_urls(df_abstract, df_raw):
    df_abstract["pdf"] = None
    df_abstract["video"] = None

    media_links = pd.read_csv("ohbm-ALL-poster-links.csv")
    for idx, row in df_abstract.iterrows():

    return df_abstract

df_raw= parser(late_break=True)
df_abstract= pd.read_csv("2021_abstracts.csv", sep="€")
df_abstract = add_urls(df_abstract, df_raw)
df_abstract.to_csv("2021_abstracts.csv", sep="€", index=False)