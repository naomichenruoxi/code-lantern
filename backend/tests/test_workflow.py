#!/usr/bin/env python3
"""
Test script to test the full workflow: upload + analyze
"""
import requests
import zipfile
import os
import tempfile
import json

def create_test_zip():
    """Create a test ZIP file with some sample code files"""
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "test_repo.zip")
    
    # Create some test files with actual functions
    test_files = {
        "src/main.py": '''
def hello_world():
    print("Hello World")
    greet_user("Alice")

def greet_user(name):
    message = format_greeting(name)
    print(message)

def format_greeting(name):
    return f"Hello, {name}!"
''',
        "src/utils.js": '''
function calculateSum(a, b) {
    return a + b;
}

const multiply = (x, y) => {
    return x * y;
}

function processData(data) {
    const result = calculateSum(data.a, data.b);
    return multiply(result, 2);
}
''',
        "README.md": "# Test Repository\n\nThis is a test repo.\n",
        "package.json": '{"name": "test-repo", "version": "1.0.0"}\n'
    }
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path, content in test_files.items():
            zipf.writestr(file_path, content)
    
    return zip_path

def test_full_workflow():
    """Test upload + analysis workflow"""
    print("🚀 Testing full workflow...")
    
    # Step 1: Upload
    zip_path = create_test_zip()
    
    try:
        print("📦 Uploading ZIP file...")
        with open(zip_path, 'rb') as f:
            files = {'file': ('test_repo.zip', f, 'application/zip')}
            response = requests.post('http://localhost:8000/api/upload', files=files)
        
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.status_code}")
            print(response.text)
            return
            
        upload_result = response.json()
        repo_id = upload_result['repo_id']
        print(f"✅ Upload successful! Repo ID: {repo_id}")
        
        # Step 2: Analyze
        print("🔍 Analyzing project structure...")
        response = requests.get(f'http://localhost:8000/api/analyze/{repo_id}')
        
        if response.status_code != 200:
            print(f"❌ Analysis failed: {response.status_code}")
            print(response.text)
            return
            
        analysis_result = response.json()
        print(f"✅ Analysis complete! Files analyzed: {analysis_result['files_analyzed']}")
        
        # Pretty print the architecture map
        print("\n🏗️  Architecture Map:")
        print(json.dumps(analysis_result['architecture_map'], indent=2))
        
        return analysis_result
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed!")
        print("🚨 Make sure the server is running first:")
        print("   python main.py")
        return None
    finally:
        # Cleanup test file
        os.remove(zip_path)

if __name__ == "__main__":
    test_full_workflow()