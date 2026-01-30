#!/usr/bin/env python3
"""
Display Architecture JSON - Shows the complete architecture map in terminal
"""
import requests
import json
import zipfile
import os
import tempfile

def create_simple_test_project():
    """Create a test project to analyze"""
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "architecture_display_test.zip")
    
    test_files = {
        "app.py": '''def main():
    """Main application entry point"""
    config = load_config()
    server = create_server(config)
    start_application(server)

def load_config():
    """Load application configuration"""
    return {"host": "localhost", "port": 8000}

def create_server(config):
    """Create web server instance"""
    setup_routes()
    configure_middleware()
    return initialize_server(config)

def start_application(server):
    """Start the web application"""
    server.run()
''',
        "services/auth.py": '''def authenticate(username, password):
    """Authenticate user credentials"""
    user = find_user(username)
    if user and check_password(password, user.hash):
        return create_session(user)
    return None

def find_user(username):
    """Find user in database"""
    return query_database("users", {"username": username})

def check_password(password, hash):
    """Verify password against hash"""
    return verify_hash(password, hash)

def create_session(user):
    """Create user session"""
    return generate_token(user.id)
''',
        "utils.js": '''function validateInput(data) {
    if (!data || typeof data !== "string") {
        return false;
    }
    return data.length > 0;
}

const processData = (input) => {
    const isValid = validateInput(input);
    if (!isValid) {
        throw new Error("Invalid input");
    }
    return formatOutput(input);
};

function formatOutput(data) {
    return {
        processed: true,
        data: data.toUpperCase(),
        timestamp: Date.now()
    };
}
'''
    }
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path, content in test_files.items():
            zipf.writestr(file_path, content)
    
    return zip_path

def display_architecture_json():
    """Upload project and display the complete architecture JSON"""
    print("🏗️  ARCHITECTURE JSON DISPLAY")
    print("=" * 60)
    
    # Create test project
    print("📦 Creating test project...")
    zip_path = create_simple_test_project()
    
    try:
        # Upload project
        print("⬆️  Uploading project...")
        with open(zip_path, 'rb') as f:
            files = {'file': ('architecture_test.zip', f, 'application/zip')}
            upload_response = requests.post('http://localhost:8000/api/upload', files=files)
        
        if upload_response.status_code != 200:
            print(f"❌ Upload failed: {upload_response.status_code}")
            return
        
        repo_id = upload_response.json()['repo_id']
        print(f"✅ Upload successful! Repo ID: {repo_id}")
        
        # Analyze project
        print("🔍 Analyzing project...")
        analyze_response = requests.get(f'http://localhost:8000/api/analyze/{repo_id}')
        
        if analyze_response.status_code != 200:
            print(f"❌ Analysis failed: {analyze_response.status_code}")
            return
        
        analysis_data = analyze_response.json()
        print(f"✅ Analysis complete! Files analyzed: {analysis_data['files_analyzed']}")
        
        # Display the complete architecture JSON
        print("\n" + "=" * 60)
        print("📊 COMPLETE ARCHITECTURE JSON STRUCTURE")
        print("=" * 60)
        
        # Pretty print the entire response
        print(json.dumps(analysis_data, indent=2))
        
        print("\n" + "=" * 60)
        print("🏗️  ARCHITECTURE MAP ONLY")
        print("=" * 60)
        
        # Display just the architecture_map part
        architecture_map = analysis_data.get('architecture_map', {})
        print(json.dumps(architecture_map, indent=2))
        
        # Summary
        print("\n" + "=" * 60)
        print("📈 SUMMARY")
        print("=" * 60)
        
        list_of_files = architecture_map.get('listOfFiles', [])
        total_functions = sum(len(file.get('listOfFunctions', [])) for file in list_of_files)
        total_calls = sum(
            len(func.get('calls', []))
            for file in list_of_files
            for func in file.get('listOfFunctions', [])
        )
        
        print(f"📄 Files: {len(list_of_files)}")
        print(f"⚙️  Functions: {total_functions}")
        print(f"🔗 Function calls: {total_calls}")
        
        # File breakdown
        print(f"\n📂 Files breakdown:")
        for file_data in list_of_files:
            file_path = file_data.get('filePath')
            functions = file_data.get('listOfFunctions', [])
            print(f"  📄 {file_path}: {len(functions)} functions")
            for func in functions:
                func_name = func.get('functionName', '').split('-')[-1]
                calls = func.get('calls', [])
                print(f"    ⚙️  {func_name}() → calls {len(calls)} functions")
                if calls:
                    print(f"      🔗 {', '.join(calls)}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server!")
        print("🚨 Make sure the server is running:")
        print("   cd backend")
        print("   python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Cleanup
        os.remove(zip_path)

if __name__ == "__main__":
    display_architecture_json()