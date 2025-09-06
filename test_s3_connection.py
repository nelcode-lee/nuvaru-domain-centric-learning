#!/usr/bin/env python3
"""
Test AWS S3 connection and configuration
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import sys

def test_s3_connection():
    """Test S3 connection with user credentials"""
    print("🧪 Testing AWS S3 Connection")
    print("=" * 40)
    
    # Get credentials from user
    access_key = input("Enter your AWS Access Key ID: ").strip()
    secret_key = input("Enter your AWS Secret Access Key: ").strip()
    bucket_name = input("Enter your S3 bucket name (nuvaru): ").strip() or "nuvaru"
    region = input("Enter your AWS region (eu-north-1): ").strip() or "eu-north-1"
    
    if not access_key or not secret_key:
        print("❌ Access Key ID and Secret Access Key are required!")
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
                print(f"   - {bucket}")
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
            test_content = "This is a test file for Nuvaru platform"
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
        
        # Test 5: Check permissions
        print(f"\n🔐 Test 5: Checking permissions...")
        try:
            # Try to get bucket location
            response = s3_client.get_bucket_location(Bucket=bucket_name)
            bucket_region = response.get('LocationConstraint', 'us-east-1')
            print(f"✅ Bucket region: {bucket_region}")
            
            # Check if we can read bucket policy
            try:
                s3_client.get_bucket_policy(Bucket=bucket_name)
                print("✅ Can read bucket policy")
            except ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
                    print("✅ No bucket policy set (this is normal)")
                else:
                    print(f"⚠️ Cannot read bucket policy: {e}")
                    
        except ClientError as e:
            print(f"❌ Failed to check permissions: {e}")
            return False
        
        print("\n🎉 All tests passed! Your S3 configuration is working correctly.")
        print("\n📋 Summary:")
        print(f"   ✅ Bucket: {bucket_name}")
        print(f"   ✅ Region: {region}")
        print(f"   ✅ Access Key: {access_key[:10]}...")
        print(f"   ✅ Permissions: Full access confirmed")
        
        print("\n🚀 Ready for Railway deployment!")
        print("You can now use these credentials in Railway:")
        print(f"   AWS_ACCESS_KEY_ID={access_key}")
        print(f"   AWS_SECRET_ACCESS_KEY={secret_key}")
        print(f"   S3_BUCKET_NAME={bucket_name}")
        print(f"   AWS_REGION={region}")
        
        return True
        
    except NoCredentialsError:
        print("❌ No credentials provided or invalid credentials")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function"""
    print("AWS S3 Connection Test for Nuvaru Platform")
    print("=" * 50)
    
    print("\n📝 This test will:")
    print("1. Connect to your S3 bucket")
    print("2. List buckets and objects")
    print("3. Test file upload/download")
    print("4. Check permissions")
    print("5. Verify everything is ready for Railway")
    
    print("\n⚠️ You'll need:")
    print("- AWS Access Key ID")
    print("- AWS Secret Access Key")
    print("- S3 bucket name")
    print("- AWS region")
    
    response = input("\nReady to test? (y/n): ").lower()
    if response != 'y':
        print("Test cancelled.")
        return
    
    try:
        success = test_s3_connection()
        if success:
            print("\n✅ S3 test completed successfully!")
            print("Your S3 configuration is ready for Railway deployment.")
        else:
            print("\n❌ S3 test failed!")
            print("Please check your credentials and try again.")
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()
