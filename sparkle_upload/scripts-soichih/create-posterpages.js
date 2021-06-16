#!/usr/bin/env node
const config = require('./config');
const admin = require('firebase-admin');
const keywordExtractor = require('keyword-extractor');

admin.initializeApp(config.firebase);

//ref https://github.com/margulies/ohbm2021/blob/main/sparkle_upload/scripts/create-posterpages.ts

//from #general
const posters = require('./posters.json');
const db = admin.firestore();
const venuesRef = db.collection('venues');

async function update() {
    for(const posterid in posters) {
        const poster = posters[posterid];
        //console.log(posterid);
        //console.dir(poster);

        const set = {
            poster: {},
            template: "posterpage",
            parentId: "posterhall",
            name: posterid,
            config: {
                landingPageConfig: {
                    coverImageUrl: "", 
                    subtitle: "", 
                    presentation: [], 
                    checkList: [], 
                },
            },
            host: { icon: "", },
            owners: [], // NEED TO ADD PRESENTER ID
            isLive: false,
            code_of_conduct_questions: [], 
            profile_questions: [], 
            theme: { primaryColor: "", }
        }
        //console.dir(set);
        //try {
        const ref = venuesRef.doc(posterid);
        ref.get().then(async snapshot=>{
            if(snapshot.exists) console.log("exists", posterid);
            else {
                console.log("doesn't exists", posterid, "setting initial content");
                await ref.set(set);
            }
        });
        //} catch (err) {
        //    console.error(err);
        //}
    }
}
update();


