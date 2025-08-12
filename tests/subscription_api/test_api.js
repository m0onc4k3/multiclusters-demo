import fetch from 'node-fetch';
import { strict as assert } from 'assert';
import { readFile } from 'fs/promises';
import { join } from 'path';
import dotenv from 'dotenv';

// Load .env from project root
dotenv.config({ path: join(process.cwd(), '.env') });

describe('API Tests', function () {
    this.timeout(5000); // Increase timeout to 5000ms

    let config;
    before(async () => {
        // Read config from tests/subscription_api/config.json
        try {
            const configPath = join(process.cwd(), 'tests', 'subscription_api', 'config.json');
            const configData = await readFile(configPath, 'utf-8');
            config = JSON.parse(configData);
            config.USERNAME = process.env.USERNAME;
            config.PASSWORD = process.env.PASSWORD;
            if (!config.USERNAME || !config.PASSWORD) {
                throw new Error('Missing USERNAME or PASSWORD in environment variables');
            }
        } catch (error) {
            throw new Error(`Failed to read config.json or environment variables: ${error.message}`);
        }
    });

    let accessToken;

    it('should login and get access_token', async function () {
        this.timeout(3000);
        const response = await fetch(config.LOGIN_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: config.USERNAME, password: config.PASSWORD })
        });
        assert.strictEqual(response.ok, true, 'Login failed');
        const cookies = response.headers.get('set-cookie');
        const tokenMatch = cookies.match(/access_token=([^;]+)/);
        assert(tokenMatch, 'No access_token found');
        accessToken = tokenMatch[1];
        console.log('Access token:', accessToken);
    });

    it('should submit address form', async function () {
        this.timeout(5000);
        const response = await fetch(config.API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Cookie': `access_token=${accessToken}`
            },
            body: JSON.stringify(config.FORM_DATA)
        });
        const result = await response.json();
        assert.strictEqual(response.status, 201, `Form submission failed: ${JSON.stringify(result)}`);
        assert(result._id, 'Response missing _id');
        assert(result.created_at, 'Response missing created_at');
        console.log('Address created:', result);
    });
});