"""
Grab late breaking data and transform to the same format as the existing ones
Notes
For the links, poster ics links are:
https://firebasestorage.googleapis.com/v0/b/sparkle-ohbm.appspot.com/o/assets%2Fcalendars%2Fposters%2Fposter[SUBMISSION_ID].ics?alt=media

The venue links are:
https://ohbm.sparkle.space/in/poster[SUBMISSION_ID]

The poster and video links (pre-generated) are located in the enclosed .csv file.
"""
import pandas as pd
from parser_web import main as parser
from utils import compile_authros_index, category_to_df


cols = ['submissionNumber', 'title', 'authors','institution', 'previewurl']


def main():
    # create file for late breaking poster separately
    df_accepted = parser(late_break=True)
    df_accepted_late = df_accepted.loc[:, cols]
    df_accepted_late.to_csv("latebreaking_abstracts.csv", index=False,sep="€")
    # concatnate late breaking poster and first batch of submission
    df_abstract = pd.read_csv("firstsubmission_abstracts.csv", sep="€")
    df_abstract = pd.concat([df_abstract, df_accepted_late], axis=0)
    df_abstract.to_csv("2021_abstracts.csv", index=False,sep="€")

    # get all the posters
    df_all_abstracts = parser(late_break=False)

    poster_categories = category_to_df(df_accepted)
    poster_categories.to_csv("2021_categories_index.csv", index=False, sep="€")

    df_authors = compile_authros_index(df_all_abstracts)
    df_authors.to_csv("2021_authors_index.csv", index=False, sep="€")

if __name__ == "__main__":
    main()
