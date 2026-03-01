const express = require('express');
const { BoxOAuth, OAuthConfig } = require('box-node-sdk/box');
const proc = require('node:process');

// 1. Setup Configuration
proc.loadEnvFile();
const config = new OAuthConfig({
    clientId: proc.env.BOX_CLIENT_ID,
    clientSecret: proc.env.BOX_CLIENT_SECRET,
});
const oauth = new BoxOAuth({ config: config });

const app = express();
const PORT = 3000;

// 2. Start the flow
app.get('/login', (req, res) => {
    const authorizeUrl = oauth.getAuthorizeUrl({
        // This MUST match what's in your Box Dev Console
        redirect_uri: `http://localhost:${PORT}/callback` 
    });
    res.redirect(authorizeUrl);
});

// 3. Capture the code
app.get('/callback', async (req, res) => {
    const authCode = req.query.code;

    if (!authCode) {
        return res.send('No code found in the URL.');
    }

    try {
        // Exchange code for Access + Refresh Tokens
        const tokenInfo = await oauth.getTokensAuthorizationCodeGrant(authCode);
        
        console.log('--- SUCCESS ---');
        console.log('Access Token:', tokenInfo.accessToken);
        console.log('Refresh Token:', tokenInfo.refreshToken);

        res.send('Authenticated! You can close this tab and check your terminal.');
    } catch (err) {
        console.error('Token exchange failed:', err);
        res.status(500).send('Authentication failed.');
    }
});

app.listen(PORT, () => {
    console.log(`\n1. Go to http://localhost:${PORT}/login to start the flow`);
});
