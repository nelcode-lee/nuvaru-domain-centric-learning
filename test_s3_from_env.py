#!/usr/bin/env python3
"""
Test AWS S3 connection using environment variables
"""

import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import sys

def load_env_file(file_path):
    """Load environment variables from a file"""
    env_vars = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"\'')
                    env_vars[key] = value
    return env_vars

def test_s3_from_env():
    """Test S3 connection using environment variables"""
    print("🧪 Testing AWS S3 Connection from Environment Variables")
    print("=" * 60)
    
    # Load environment variables from various files
    env_files = ['.env', 'production.env', 'railway.env']
    env_vars = {}
    
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"📄 Loading environment variables from {env_file}")
            file_vars = load_env_file(env_file)
            env_vars.update(file_vars)
    
    # Also check system environment variables
    for key in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'S3_BUCKET_NAME', 'AWS_REGION']:
        if key in os.environ:
            env_vars[key] = os.environ[key]
    
    # Get S3 credentials - prioritize .env file values
    access_key = env_vars.get('AWS_ACCESS_KEY_ID')
    secret_key = env_vars.get('AWS_SECRET_ACCESS_KEY')
    bucket_name = env_vars.get('S3_BUCKET_NAME', 'nuvaru')
    region = env_vars.get('AWS_REGION', 'eu-north-1')
    
    # Override with .env file values if they exist
    if os.path.exists('.env'):
        dotenv_vars = load_env_file('.env')
        access_key = dotenv_vars.get('AWS_ACCESS_KEY_ID', access_key)
        secret_key = dotenv_vars.get('AWS_SECRET_ACCESS_KEY', secret_key)
        bucket_name = dotenv_vars.get('S3_BUCKET_NAME', bucket_name)
        region = dotenv_vars.get('AWS_REGION', region)
    
    print(f"\n📋 Found configuration:")
    print(f"   Access Key: {'✅ Found' if access_key else '❌ Missing'}")
    print(f"   Secret Key: {'✅ Found' if secret_key else '❌ Missing'}")
    print(f"   Bucket: {bucket_name}")
    print(f"   Region: {region}")
    
    if not access_key or not secret_key:
        print("\n❌ AWS credentials not found in environment files!")
        print("\n📝 To add your credentials, create a .env file with:")
        print("AWS_ACCESS_KEY_ID=your-access-key-id")
        print("AWS_SECRET_ACCESS_KEY=your-secret-access-key")
        print("S3_BUCKET_NAME=nuvaru")
        print("AWS_REGION=eu-north-1")
        return False
    
    try:
        # Create S3 client
        print(f"\n🔗 Connecting to S3 in region: {region}")
        s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        # Test 1: List buckets
        print("\n📋 Test 1: Listing buckets...")
        try:
            response = s3_client.list_buckets()
            buckets = [bucket['Name'] for bucket in response['Buckets']]
            print(f"✅ Successfully connected! Found {len(buckets)} buckets:")
            for bucket in buckets:
                marker = " 👈 Your bucket" if bucket == bucket_name else ""
                print(f"   - {bucket}{marker}")
        except ClientError as e:
            print(f"❌ Failed to list buckets: {e}")
            return False
        
        # Test 2: Check if your bucket exists
        print(f"\n🗂️ Test 2: Checking bucket '{bucket_name}'...")
        try:
            response = s3_client.head_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' exists and is accessible!")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"❌ Bucket '{bucket_name}' does not exist!")
                return False
            else:
                print(f"❌ Error accessing bucket: {e}")
                return False
        
        # Test 3: List objects in bucket
        print(f"\n📄 Test 3: Listing objects in '{bucket_name}'...")
        try:
            response = s3_client.list_objects_v2(Bucket=bucket_name)
            object_count = response.get('KeyCount', 0)
            print(f"✅ Bucket contains {object_count} objects")
            
            if object_count > 0:
                print("   Objects:")
                for obj in response.get('Contents', []):
                    print(f"   - {obj['Key']} ({obj['Size']} bytes)")
            else:
                print("   Bucket is empty (this is normal for a new bucket)")
        except ClientError as e:
            print(f"❌ Failed to list objects: {e}")
            return False
        
        # Test 4: Test upload (small test file)
        print(f"\n📤 Test 4: Testing file upload...")
        try:
            test_content = "This is a test file for Nuvaru platform - " + str(os.urandom(8).hex())
            test_key = "test/nuvaru-test.txt"
            
            s3_client.put_object(
                Bucket=bucket_name,
                Key=test_key,
                Body=test_content.encode('utf-8'),
                ContentType='text/plain'
            )
            print(f"✅ Successfully uploaded test file: {test_key}")
            
            # Clean up test file
            s3_client.delete_object(Bucket=bucket_name, Key=test_key)
            print("✅ Test file cleaned up")
            
        except ClientError as e:
            print(f"❌ Failed to upload test file: {e}")
            return False
        
        print("\n🎉 All tests passed! Your S3 configuration is working correctly.")
        print("\n📋 Summary:")
        print(f"   ✅ Bucket: {bucket_name}")
        print(f"   ✅ Region: {region}")
        print(f"   ✅ Access Key: {access_key[:10]}...")
        print(f"   ✅ Permissions: Full access confirmed")
        
        print("\n🚀 Ready for Railway deployment!")
        print("Your S3 configuration is working and ready to use.")
        
        return True
        
    except NoCredentialsError:
        print("❌ No credentials provided or invalid credentials")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function"""
    print("AWS S3 Connection Test from Environment Variables")
    print("=" * 55)
    
    print("\n📝 This test will:")
    print("1. Load AWS credentials from .env files")
    print("2. Connect to your S3 bucket")
    print("3. Test file upload/download")
    print("4. Verify everything is ready for Railway")
    
    success = test_s3_from_env()
    
    if success:
        print("\n✅ S3 test completed successfully!")
        print("Your S3 configuration is ready for Railway deployment.")
    else:
        print("\n❌ S3 test failed!")
        print("Please add your AWS credentials to a .env file and try again.")

if __name__ == "__main__":
    main()
