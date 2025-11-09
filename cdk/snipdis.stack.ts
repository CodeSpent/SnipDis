import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as ssm from 'aws-cdk-lib/aws-ssm';

export interface SnipDisStackProps extends cdk.StackProps {
  instanceType: string;
  keyPairName: string;
  botToken: string;
  topggToken: string;
  sentryDsn?: string;
  youtubeApiKey?: string;
  proxyscrapeApiKey?: string;
  devGuildIds?: string;
  environment?: string;
}

export class SnipDisStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: SnipDisStackProps) {
    super(scope, id, props);

    // DynamoDB Table for Vote Reminders
    const voteRemindersTable = new dynamodb.Table(this, 'VoteRemindersTable', {
      tableName: 'vote-reminders',
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      partitionKey: { name: 'user_id', type: dynamodb.AttributeType.NUMBER },
      sortKey: { name: 'bot_id', type: dynamodb.AttributeType.NUMBER },
      timeToLiveAttribute: 'expire_time',
    });

    // SSM Parameters for storing configuration securely
    const botTokenParam = new ssm.StringParameter(this, 'BotTokenParameter', {
      parameterName: '/discord/bot_token',
      stringValue: props.botToken,
      type: ssm.ParameterType.SECURE_STRING,
    });

    const topggTokenParam = new ssm.StringParameter(this, 'TopGGTokenParameter', {
      parameterName: '/discord/topgg_token',
      stringValue: props.topggToken,
      type: ssm.ParameterType.SECURE_STRING,
    });

    const sentryDsnParam = new ssm.StringParameter(this, 'SentryDSNParameter', {
      parameterName: '/discord/sentry_dsn',
      stringValue: props.sentryDsn || '',
      type: ssm.ParameterType.SECURE_STRING,
    });

    const youtubeApiKeyParam = new ssm.StringParameter(this, 'YouTubeAPIKeyParameter', {
      parameterName: '/discord/youtube_api_key',
      stringValue: props.youtubeApiKey || '',
      type: ssm.ParameterType.SECURE_STRING,
    });

    const proxyscrapeApiKeyParam = new ssm.StringParameter(this, 'ProxyScrapeAPIKeyParameter', {
      parameterName: '/discord/proxyscrape_api_key',
      stringValue: props.proxyscrapeApiKey || '',
      type: ssm.ParameterType.SECURE_STRING,
    });

    const devGuildIdsParam = new ssm.StringParameter(this, 'DevGuildIDsParameter', {
      parameterName: '/discord/dev_guild_ids',
      stringValue: props.devGuildIds || '',
      type: ssm.ParameterType.STRING,
    });

    const envParam = new ssm.StringParameter(this, 'EnvParameter', {
      parameterName: '/discord/env',
      stringValue: props.environment || 'PROD',
      type: ssm.ParameterType.STRING,
    });

