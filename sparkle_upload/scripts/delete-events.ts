#!/usr/bin/env node -r esm -r ts-node/register

import admin from "firebase-admin";
import { initFirebaseAdminApp, makeScriptUsage } from "./lib/helpers";
import { resolve } from "path";
const fs = require("fs");
const csv = require("csv-parser");

const usage = makeScriptUsage({
  description:
    "Bulk upload events. Based on csv file with event details",
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
  eventId: string;
  venueId: string;  
}

fs.createReadStream(filePath)
  .pipe(csv())
  .on("data", async (event: events) => {
    await admin
      .firestore()
      .collection("venues")
      .doc(event.venueId)
      .collection("events")
      .doc(event.eventId)
      .delete()
      .then()
      .catch(function (err: string) {
        console.error("delete error:", err);
      });
  })
  .on("end", () => {
    console.log("Event deletion successfully processed");
  });
    
