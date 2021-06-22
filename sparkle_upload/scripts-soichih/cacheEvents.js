#!/usr/bin/env node
const config = require('./config');
const admin = require('firebase-admin');
const fs = require('fs');
const async = require('async');

admin.initializeApp(config.firebase);

async function cache() {

    const db = admin.firestore();

    const venues = await db.collection('venues').get();
    const venueIds = [];
    venues.forEach(v=>{
        venueIds.push(v.id);
    });
    
    const allEvents = [];
    async.forEach(venueIds, (id, next)=>{
        console.log("loading event s for ---", id);
        const events = db.collection('venues/'+id+'/events').get().then(events=>{
            events.forEach(event=>{
                console.log("  ",event.id);
                const e = event.data();
                
                //sparkle wants some extra things..
                e.id = event.id;
                e.venueId = id;

                allEvents.push(e);
            });
            next();
        });
    }, err=>{
        console.log("saving events.json (just in case)");
        fs.writeFileSync("events.json", JSON.stringify(allEvents));

        console.log("then uploading it to gs://");
        const bucket = admin.storage().bucket("gs://sparkle-ohbm.appspot.com");
        const file = bucket.file('assets/cache/events.json');
        const stream = file.createWriteStream({metadata: {contentType: 'application/json'}});
        stream.write(JSON.stringify(allEvents));
        stream.end();
        stream.on('finish', ()=>{
            console.log("finished");
        });
        stream.on('error', console.error);
    });
}

cache();
