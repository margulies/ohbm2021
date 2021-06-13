#!/usr/bin/env node -r esm -r ts-node/register

import admin from "firebase-admin";
import { initFirebaseAdminApp, makeScriptUsage } from "./lib/helpers";
import { resolve } from "path";
const fs = require("fs");
const csv = require("csv-parser");

const usage = makeScriptUsage({
  description:
    "Bulk upload posterpages. Based on csv file with poster details",
  usageParams: "PROJECT_ID [CREDENTIAL_PATH] [EVENTS_CSV_FILE]",
  exampleParams: "co-reality-map [theMatchingAccountServiceKey.json] [posterpages.csv]",
});

const [projectId, credentialPath, filePath] = process.argv.slice(2);

if (!projectId || !credentialPath || !filePath) {
  usage();
}

interface posterpage {
  name: string;
  title: string;
  authorName?: string;
  iframeUrl?: string;
  introVideoUrl?: string;
  thumbnailUrl?: string;
  category?: string;
  contactEmail?: string;
  moreInfoUrl?: string;
  parentId: string;
  chatTitle: string;
  moreInfoUrlTitle?: string;
}

// const venueId = name.replace(/\W/g, "").toLowerCase();

initFirebaseAdminApp(projectId, {
  credentialPath: credentialPath
    ? resolve(__dirname, credentialPath)
    : undefined,
});

fs.createReadStream(filePath)
  .pipe(csv())
  .on("data", async (poster: posterpage) => {
    const categories = poster.category ? poster.category.split(',') : "";
    await admin
      .firestore()
      .collection("venues")
      .doc(poster.name)
      .set({
        template: "posterpage",
        chatTitle: poster.chatTitle,
        attendeesTitle: "Attendees",
        parentId: poster.parentId,
        name: poster.title,
        iframeUrl: poster.iframeUrl,
        config: {
          landingPageConfig: {
            coverImageUrl: "",
            subtitle: "",
            presentation: [],
            checkList: [],
          },
        },
        host: {
          icon: "",
        },
        poster: {
          authorName: poster.authorName,
          introVideoUrl: poster.introVideoUrl,
          thumbnailUrl: poster.thumbnailUrl,
          title: poster.title,
          categories: categories,
          //text: poster.text,
          //authorUserId: poster.authorUserId,
          //abstractURL: poster.abstractURL,
          contactEmail: poster.contactEmail,
          moreInfoUrl: poster.moreInfoUrl,
          moreInfoUrlTitle: poster.moreInfoUrlTitle,
        },
        owners: ["MmLlloenTiO9BRxui8tA4YsTgS13","QYMwGyzmj1UYctLDBEgPf7ZdAhF3","nRW5gaGOIsP9OpWz6xUr9rH13be2"], // NEED TO ADD PRESENTER ID
        isLive: false,
        code_of_conduct_questions: [],
        profile_questions: [],
        theme: {
          primaryColor: "#bc271a",
        }
        //termsAndConditions: TermOfService[] = [],
        // height,
        // width,
      })
      .then()
      // add in for situation where posterpage doesn't yet exist
  })
  .on("end", () => {
    console.log("posters successfully updated")
  })
