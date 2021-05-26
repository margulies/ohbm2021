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
    "Bulk upload events. Based on csv file with event details",
  usageParams: "PROJECT_ID [CREDENTIAL_PATH] [EVENTS_CSV_FILE]",
  exampleParams: "co-reality-map [theMatchingAccountServiceKey.json] [../../events.csv]",
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

interface events {
  location: string;
  name: string;
  host: string;
  description: string;
  start: number;
  duration: number;
  eventId?: string;
}

fs.createReadStream(filePath)
  .pipe(csv())
  .on("data", async (event: events) => {
    if (event.eventId) {
      await admin
        .firestore()
        .collection("venues")
        .doc(event.location)
        .collection("events")
        .doc(event.eventId)
        .update({
          name: event.name,
          host: event.host,
          description: event.description,
          start_utc_seconds: Number(event.start),
          duration_minutes: Number(event.duration),
          price: 0,
          collective_price: 0,
        })
        .then()
        .catch(function (err: string) {
          console.error("Add event error:", err); //process.exit(1);
        });
    } else {
      await admin
        .firestore()
        .collection("venues")
        .doc(event.location)
        .collection("events")
        .add({
          name: event.name,
          host: event.host,
          description: event.description,
          start_utc_seconds: Number(event.start),
          duration_minutes: Number(event.duration),
          price: 0,
          collective_price: 0,
        })
        .then()
        .catch(function (err: string) {
          console.error("Add event error:", err); //process.exit(1);
        });
    }
  })
  .on("end", () => {
    console.log("Events successfully processed");
  });
