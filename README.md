# Scripts for working with data related to OHBM 2021

_If you would like to **add or modify events** for OHBM 2021, instructions for preparing the necessary information is at the bottom of this page._

**Getting started:** In addition to the enclosed scripts, you'll need to create a `.env` file with:
  1. your login credentials for Firebase
  2. api information for Attendee Interactive

See the `.env.sample` for the required information.

# Compiling the abstract book

_Special thanks to @htwangtw for many contributions._

_All files used to generate the OHBM Abstract Book are located in the [`ohbm2021_abstract_book`](./ohbm2021_abstract_book) directory._

The `ipython` notebook [`ohbm_abstract.ipynb`](./ohbm2021_abstract_book/ohbm_abstract.ipynb) contains all the commands used to generate the `.csv` files required for compiling the [`ohbm2021_abstract_book.tex`](./ohbm2021_abstract_book/ohbm_abstract.ipynb) file. A note that the `.csv` files are delimited using `€` to avoid potential conflicts with the variety of characters used in the abstract content.

To compile the `.tex` file, run the following command **twice** from within the [`ohbm2021_abstract_book`](./ohbm2021_abstract_book) directory:

    lualatex -interaction=nonstopmode ohbm2021_abstract_book.tex

_Note: Compiling the full abstract book currently takes approximately an hour, but it'll get there..._

# Schedule

The primary file containing schedule information is [`OHBM2021_schedule.csv`](./schedule/OHBM2021_schedule.csv). This file is used to generate `ics` calendar files, which can be imported into any calendar software, as well as the `csv` file described below for importing the events into Sparkle.

