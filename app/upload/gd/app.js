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

oauth2client.setCredentials({refresh_token: REFRESH_TOKEN});

const drive = google.drive({
    version: 'v3',
    auth: oauth2client
});

const filepath_name = process.env.FILENAME;
const filepath = path.join(filepath_name);

async function uploadFile () {
    try {
        const response = await drive.files.create({
            requestBody: {
                name: 'my-lab05-2drive.pdf',
                mimeType: mimeTypes.lookup(filepath_name)
            },
            media: {
                mimeType: mimeTypes.lookup(filepath_name),
                body: fs.createReadStream(filepath)
            }
        });
        
        console.log(response.data);
    } catch (error){
        console.log(error.message);
    }
}

uploadFile();