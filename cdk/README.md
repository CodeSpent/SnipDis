# SnipDis CDK Deployment

This directory contains the AWS CDK (Cloud Development Kit) implementation for deploying the SnipDis Discord bot infrastructure.

## Overview

The CDK implementation provides a TypeScript-based approach to defining and deploying the AWS infrastructure required for the SnipDis Discord bot. This approach offers several advantages over the CloudFormation template approach:

- **Type Safety**: TypeScript provides type checking, making it easier to catch errors before deployment.
- **Modularity**: The infrastructure is defined in a more modular and maintainable way.
- **Reusability**: Components can be easily reused and composed.
- **Better Developer Experience**: Modern IDE features like auto-completion and inline documentation.

## Files

- `cdk.ts`: The entry point for the CDK application. It loads environment variables and creates the stack.
- `snipdis.stack.ts`: Defines the AWS resources that make up the SnipDis infrastructure.
- `deploy.sh`: A helper script to simplify the deployment process.
- `package.json`: Defines the Node.js dependencies for the CDK project.
- `tsconfig.json`: TypeScript configuration for the project.

## Prerequisites

- Node.js (v14 or later)
- npm (v6 or later)
- AWS CLI configured with appropriate credentials
- AWS CDK installed globally (optional, as it's included in the project dependencies)

## Deployment

1. Ensure you have a `.env` file in the project root with the required parameters:
   ```
   BOT_TOKEN=your-discord-bot-token
   TOPGG_TOKEN=your-topgg-api-token
   KEY_PAIR=your-key-pair-name
   ```

2. Run the deployment script:
   ```bash
   ./deploy.sh
   ```

   This script will:
   - Check for required dependencies
   - Validate your .env file
   - Install npm dependencies
   - Build the TypeScript code
   - Deploy the CDK stack

## Manual Deployment

If you prefer to run the commands manually:

1. Install dependencies:
   ```bash
   npm install
   ```

2. Build the TypeScript code:
   ```bash
   npm run build
   ```

3. Deploy the stack:
   ```bash
   npm run deploy
   ```

## Customization

You can customize the deployment by adding or modifying environment variables in the `.env` file:

```
# Required parameters
BOT_TOKEN=your-discord-bot-token
TOPGG_TOKEN=your-topgg-api-token
KEY_PAIR=your-key-pair-name

# Optional parameters
STACK_NAME=snipdis-bot
AWS_REGION=us-east-1
INSTANCE_TYPE=t3.micro
SENTRY_DSN=your-sentry-dsn
YOUTUBE_API_KEY=your-youtube-api-key
PROXYSCRAPE_API_KEY=your-proxyscrape-api-key
GUILD_IDS=123456789,987654321
ENV=PROD
```

## Troubleshooting

- If you encounter errors during deployment, check the CDK output for detailed error messages.
- Ensure your AWS credentials are properly configured and have the necessary permissions.
- If you need to destroy the stack, you can run:
  ```bash
  npm run cdk destroy
  ```