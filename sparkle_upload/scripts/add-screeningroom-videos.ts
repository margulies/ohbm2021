#!/usr/bin/env node -r esm -r ts-node/register

var firebase = require("firebase/app");
require("firebase/auth");
require("firebase/firestore");

import admin from "firebase-admin";
import { initFirebaseAdminApp, makeScriptUsage } from "./lib/helpers";
import { resolve } from "path";
const fs = require("fs");
const csv = require("csv-parser");

const usage = makeScriptUsage({
  description:
    "Bulk upload videos to screening room template. Based on csv file with video details",
  usageParams: "PROJECT_ID [CREDENTIAL_PATH] VENUEID [EVENTS_CSV_FILE]",
  exampleParams: "co-reality-map [theMatchingAccountServiceKey.json] [venueid] [../../events.csv]",
});

const [projectId, credentialPath, filePath] = process.argv.slice(2);

if (!projectId || !credentialPath || !filePath) {
  usage();
}

initFirebaseAdminApp(projectId, {
  credentialPath: credentialPath
    ? resolve(__dirname, credentialPath)
    : undefined,
});

interface videos {
  location: string;
  title: string;
  authorName: string;
  thumbnailSrc?: string;
  videoSrc: string;
  category: string;
  subCategory?: string;
  videoId?: string;
}

fs.createReadStream(filePath)
  .pipe(csv())
  .on("data", async (video: videos) => {
    await admin
      .firestore()
      .collection("venues")
      .doc(video.location)
      .collection("screeningRoomVideos")
      .add({
        title: video.title,
        authorName: video.authorName,
        thumbnailSrc: video.thumbnailSrc,
        videoSrc: video.videoSrc,
        category: video.category,
        subCategory: video.subCategory,
      })
      .then()
      .catch(function (err: string) {
        console.error("Add event error:", err);
      });
  })
  .on("end", () => {
    console.log("Videos successfully processed");
  });