The columns in the main schedule file are structured as described in the section on [Setting up the events file](#Setting-up-the-events-file-for-uploading:).

## Updating ICS for synced calendars

The [`OHBM2021_Schedule_All.ics`](./schedule/calendar/conference/OHBM2021_Schedule_All.ics) calendar file can be updated by modifying in a calendar software, exported and uploaded to Firebase storage in the directory: `assets/calendars/` [link](gs://sparkle-ohbm.appspot.com/assets/calendars), replacing the current version. This will automatically update all synced calendars.

### Posters

Posters (Abstracts) are assigned to standby times based on the combination of the [schedule file](./schedule/OHBM2021_schedule.csv), which specifies the times, and the session assignment, which is based on abstract categories. The categories and session assignments can be found in the [abstract data file](./schedule/abstract_assigned_for_schedule.csv). The code used to grab the times and create the schedule files for abstracts is in [OHBM_schedule_posters.ipynb](./schedule/OHBM_schedule_posters.ipynb).

### Converting the schedule file to calendar (`.ics`) and sparkle-readable files

The code for converting the [schedule file](./schedule/OHBM2021_schedule.csv) to calendars is available in [OHBM_schedule_to_calendars.ipynb](./schedule/OHBM_schedule_to_calendars.ipynb).

For uploading the output `.csv` file into Sparkle, see the section below.

<!--
### Optimizing scheduling
### Assigning posters to categories for stand-by times
### Sharing the schedule
-->

# Adding content to Sparkle

All scripts necessary for uploading content are available in the [sparkle_upload/scripts](sparkle_upload/scripts) directory. Please note for some of the scripts to work, it may be necessary to have a local copy of the [Sparkle repository](https://github.com/sparkletown/sparkle) as well.

To use scripts for batch uploading and modifying of events/venues, first run `npm install` from inside the [sparkle_upload](./sparkle_upload) directory. Further information about sparkle can be found at [here](https://github.com/sparkletown/sparkle).

### Setting up the events file for uploading:
To add events to sparkle, simply create a `.csv` file with one event per row that includes the following comma-delimited fields:


| Title | Speaker | Moderator | Date Start | Time Start | Date End | Time End | Location | TimeZoneBlock | Categories | UID | EVENTID
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  "Example Title", | "Jane Doe", | , | 20210622, | 140000, | 20210622, | 150000, | mainauditorium | AmericasEurope | keynote | , | , |

_If you prefer to make this file in excel, simply export the file as `.csv`_

**Tips:**
- If the field has multiple words, place quotes around it.
- If a specific field isn't necessary for your event, leave it blank by placing a `comma`
- `Moderator` can refer to a person that is moderating and/or an organization that is organizing. If some cases this can be used to describe content of the event.
- Dates are specified in UTC as `YYYYMMDD`
- Times are specified in UTC as `HHMMSS`
- `Location` refers to the venue name in Sparkle. If you don't know at this stage, simply write `TBD` and we'll sort that out on our end. This is updated regularly, though current options include: ['mainauditorium', 'symposiumhall1', 'symposiumhall2','symposiumhall3' 'symposiumhall4', 'posterhall', 'lounge', 'opendiscussion', 'exhibithall']
- `TimeZoneBlock` options are: `AmericasEurope`, `AmericasAsia`, `EuropeAsia`
- `Categories` refers to the program category, and currently includes the following options: ['Talairach', 'Keynote', 'Symposium', 'Poster Highlights', 'Posters', 'Sponsored Symposia', 'Social', 'Announcements', 'Roundtables', 'Exhibitors Hour']
- `UID` is the unique identifier used by `.ics` files to ensure that an event won't be duplicated when modified or re-imported
- `EVENTID` is the identifier used by Firebase (Sparkle) for the event

_If you have any specific needs that aren't met by these fields, please get in touch to discussion options._

### Adding new events:

The schedule `.csv` file described above can be used to upload events to Sparkle using the following command:

    ./add-event.ts sparkle-ohbm ./prodAccountKey.json [path to schedule.csv file]

### Modifying existing events:

If you find any errors in the schedule, please let us know and we'll get them fixed as soon as possible.

To modify events, it is first necessary to get the `eventID` associated with an event in the Firebase database. The following command will generate a file with all eventIDs that can be used for reference:

     ./get-events.ts sparkle-ohbm ./prodAccountKey.json > ./events.csv


**Next copy the `eventIDs` to the last column of the `.csv` schedule file** so that the event is linked to its place in Firebase. The schedule file can then be used to modify the existing event:

    ./add-event.ts sparkle-ohbm ./prodAccountKey.json [path to schedule.csv file that includes eventIDs]


### Deleting events
First get events and remove those to keep from csv:

    ./get-events.ts sparkle-ohbm ./prodAccountKey.json > ./events.csv

Then edit the `events.csv` file to only contain events you would like to delete. To be safe, rename file as `events_to_delete.csv`.

Then run the following to delete events listed in `./events_to_delete.csv`:

    ./delete-events.ts sparkle-ohbm ./prodAccountKey.json ./events_to_delete.csv


## Adding rooms/venues to Sparkle

To add new rooms/venues, best to send along a `.csv` spreadsheet with the following information:

- Template type
- Room/Venue name
- Link to space, if external to sparkle (e.g., Zoom link)
- Link to embeddable content, if venue type allows iframe. This can also be a live-stream link
- Brief description for landing page
- Where should the venue be locationed within Sparkle?
- Who are the 'owners' of the venue?

To create the venues based on this file:

    ./create-venues.ts sparkle-ohbm ./prodAccountKey.json [venues file].csv

### Adding `posterpage` venues to Sparkle

Same procedure as above, but the `.cvs` files should contain:

- Title
- Author name
- URL of poster
- URL of thumbnail
- URL of embedable video
- List of categories
- Poster ID number, if already assigned elsewhere

To create the posterpage based on this file:

    ./create-posterpage.ts sparkle-ohbm ./prodAccountKey.json [posterpages file].csv

### Adding video content to Sparkle `screeningroom` venues

A `cvs` file should contain:

- **Title** (if part of video subcategory, such as a symposium, begin `title` with `number`, such as `1.  [title]` or `Lecture 1. [title]`. This will be used for automatically sorting videos within a subcategory)
- **Author name** (if multiple authors, separate names with commas)
- **URL of thumbnail**
- **URL of embedable video**
- **Name of video category** (eg, Keynote, Symposium, etc...)
- **Name of video subcategory** (_optional_), (eg Title of symposium)
- **Video ID** (_optional_) , if already assigned elsewhere

To upload the screeningroom content based on this file:

    ./add-screeningroom-videos.ts sparkle-ohbm ./prodAccountKey.json [videos file].csv
