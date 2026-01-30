#!/usr/bin/env python3
"""
Test project-relative paths in architecture JSON
"""
import requests
import json
import zipfile
import os
import tempfile

def create_path_test_project():
    """Create a test project to verify path formats"""
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "path_test.zip")
    
    test_files = {
        "app.py": '''def main():
    """Main entry point"""
    config = load_config()
    start_app(config)

def load_config():
    """Load configuration"""
    return {"port": 8000}
''',
        "src/utils.py": '''def helper_function():
    """Helper function"""
    return process_data()

def process_data():
    """Process the data"""
    return format_output()
''',
        "frontend/main.js": '''function initApp() {
    // Initialize application
    setupRoutes();
    startListening();
}

function setupRoutes() {
    // Setup routing
    return true;
}
'''
    }
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path, content in test_files.items():
            zipf.writestr(file_path, content)
    
    return zip_path

def test_path_format():
    """Test that paths are project-relative"""
    print("🧪 Testing Path Format")
    print("=" * 40)
    
    zip_path = create_path_test_project()
    
    try:
        # Upload
        print("📦 Uploading project...")
        with open(zip_path, 'rb') as f:
            files = {'file': ('path_test.zip', f, 'application/zip')}
            response = requests.post('http://localhost:8000/api/upload', files=files)
        
        repo_id = response.json()['repo_id']
        print(f"✅ Uploaded: {repo_id}")
        
        # Analyze
        print("🔍 Analyzing project...")
        response = requests.get(f'http://localhost:8000/api/analyze/{repo_id}')
        
        if response.status_code == 200:
            data = response.json()
            architecture_map = data['architecture_map']
            
            print("✅ Analysis complete!")
            print(f"📊 Files analyzed: {data['files_analyzed']}")
            
            print("\n📁 FILE PATHS:")
            for file_data in architecture_map['listOfFiles']:
                file_path = file_data['filePath']
                functions = file_data['listOfFunctions']
                
                print(f"📄 {file_path}")
                
                # Verify path format
                if file_path.startswith('/') or '\\' in file_path:
                    print(f"❌ Path should be project-relative, not absolute: {file_path}")
                else:
                    print(f"✅ Good project-relative path: {file_path}")
                
                # Show functions
                for func in functions:
                    func_name = func['functionName']
                    calls = func['calls']
                    print(f"   ⚙️  {func_name} → calls {len(calls)} functions")
                
                print()
            
            return True
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        os.remove(zip_path)

if __name__ == "__main__":
    success = test_path_format()
    if success:
        print("🎉 Path format test completed!")
    else:
        print("❌ Path format test failed!")