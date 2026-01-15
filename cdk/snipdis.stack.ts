import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';

export interface SnipDisStackProps extends cdk.StackProps {
  instanceType: string;
  keyPairName: string;
  devGuildIds?: string;
  environment?: string;
}

export class SnipDisStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: SnipDisStackProps) {
    super(scope, id, props);

    // Reference pre-existing secret in AWS Secrets Manager (retained from previous stack)
    // To update secrets, use: aws secretsmanager put-secret-value --secret-id discord-bot/secrets --secret-string '{"bot_token":"...","sentry_dsn":"...","youtube_api_key":"...","proxyscrape_api_key":"..."}'
    const botSecrets = secretsmanager.Secret.fromSecretNameV2(
      this, 'BotSecrets', 'discord-bot/secrets'
    );

    // Non-secret configuration in SSM Parameter Store
    const devGuildIdsParam = new ssm.StringParameter(this, 'DevGuildIDsParameter', {
      parameterName: '/discord/dev_guild_ids',
      stringValue: props.devGuildIds || '',
    });

    const envParam = new ssm.StringParameter(this, 'EnvParameter', {
      parameterName: '/discord/env',
      stringValue: props.environment || 'PROD',
    });

    // IAM Role for EC2 Instance
    const botInstanceRole = new iam.Role(this, 'BotInstanceRole', {
      assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSSMManagedInstanceCore'),
      ],
    });


    // Add permissions for Secrets Manager
    botInstanceRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['secretsmanager:GetSecretValue'],
      resources: [botSecrets.secretArn],
    }));

    // Add permissions for SSM Parameters (non-secret config)
    botInstanceRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['ssm:GetParameter'],
      resources: [
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

    // Create new KeyPair per new CDK guidelines
    const keyPair = new ec2.KeyPair(this, 'KeyPair',
        {
          type: ec2.KeyPairType.ED25519,
          format: ec2.KeyPairFormat.PEM,
        });

    // EC2 Instance
    const botInstance = new ec2.Instance(this, 'BotInstance', {
      vpc: ec2.Vpc.fromLookup(this, 'DefaultVPC2', { isDefault: true }),
      instanceType: new ec2.InstanceType(props.instanceType),
      machineImage: ec2.MachineImage.latestAmazonLinux2023(),
      keyPair: keyPair,
      role: botInstanceRole,
      securityGroup: botSecurityGroup,
      userData: ec2.UserData.custom(`#!/bin/bash -xe
# Deployment timestamp: ${new Date().toISOString()}
dnf update -y
dnf install -y python3.11 python3.11-pip git

# Create bot directory
mkdir -p /opt/discord-bot
cd /opt/discord-bot

# Clone your repository
git clone https://github.com/CodeSpent/SnipDis.git .

# Create virtual environment and install dependencies
python3.11 -m venv /opt/discord-bot/venv
source /opt/discord-bot/venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install boto3 py-cord

# Create script to generate environment file from Secrets Manager and SSM
cat > /opt/discord-bot/generate_env.py << 'EOL'
#!/usr/bin/env python3
import boto3
import json
import sys
import time
import urllib.request

def get_instance_region():
    """Get region from EC2 instance metadata"""
    try:
        # Get token for IMDSv2
        req = urllib.request.Request(
            'http://169.254.169.254/latest/api/token',
            headers={'X-aws-ec2-metadata-token-ttl-seconds': '21600'},
            method='PUT'
        )
        with urllib.request.urlopen(req, timeout=2) as response:
            token = response.read().decode()

        # Get availability zone
        req = urllib.request.Request(
            'http://169.254.169.254/latest/meta-data/placement/availability-zone',
            headers={'X-aws-ec2-metadata-token': token}
        )
        with urllib.request.urlopen(req, timeout=2) as response:
            az = response.read().decode()

        # Remove the trailing letter to get region
        return az[:-1]
    except Exception as e:
        print(f"Failed to get region from metadata: {e}")
        return 'us-east-1'

def main():
    try:
        print("Generating environment file...")

        # Get region from instance metadata
        aws_region = get_instance_region()
        print(f"Using AWS region: {aws_region}")

        # Initialize clients with explicit region
        secrets_client = boto3.client('secretsmanager', region_name=aws_region)
        ssm = boto3.client('ssm', region_name=aws_region)

        # Get secrets from Secrets Manager
        max_retries = 3
        secrets = None
        for attempt in range(max_retries):
            try:
                print(f"Fetching secrets from Secrets Manager (attempt {attempt + 1}/{max_retries})...")
                response = secrets_client.get_secret_value(SecretId='discord-bot/secrets')
                secrets = json.loads(response['SecretString'])
                print("Successfully retrieved secrets")
                break
            except Exception as e:
                if attempt >= max_retries - 1:
                    print(f"Failed to get secrets after {max_retries} attempts: {str(e)}")
                    sys.exit(1)
                print(f"Error: {str(e)}. Retrying in 5 seconds...")
                time.sleep(5)

        # Function to get SSM parameter
        def get_ssm_param(param_name, default=""):
            try:
                response = ssm.get_parameter(Name=param_name)
                return response['Parameter']['Value']
            except Exception as e:
                print(f"Could not get {param_name}: {str(e)}, using default")
                return default

        # Get non-secret config from SSM
        dev_guild_ids = get_ssm_param('/discord/dev_guild_ids', '')
        env = get_ssm_param('/discord/env', 'PROD')

        # Write to .env file
        env_file_path = '/opt/discord-bot/.env'
        with open(env_file_path, 'w') as f:
            f.write(f"BOT_TOKEN={secrets.get('bot_token', '')}\\n")
            f.write(f"TOPGG_TOKEN={secrets.get('topgg_token', '')}\\n")
            f.write(f"TOPGG_BOT_ID=1334225517603192902\\n")
            f.write(f"AWS_REGION={aws_region}\\n")
            f.write(f"SENTRY_DSN={secrets.get('sentry_dsn', '')}\\n")
            f.write(f"YOUTUBE_API_KEY={secrets.get('youtube_api_key', '')}\\n")
            f.write(f"PROXYSCRAPE_API_KEY={secrets.get('proxyscrape_api_key', '')}\\n")
            f.write(f"GUILD_IDS={dev_guild_ids}\\n")
            f.write(f"ENV={env}\\n")

        print(f"Environment file generated successfully at {env_file_path}")

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOL

# Make the script executable and run it with venv
chmod +x /opt/discord-bot/generate_env.py
/opt/discord-bot/venv/bin/python3 /opt/discord-bot/generate_env.py

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
ExecStart=/opt/discord-bot/venv/bin/python3 /opt/discord-bot/main.py
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

    new cdk.CfnOutput(this, 'PublicIP', {
      description: 'Public IP of EC2 Instance',
      value: botInstance.instancePublicIp,
    });
  }
}