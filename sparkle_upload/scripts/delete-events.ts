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
    "Bulk delete events. Based on csv file with event details",
  usageParams: "PROJECT_ID [CREDENTIAL_PATH] [EVENTS_TO_DELETE_CSV_FILE]",
  exampleParams: "co-reality-map [theMatchingAccountServiceKey.json] [events_to_delete.csv]",
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
  EventID: string;
  VenueID: string;
}

fs.createReadStream(filePath)
  .pipe(csv())
  .on("data", async (event: events) => {
    await admin
      .firestore()
      .collection("venues")
      .doc(event.VenueID)
      .collection("events")
      .doc(event.EventID)
      .delete()
      .then()
      .catch(function (err: string) {
        console.error("delete error:", err);
      });
  })
  .on("end", () => {
    console.log("Event deletion successfully processed");
  });
