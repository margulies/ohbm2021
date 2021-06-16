#!/usr/bin/env node
const posters = require('./posters.backup.json');
const fs = require('fs');

const updates = require('./updated_content_and_links');

/*
const csv = fs.readFileSync("updated_content_and_links.csv", "utf-8");
const lines = csv.split("\n");
const head = lines.shift();
//posterId,title,Name of Presenter,introVideoUrl,thumbnailUrl,Submitter Email,primaryCategoryParent,secondaryCategoryParent,Primary Category,Secondary Category
function stripQuotes(v) {
    if(v[0] == '"') return v.substring(1, v.length-2);
    return v;
}

lines.forEach(line=>{
    const cols = line.split(",");
    const id = stripQuotes(cols[0]);
    const title = stripQuotes(cols[1]);
    //console.log(id, title);

    //look for poster
    const poster = posters["poster"+id];
    //console.dir(poster.title);
    if(title != poster.title) {
        console.log("title changed", id, title, "\n",poster.title);
    }
});
*/

updates.forEach(update=>{
    //console.dir(update);
    /*
 {
  posterId: '2808',
  title: 'Ongoing Alpha EEG Power Predicts Digits-in-Noise Recognition and Perceived Clarity',
  'Name of Presenter': 'Thomas Houweling',
  introVideoUrl: 'https://player.vimeo.com/video/562951248',
  thumbnailUrl: 'https://anyscreeninc.com/PF/OHBM/2021/OHBM-Ed-Courses-and-Poster-Presenters/video_files/Thomas_Houweling60ac199b3aad8/thumb.jpg',
  'Submitter Email': 'thomas.houweling@psychologie.uzh.ch',
  primaryCategoryParent: 'Language',
  secondaryCategoryParent: 'Novel Imaging Acquisition Methods',
  'Primary Category': 'Speech Perception',
  'Secondary Category': 'EEG'
}

    */
    const poster = posters["poster"+update.posterId];
    /*
    if(update.title != poster.title) {
        console.log(update.posterId, update.title, "\n -- ", poster.title);
    }
    */
    poster.title = update.title;
    poster.introVideoUrl = update.introVideoUrl;
    poster.category = [ update.primaryCategoryParent, update.secondaryCategoryParent ];
    //poster.name = "Poster "+update.posterId;
    //poster.chatTitle = "Poster "+update.posterId;
});

fs.writeFileSync("posters.json", JSON.stringify(posters, null, 4));
