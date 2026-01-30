#!/usr/bin/env python3
"""
Debug function extraction
"""
import requests
import json
import zipfile
import os
import tempfile

def create_simple_test_zip():
    """Create a simple test ZIP with just one Python file"""
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "debug_repo.zip")
    
    # Simple Python file
    test_file = {
        "test.py": '''
def create_user(username, email, age):
    """Creates a new user"""
    if age < 18:
        return None
    return {"username": username, "email": email, "age": age}

def validate_email(email):
    return "@" in email
'''
    }
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path, content in test_file.items():
            zipf.writestr(file_path, content)
    
    return zip_path

def debug_function_extraction():
    """Test function extraction specifically"""
    print("🔧 Debug Function Extraction")
    print("=" * 40)
    
    # Step 1: Upload a new project
    zip_path = create_simple_test_zip()
    
    try:
        print("📦 Step 1: Uploading test project...")
        with open(zip_path, 'rb') as f:
            files = {'file': ('debug_repo.zip', f, 'application/zip')}
            response = requests.post('http://localhost:8000/api/upload', files=files)
        
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.status_code}")
            return
            
        repo_id = response.json()['repo_id']
        print(f"✅ Upload successful! Repo ID: {repo_id}")
        
        # Step 2: Analyze
        print("🔍 Step 2: Analyzing...")
        response = requests.get(f'http://localhost:8000/api/analyze/{repo_id}')
        if response.status_code != 200:
            print(f"❌ Analysis failed: {response.status_code}")
            return
        print("✅ Analysis complete!")
        
        # Step 3: Get files
        print("📁 Step 3: Getting files...")
        response = requests.get(f'http://localhost:8000/api/files/{repo_id}')
        if response.status_code != 200:
            print(f"❌ Files request failed: {response.status_code}")
            print(response.text)
            return
        
        files_data = response.json()
        print("✅ Files retrieved!")
        print("📁 Available files:")
        for file_info in files_data['files']:
            print(f"  {file_info['filePath']}: {file_info['functions']}")
        
        # Step 4: Test function details
        test_file = "test.py"
        test_function = "create_user"
        
        print(f"\n🔍 Step 4: Testing function '{test_function}' in '{test_file}'")
        
        params = {
            'file_path': test_file,
            'function_name': test_function
        }
        
        response = requests.get(f'http://localhost:8000/api/function/{repo_id}', params=params)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print("\nFunction details:")
            details = result['details']
            print(f"Name: {details['function_name']}")
            print(f"Inputs: {details['inputs']}")
            print(f"Outputs: {details['outputs']}")
            print(f"Description: {details['description']}")
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        os.remove(zip_path)

if __name__ == "__main__":
    debug_function_extraction()