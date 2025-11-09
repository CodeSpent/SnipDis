#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { SnipDisStack } from './snipdis.stack';
import * as dotenv from 'dotenv';
import * as path from 'path';

// Load environment variables from .env file in the project root
dotenv.config({ path: path.resolve(__dirname, '../.env') });

const app = new cdk.App();

// Get parameters from environment variables or use defaults
const stackName = process.env.STACK_NAME || 'snipdis-bot';
const region = process.env.AWS_REGION || 'us-east-1';
const instanceType = process.env.INSTANCE_TYPE || 't3.micro';
const keyPairName = process.env.KEY_PAIR;
const botToken = process.env.BOT_TOKEN;
const topggToken = process.env.TOPGG_TOKEN;
const sentryDsn = process.env.SENTRY_DSN || '';
const youtubeApiKey = process.env.YOUTUBE_API_KEY || '';
const proxyscrapeApiKey = process.env.PROXYSCRAPE_API_KEY || '';
const devGuildIds = process.env.GUILD_IDS || '';
const env = process.env.ENV || 'PROD';

// Validate required parameters
if (!keyPairName) {
  console.error('Error: KEY_PAIR environment variable is required');
  process.exit(1);
}

if (!botToken) {
  console.error('Error: BOT_TOKEN environment variable is required');
  process.exit(1);
}

if (!topggToken) {
  console.error('Error: TOPGG_TOKEN environment variable is required');
  process.exit(1);
}

// Create the stack with parameters
new SnipDisStack(app, stackName, {
  env: { region },
  instanceType,
  keyPairName,
  botToken,
  topggToken,
  sentryDsn,
  youtubeApiKey,
  proxyscrapeApiKey,
  devGuildIds,
  environment: env,
});

app.synth();