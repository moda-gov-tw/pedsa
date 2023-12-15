// ==============================|| PROJECT - GET LIST DIR ||============================== //

import fs from "fs";
import path from 'path'

// Handles incoming HTTP requests
export default async function handler(req, res) {
    const targetDir = req.query.targetDir;
    try {
        const filepath = (targetDir.startsWith("..")) ? path.resolve(targetDir) : path.join(process.cwd(), targetDir);

        // Check request method
        if (req.method !== "GET") {
            return res.status(405).send("Method Not Allowed");
        }

        // read list of dir.
        const files = await fs.readdirSync(filepath);
        console.log(files);

        // Turn files & size into JSON of array
        const fileList = files.map((file) => {
            return {
                fileName: file,
                url: path.join(targetDir, file),
                // size: fs.statSync(filepath + "/" + file).size,
            };
        });

        return res.status(200).json({ status: 1, msg: '', obj: fileList });
    }
    catch (error) {
        console.log("[API GET listDir] ERROR\n", error);
        if (error.errno == -2) {
            console.log("------------------------------");
            return res.status(200).json({ status: 0, msg: `Error: No such file or directory, ${targetDir}`, obj: [] });
        }
        else
            return res.status(500).json({ status: -1, msg: `Unexpected ERROR`, obj: [] });
    }
}