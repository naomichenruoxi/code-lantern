#!/usr/bin/env python3
"""
Test script to upload a zip file to the backend
"""
import requests
import zipfile
import os
import tempfile

def create_test_zip():
    """Create a test ZIP file with some sample code files"""
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "test_repo.zip")
    
    # Create some test files
    test_files = {
        "src/main.py": "print('Hello World')\n",
        "src/utils.js": "function hello() { return 'Hello'; }\n",
        "README.md": "# Test Repository\n\nThis is a test repo.\n",
        "package.json": '{"name": "test-repo", "version": "1.0.0"}\n'
    }
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path, content in test_files.items():
            zipf.writestr(file_path, content)
    
    return zip_path

def test_upload():
    """Test the upload endpoint"""
    # Create test ZIP
    zip_path = create_test_zip()
    
    try:
        # Upload to server
        with open(zip_path, 'rb') as f:
            files = {'file': ('test_repo.zip', f, 'application/zip')}
            response = requests.post('http://localhost:8000/api/upload', files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful!")
            print(f"Repo ID: {result['repo_id']}")
            print(f"Extracted to: {result['extracted_to']}")
            return result['repo_id']
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(response.text)
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed!")
        print("🚨 Make sure the server is running first:")
        print("   Terminal 1: python main.py")
        print("   Terminal 2: python test_upload.py")
        return None
    finally:
        # Cleanup test file
        os.remove(zip_path)

if __name__ == "__main__":
    print("🚀 Testing upload endpoint...")
    test_upload()