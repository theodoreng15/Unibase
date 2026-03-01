const express = require('express');
const { BoxOAuth, OAuthConfig } = require('box-node-sdk/box');
const proc = require('node:process');
const fs = require('fs');
const path = require('path');

// 1. Setup Configuration
const env_path = "../../../.env";
proc.loadEnvFile(env_path);
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
        redirectUri: 'http://localhost:3000/callback'
    });
    res.redirect(authorizeUrl);
});

function updateEnvValue(key, value) {
    let envContent = fs.readFileSync(env_path, 'utf8');
    const regex = new RegExp(`^${key}=.*`, 'm');
    if (envContent.match(regex)) {
        envContent = envContent.replace(regex, `${key}=${value}`);
    } else {
        envContent += `\n${key}=${value}`;
    }
    fs.writeFileSync(env_path, envContent);
    console.log(`Updated ${key} in .env file.`);
}

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

        res.send(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Authenticated</title>
                <style>
                    body { font-family: sans-serif; padding: 20px; line-height: 1.6; }
                    .token-container { 
                        background: #f4f4f4; 
                        padding: 15px; 
                        border-radius: 8px; 
                        margin-bottom: 10px; 
                        display: flex; 
                        justify-content: space-between;
                        align-items: center;
                        border: 1px solid #ddd;
                    }
                    code { font-family: monospace; word-break: break-all; margin-right: 10px; color: #333; }
                    button { 
                        background: #007bff; 
                        color: white; 
                        border: none; 
                        padding: 8px 12px; 
                        border-radius: 4px; 
                        cursor: pointer; 
                        white-space: nowrap;
                    }
                    button:hover { background: #0056b3; }
                    h2 { color: #28a745; }
                </style>
            </head>
            <body>
                <h2>Authenticated!</h2>
                
                <p><strong>Access Token:</strong></p>
                <div class="token-container">
                    <code id="access">${tokenInfo.accessToken}</code>
                    <button onclick="copyToClipboard('access')">Copy</button>
                </div>

                <p><strong>Refresh Token:</strong></p>
                <div class="token-container">
                    <code id="refresh">${tokenInfo.refreshToken}</code>
                    <button onclick="copyToClipboard('refresh')">Copy</button>
                </div>

                <script>
                    function copyToClipboard(id) {
                        const text = document.getElementById(id).innerText;
                        navigator.clipboard.writeText(text).then(() => {
                            // alert('Copied to clipboard!');
                        }).catch(err => {
                            console.error('Failed to copy: ', err);
                        });
                    }
                </script>
            </body>
            </html>
        `);
        
        updateEnvValue("BOX_ACCESS_TOKEN", tokenInfo.accessToken);
        updateEnvValue("BOX_REFRESH_TOKEN", tokenInfo.refreshToken);
    } catch (err) {
        console.error('Token exchange failed:', err);
        res.status(500).send('Authentication failed.');
    }
});

app.listen(PORT, () => {
    console.log(`\n1. Go to http://localhost:${PORT}/login to start the flow`);
});
