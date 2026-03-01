import { BoxClient, OAuthConfig, BoxOAuth } from "box-node-sdk";

import { loadEnvFile, env } from 'node:process';

// 1. Setup Configuration
loadEnvFile();
const config = new OAuthConfig({
    clientId: env.BOX_CLIENT_ID,
    clientSecret: env.BOX_CLIENT_SECRET,
});

const oauth = new BoxOAuth({ config: config });
const accessToken = {
    accessToken: env.BOX_ACCESS_TOKEN,
    refreshToken: env.BOX_REFRESH_TOKEN,
};
await oauth.tokenStorage.store(accessToken);

const client = new BoxClient({ auth: oauth });

import { createReadStream } from "fs"

async function uploadFile(FILENAME) {
    const attrs = { name: FILENAME, parent: { id: '0' } };
    const body = {
        attributes: attrs,
        file: createReadStream(env.FILENAME),
    };
    const files = await client.uploads.uploadFile(body);
    const file = files.entries[0];
    console.log(`File uploaded with id ${file.id}, name ${file.name}`);
}