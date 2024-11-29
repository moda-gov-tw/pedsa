// ==============================|| PROJECT - GET LIST DIR ||============================== //

import fs from "fs";
import path from 'path'

// Handles incoming HTTP requests
export default async function handler(req, res) {
    const targetDir = req.query.targetDir;
    const RESTRICTED_DIR = path.resolve(process.cwd(), 'download_folder');

    const targetDirRegex = /^(enc|dec)\/(k|syn|dp)\/[a-zA-Z][a-zA-Z0-9_]*$/;
    if (!targetDirRegex.test(targetDir)) {
        return res.status(400).json({ status: 0, msg: 'Invalid directory format', obj: [] });
    }

    try {
        // const filepath = (targetDir.startsWith("..")) ? path.resolve(targetDir) : path.join(process.cwd(), targetDir);

        // Check request method
        if (req.method !== "GET") {
            return res.status(405).send("Method Not Allowed");
        }

        const normalizedTargetDir = path.normalize(targetDir).replace(/^(\.\.(\/|\\|$))+/, '');
        const resolvedPath = path.resolve(RESTRICTED_DIR, normalizedTargetDir);
        
        if (!resolvedPath.startsWith(RESTRICTED_DIR)) {
            return res.status(400).json({ status: 0, msg: 'Access to this directory is restricted', obj: [] });
        }

        const stats = await fs.promises.stat(resolvedPath);
        if (!stats.isDirectory()) {
            return res.status(400).json({ status: 0, msg: 'The path is not a directory', obj: [] });
        }

        // read list of dir.
        // const files = await fs.readdirSync(resolvedPath);
        const files = await fs.promises.readdir(resolvedPath);
        // console.log(files);

        // Turn files & size into JSON of array
        const fileList = files.map((file) => {
            return {
                fileName: file,
                url: path.join('download_folder',targetDir, file),
                // size: fs.statSync(filepath + "/" + file).size,
            };
        });

        return res.status(200).json({ status: 1, msg: '', obj: fileList });
    }
    catch (error) {
        // console.log("[API GET listDir] ERROR\n", error);
        if (error.errno == -2) {
            console.log("------------------------------");
            return res.status(200).json({ status: 0, msg: `Error: No such file or directory, ${targetDir}`, obj: [] });
        }
        else
            return res.status(500).json({ status: -1, msg: `Unexpected ERROR`, obj: [] });
    }
}