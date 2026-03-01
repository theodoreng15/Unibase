const { google } = require("googleapis")
const path = require("path")
const fs = require("fs")
const mimeTypes = require("mime-types")
const proc = require('node:process');

proc.loadEnvFile();

const CLIENT_ID = process.env.CLIENT_ID;
const CLIENT_SECRET = process.env.CLIENT_SECRET;

const REDIRECT_URI = process.env.REDIRECT_URI;
const REFRESH_TOKEN = process.env.REFRESH_TOKEN;

const oauth2client = new google.auth.OAuth2(
    CLIENT_ID,
    CLIENT_SECRET,
    REDIRECT_URI
);

oauth2client.setCredentials({ refresh_token: REFRESH_TOKEN });

const drive = google.drive({
    version: 'v3',
    auth: oauth2client
});

const filepath_name = process.env.FILENAME;
const filepath = path.join(filepath_name);

async function deleteFile(FILE_ID) {
    try {
        const response = await drive.files.delete({
            fileId: FILE_ID,
        });
        console.log(response.data, response.status);
    } catch (error) {
        if (error == 204){
            console.log(error.message, ": file deleted");
        }
    }
}