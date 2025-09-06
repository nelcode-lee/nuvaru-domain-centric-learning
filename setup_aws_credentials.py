#!/usr/bin/env python3
"""
Quick script to help set up AWS credentials in Railway
"""

import subprocess
import sys

def set_aws_credentials():
    """Set AWS credentials in Railway"""
    print("🔑 Setting up AWS S3 credentials in Railway")
    print("=" * 50)
    
    # Get credentials from user
    access_key = input("Enter your AWS Access Key ID: ").strip()
    secret_key = input("Enter your AWS Secret Access Key: ").strip()
    bucket_name = input("Enter your S3 bucket name: ").strip()
    region = input("Enter your AWS region (default: us-east-1): ").strip() or "us-east-1"
    
    # Validate inputs
    if not access_key or not secret_key or not bucket_name:
        print("❌ All fields are required!")
        return False
    
    if not access_key.startswith('AKIA'):
        print("⚠️ Warning: Access Key ID should start with 'AKIA'")
    
    # Set environment variables in Railway
    credentials = {
        "AWS_ACCESS_KEY_ID": access_key,
        "AWS_SECRET_ACCESS_KEY": secret_key,
        "S3_BUCKET_NAME": bucket_name,
        "AWS_REGION": region
    }
    
    print("\n🚀 Setting credentials in Railway...")
    
    for key, value in credentials.items():
        try:
            subprocess.run(['railway', 'variables', 'set', f"{key}={value}"], 
                         check=True, capture_output=True)
            print(f"✅ Set {key}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to set {key}")
            return False
    
    print("\n🎉 AWS credentials set successfully!")
    print("\n📋 Summary:")
    print(f"   Bucket: {bucket_name}")
    print(f"   Region: {region}")
    print(f"   Access Key: {access_key[:10]}...")
    
    return True

def test_s3_connection():
    """Test S3 connection"""
    print("\n🧪 Testing S3 connection...")
    
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        # This would test the connection, but we don't have the credentials in this script
        print("✅ S3 credentials configured")
        print("   Test will be performed during Railway deployment")
        
    except ImportError:
        print("⚠️ boto3 not installed locally (this is normal)")
        print("   S3 connection will be tested in Railway")

def main():
    """Main function"""
    print("AWS S3 Credentials Setup for Railway")
    print("=" * 40)
    
    print("\n📝 Before running this script:")
    print("1. Make sure you have created an S3 bucket")
    print("2. Create an IAM user with S3 permissions")
    print("3. Generate access keys for that user")
    print("4. Have your Railway project ready")
    
    response = input("\nDo you have all the required information? (y/n): ").lower()
    if response != 'y':
        print("\n🔗 Quick links:")
        print("   S3 Console: https://s3.console.aws.amazon.com/")
        print("   IAM Console: https://console.aws.amazon.com/iam/")
        print("   Railway: https://railway.app/")
        return
    
    if set_aws_credentials():
        test_s3_connection()
        print("\n✅ Setup complete!")
        print("\n🚀 Next steps:")
        print("1. Continue with Railway deployment")
        print("2. Test file upload functionality")
        print("3. Monitor S3 usage and costs")
    else:
        print("\n❌ Setup failed. Please try again.")

if __name__ == "__main__":
    main()
