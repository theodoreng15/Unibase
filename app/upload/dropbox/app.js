const { Dropbox } = require("dropbox");
const path = require("path");
const fs = require("fs");
const proc = require('node:process');

proc.loadEnvFile();

const CLIENT_ID = process.env.CLIENT_ID;
const CLIENT_SECRET = process.env.CLIENT_SECRET;
const REFRESH_TOKEN = process.env.REFRESH_TOKEN;

const dbx = new Dropbox({
    clientId: CLIENT_ID,
    clientSecret: CLIENT_SECRET,
    refreshToken: REFRESH_TOKEN
});

const filepath_name = process.env.FILENAME;
const filepath = path.join(filepath_name);

async function uploadFile() {
    try {
        const contents = fs.readFileSync(filepath);
        const response = await dbx.filesUpload({
            path: '/' + path.basename(filepath_name),
            contents: contents
        });

        console.log(response.result);
    } catch (error) {
        console.log(error.message);
    }
}

uploadFile();