    // IAM Role for EC2 Instance
    const botInstanceRole = new iam.Role(this, 'BotInstanceRole', {
      assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSSMManagedInstanceCore'),
      ],
    });

    // Add permissions for DynamoDB
    botInstanceRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'dynamodb:PutItem',
        'dynamodb:GetItem',
        'dynamodb:DeleteItem',
        'dynamodb:Query',
        'dynamodb:Scan',
      ],
      resources: [voteRemindersTable.tableArn],
    }));

    // Add permissions for SSM Parameters
    botInstanceRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['ssm:GetParameter'],
      resources: [
        botTokenParam.parameterArn,
        topggTokenParam.parameterArn,
        sentryDsnParam.parameterArn,
        youtubeApiKeyParam.parameterArn,
        proxyscrapeApiKeyParam.parameterArn,
        devGuildIdsParam.parameterArn,
        envParam.parameterArn,
      ],
    }));

    // Security Group for EC2 Instance
    const botSecurityGroup = new ec2.SecurityGroup(this, 'BotSecurityGroup', {
      vpc: ec2.Vpc.fromLookup(this, 'DefaultVPC', { isDefault: true }),
      description: 'Security group for Discord bot EC2 instance',
      allowAllOutbound: true,
    });

    botSecurityGroup.addIngressRule(
      ec2.Peer.anyIpv4(),
      ec2.Port.tcp(22),
      'Allow SSH access'
    );

    // EC2 Instance
    const botInstance = new ec2.Instance(this, 'BotInstance', {
      vpc: ec2.Vpc.fromLookup(this, 'DefaultVPC2', { isDefault: true }),
      instanceType: new ec2.InstanceType(props.instanceType),
      machineImage: ec2.MachineImage.latestAmazonLinux2(),
      keyName: props.keyPairName,
      role: botInstanceRole,
      securityGroup: botSecurityGroup,
      userData: ec2.UserData.custom(`#!/bin/bash -xe
yum update -y
yum install -y python3-pip git
pip3 install pipenv

# Create bot directory
mkdir -p /opt/discord-bot
cd /opt/discord-bot

# Clone your repository
git clone https://github.com/codespent/discord-web-clipper.git .

# Setup Python environment
pip3 install -r requirements.txt

# Update requirements.txt to include all necessary dependencies
cat > /opt/discord-bot/requirements.txt << 'EOL'
aiohttp==3.11.16
asyncio==3.4.3
beautifulsoup4==4.13.3
boto3==1.34.0
py-cord>=2.0.0
python-dotenv==1.1.0
requests==2.32.3
sentry-sdk~=2.25.1
newspaper4k>=0.1.0
dblpy>=0.4.0
EOL

# Create script to generate environment file from SSM parameters
# This script fetches the bot token and Top.gg token from SSM Parameter Store
# and writes them to a .env file for the bot to use
cat > /opt/discord-bot/generate_env.py << 'EOL'
#!/usr/bin/env python3
import boto3
import os
import sys
import time

def main():
    try:
        print("Generating environment file...")

        # Initialize SSM client
        ssm = boto3.client('ssm')

        # Function to get parameter with retry logic
        def get_parameter_with_retry(param_name, required=True):
            max_retries = 3
            retry_count = 0
            param_value = None

            while retry_count < max_retries:
                try:
                    print(f"Attempting to get {param_name} (attempt {retry_count + 1}/{max_retries})...")
                    param_response = ssm.get_parameter(Name=param_name, WithDecryption=True)
                    param_value = param_response['Parameter']['Value']
                    print(f"Successfully retrieved {param_name}")
                    break
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        if required:
                            print(f"Failed to get {param_name} after {max_retries} attempts: {str(e)}")
                            sys.exit(1)
                        else:
                            print(f"Failed to get optional parameter {param_name}: {str(e)}")
                            return ""
                    print(f"Error getting {param_name}: {str(e)}. Retrying in 5 seconds...")
                    time.sleep(5)

            return param_value

        # Get required parameters
        bot_token = get_parameter_with_retry('/discord/bot_token', required=True)
        topgg_token = get_parameter_with_retry('/discord/topgg_token', required=True)

        # Get optional parameters
        sentry_dsn = get_parameter_with_retry('/discord/sentry_dsn', required=False)
        youtube_api_key = get_parameter_with_retry('/discord/youtube_api_key', required=False)
        proxyscrape_api_key = get_parameter_with_retry('/discord/proxyscrape_api_key', required=False)
        dev_guild_ids = get_parameter_with_retry('/discord/dev_guild_ids', required=False)
        env = get_parameter_with_retry('/discord/env', required=False) or "PROD"

        # Get AWS region
        aws_region = boto3.session.Session().region_name
        print(f"Using AWS region: {aws_region}")

        # Write to .env file
        env_file_path = '/opt/discord-bot/.env'
        try:
            with open(env_file_path, 'w') as f:
                # Required parameters
                f.write(f'BOT_TOKEN={bot_token}\\n')
                f.write(f'TOPGG_TOKEN={topgg_token}\\n')
                f.write(f'TOPGG_BOT_ID=1334225517603192902\\n')
                f.write(f'AWS_REGION={aws_region}\\n')

                # Optional parameters
                f.write(f'SENTRY_DSN={sentry_dsn}\\n')
                f.write(f'YOUTUBE_API_KEY={youtube_api_key}\\n')
                f.write(f'PROXYSCRAPE_API_KEY={proxyscrape_api_key}\\n')
                f.write(f'GUILD_IDS={dev_guild_ids}\\n')
                f.write(f'ENV={env}\\n')

            print(f"Environment file generated successfully at {env_file_path}")
        except Exception as e:
            print(f"Error writing environment file: {str(e)}")
            sys.exit(1)

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOL

# Make the script executable and run it
chmod +x /opt/discord-bot/generate_env.py
python3 /opt/discord-bot/generate_env.py

# Check if the script ran successfully
if [ $? -ne 0 ]; then
  echo "Failed to generate environment file. Check the logs for details."
  exit 1
fi

# Create systemd service
cat > /etc/systemd/system/discord-bot.service << 'EOL'
[Unit]
Description=Discord Bot Service
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/discord-bot
ExecStart=/usr/bin/python3 /opt/discord-bot/main.py
Restart=always
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOL

# Set permissions
chown -R ec2-user:ec2-user /opt/discord-bot

# Enable the service to start on boot
systemctl enable discord-bot

# Start the service
echo "Starting the Discord bot service..."
systemctl start discord-bot

# Check if the service started successfully
sleep 5
if systemctl is-active --quiet discord-bot; then
  echo "Discord bot service started successfully"
else
  echo "Failed to start Discord bot service. Check the logs with: journalctl -u discord-bot"
  # Don't exit with error as the instance might still be useful for debugging
  # exit 1
fi`),
    });

    // Outputs
    new cdk.CfnOutput(this, 'InstanceId', {
      description: 'EC2 Instance ID',
      value: botInstance.instanceId,
    });

    new cdk.CfnOutput(this, 'DynamoDBTableName', {
      description: 'Name of created DynamoDB table',
      value: voteRemindersTable.tableName,
    });

    new cdk.CfnOutput(this, 'PublicIP', {
      description: 'Public IP of EC2 Instance',
      value: botInstance.instancePublicIp,
    });
  }
}