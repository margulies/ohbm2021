"""
Grab late breaking data and transform to the same format as the existing ones
"""
import pandas as pd
from parser_web import main as parser
from utils import compile_authros_index, category_to_df


cols = ['submissionNumber', 'title', 'authors','institution', 'previewurl']


def main():
    # create file for late breaking poster separately
    df_accepted = parser(late_break=True)
    df_abstract = df_accepted.loc[:, cols]
    for idx, _ in df_abstract.iterrows():
        df_abstract.loc[idx, 'title'] = df_abstract.loc[idx, 'title'].replace('\n', ' ')
    df_abstract.to_csv("latebreaking_abstracts.csv", index=False,sep="€")
    # concatnate late breaking poster and first batch of submission
    df_first= pd.read_csv("firstsubmission_abstracts.csv", sep="€")
    df_abstract = pd.concat([df_first, df_abstract], axis=0)

    df_abstract.to_csv("2021_abstracts.csv", index=False, sep="€")

    # get all the posters
    df_accepted = parser(late_break=False)

    poster_categories = category_to_df(df_accepted, latebreaking_only=True)
    poster_categories.to_csv("2021_categories_index.csv", index=False, sep="€")

    # df_authors = compile_authros_index(df_all_abstracts)
    df_authors = compile_authros_index(df_accepted)
    df_authors.to_csv("2021_authors_index.csv", index=False, sep="€")


if __name__ == "__main__":
    main()
