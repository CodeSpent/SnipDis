#!/bin/bash

# Script to deploy the SnipDis Discord Bot using AWS CDK

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install it first."
    echo "Visit https://nodejs.org/ for installation instructions."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "npm is not installed. Please install it first."
    echo "It usually comes with Node.js installation."
    exit 1
fi

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "AWS CLI is not installed. Please install it first."
    echo "Visit https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html for installation instructions."
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "AWS credentials are not configured. Please configure them first."
    echo "Run 'aws configure' to set up your AWS credentials."
    exit 1
fi

# Check if .env file exists in the project root
if [ ! -f "../.env" ]; then
    echo "Error: .env file not found in the project root."
    echo "Please create a .env file with the required parameters."
    exit 1
fi

# Check if KEY_PAIR is set in .env
if ! grep -q "KEY_PAIR" "../.env"; then
    echo "Error: KEY_PAIR is not set in the .env file."
    echo "Please add KEY_PAIR=your_key_pair_name to your .env file."
    exit 1
fi

# Check if BOT_TOKEN is set in .env
if ! grep -q "BOT_TOKEN" "../.env"; then
    echo "Error: BOT_TOKEN is not set in the .env file."
    echo "Please add BOT_TOKEN=your_discord_bot_token to your .env file."
    exit 1
fi

# Check if TOPGG_TOKEN is set in .env
if ! grep -q "TOPGG_TOKEN" "../.env"; then
    echo "Error: TOPGG_TOKEN is not set in the .env file."
    echo "Please add TOPGG_TOKEN=your_topgg_token to your .env file."
    exit 1
fi

echo "Installing dependencies..."
npm install

echo "Building TypeScript code..."
npm run build

echo "Deploying SnipDis Discord Bot infrastructure..."
npm run deploy -- --require-approval never

if [ $? -eq 0 ]; then
    echo "Deployment successful!"
else
    echo "Deployment failed."
    exit 1
fi