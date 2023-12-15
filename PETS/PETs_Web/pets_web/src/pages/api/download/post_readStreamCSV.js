// ==============================|| PROJECT - POST DOWNLOAD CSV ||============================== //

import fs from "fs";
import path from 'path'
import { stringify } from "csv-stringify";

// Handles incoming HTTP requests
export default async function handler(req, res) {
    const url = req.body.url;
    // const fileName = url.split("/").pop(); // pop out the last split element
    const filepath = path.join(process.cwd(), url);

    // Check request method
    if (req.method !== "POST") {
        return res.status(405).send("Method Not Allowed");
    }

    // Create a CSV stringifier
    const stringifier = stringify({ header: true });
    // Create a readable stream
    const readableStream = fs.createReadStream(filepath);
    // Pipe the stringifier to the stream (read file & send data stream at the same time)
    stringifier.pipe(readableStream);

    // Listen for the 'finish' event
    stringifier.on("finish", async () => {
        // Read the CSV stream
        const csvFile = await fs.promises.readFile(filepath, "utf-8");
        // Send the CSV file as the response
        res.status(200).setHeader("Content-Type", "text/csv").send(csvFile);
    });

    // Uncomment this block if you want to write new rows to the CSV file in real time
    /*
    for (const row of newDocs) {
      // Write each row to the stringifier
      stringifier.write([row.name, row.email], "utf-8");
    }
    */

    // Signal the stringifier that it is finished
    stringifier.end();
}