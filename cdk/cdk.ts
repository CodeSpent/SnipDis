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
// NOTE: Secrets are managed directly in AWS Secrets Manager, not through CDK
// To update: aws secretsmanager put-secret-value --secret-id discord-bot/secrets --secret-string '{"bot_token":"...","sentry_dsn":"...","youtube_api_key":"...","proxyscrape_api_key":"..."}'
const stackName = process.env.STACK_NAME || 'snipdis-bot';
const region = process.env.AWS_REGION || 'us-east-1';
const account = process.env.CDK_DEFAULT_ACCOUNT || process.env.AWS_ACCOUNT_ID;
const instanceType = process.env.INSTANCE_TYPE || 't3.micro';
const keyPairName = process.env.KEY_PAIR;
const devGuildIds = process.env.GUILD_IDS || '';
const env = process.env.ENV || 'PROD';

// Validate required parameters
if (!keyPairName) {
  console.error('Error: KEY_PAIR environment variable is required');
  process.exit(1);
}

// Create the stack with parameters
new SnipDisStack(app, stackName, {
  env: { account, region },
  instanceType,
  keyPairName,
  devGuildIds,
  environment: env,
});

app.synth();