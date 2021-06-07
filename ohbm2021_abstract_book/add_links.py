import pandas as pd


def add_urls(df_abstract):
    df_abstract["ics"] = None
    df_abstract["venu"] = None
    df_abstract["pdf"] = None
    df_abstract["video"] = None

    media_links = pd.read_csv("ohbm-ALL-poster-links.csv")
    for idx, row in df_abstract.iterrows():
        df_abstract.loc[idx, "venu"] = f"https://ohbm.sparkle.space/in/poster{row['submissionNumber']}"
        # df_abstract.loc[idx, "ics"] = f"https://firebasestorage.googleapis.com/v0/b/sparkle-ohbm.appspot.com/o/assets%2Fcalendars%2Fposters%2Fposter{row['submissionNumber']}.ics?alt=media"
    return df_abstract


df_abstract= pd.read_csv("2021_abstracts.csv", sep="€")
df_abstract = add_urls(df_abstract)
df_abstract.to_csv("2021_abstracts.csv", sep="€", index=False)