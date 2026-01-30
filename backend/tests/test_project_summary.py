#!/usr/bin/env python3
"""
Test the new project summary endpoint
"""
import requests
import json
import zipfile
import os
import tempfile

def create_test_project():
    """Create a test project for summary analysis"""
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "summary_test.zip")
    
    test_files = {
        "main.py": '''def main():
    """Main application entry point"""
    config = load_config()
    app = create_app(config)
    run_server(app)

def load_config():
    """Load configuration from environment"""
    return {"debug": True, "port": 8000}

def create_app(config):
    """Create Flask application"""
    setup_routes()
    configure_logging()
    return initialize_flask_app(config)
''',
        "services/auth.py": '''def authenticate_user(username, password):
    """Authenticate user credentials"""
    user = find_user(username)
    if user and verify_password(password, user.password_hash):
        return create_session(user)
    return None

def find_user(username):
    """Find user in database"""
    return query_database("users", {"username": username})

def verify_password(password, hash):
    """Verify password against hash"""
    return check_bcrypt(password, hash)
''',
        "utils/helpers.js": '''function validateEmail(email) {
    const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
    return emailRegex.test(email);
}

const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
};

function calculateTotal(items) {
    return items.reduce((sum, item) => sum + item.price, 0);
}
''',
        "config.json": '{"name": "test-project", "version": "1.0.0"}'
    }
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path, content in test_files.items():
            zipf.writestr(file_path, content)
    
    return zip_path

def test_project_summary():
    """Test the complete flow including project summary"""
    print("🧪 Testing Project Summary Endpoint")
    print("=" * 50)
    
    zip_path = create_test_project()
    
    try:
        # Upload
        print("📦 Uploading project...")
        with open(zip_path, 'rb') as f:
            files = {'file': ('summary_test.zip', f, 'application/zip')}
            response = requests.post('http://localhost:8000/api/upload', files=files)
        
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.status_code}")
            return
        
        repo_id = response.json()['repo_id']
        print(f"✅ Uploaded: {repo_id}")
        
        # Analyze
        print("🔍 Analyzing project...")
        response = requests.get(f'http://localhost:8000/api/analyze/{repo_id}')
        if response.status_code != 200:
            print(f"❌ Analysis failed: {response.status_code}")
            return
        
        print("✅ Analysis complete")
        
        # Get Project Summary
        print("📊 Getting project summary...")
        response = requests.get(f'http://localhost:8000/api/project-summary/{repo_id}')
        
        if response.status_code == 200:
            summary_data = response.json()
            
            print("✅ Project summary generated!")
            print("\n📊 PROJECT STATISTICS:")
            
            stats = summary_data['project_stats']
            
            # File stats
            file_stats = stats['file_stats']
            print(f"📄 Total Files: {file_stats['total_files']}")
            print(f"📏 Lines of Code: {file_stats['estimated_lines_of_code']}")
            print(f"📎 File Extensions: {file_stats['file_extensions']}")
            
            # Function stats
            func_stats = stats['function_stats']
            print(f"\n⚙️  Total Functions: {func_stats['total_functions']}")
            print(f"🔗 Function Calls: {func_stats['total_function_calls']}")
            print(f"📈 Avg Complexity: {func_stats['average_complexity']}")
            print(f"📊 Functions/File: {func_stats['functions_per_file']}")
            
            # Language stats
            lang_stats = stats['language_stats']
            print(f"\n💻 Primary Language: {lang_stats['primary_language']}")
            print(f"🔤 Languages: {list(lang_stats['languages'].keys())}")
            print(f"📊 Language %: {lang_stats['language_percentages']}")
            
            # Complexity metrics
            complexity = stats['complexity_metrics']
            print(f"\n🎯 Code Health Score: {complexity['code_health_score']}/100")
            print(f"📏 Project Size: {complexity['project_size']}")
            print(f"🏗️  Architecture: {complexity['architecture_complexity']}")
            
            # AI Summary
            ai_summary = summary_data['ai_summary']
            print(f"\n🤖 AI ANALYSIS:")
            print(f"📝 Overview: {ai_summary['overview']}")
            print(f"💪 Strengths: {', '.join(ai_summary['strengths'])}")
            print(f"💡 Recommendations: {', '.join(ai_summary['recommendations'])}")
            print(f"🏗️  Architecture: {ai_summary['architecture_insights']}")
            print(f"⚡ Technology: {ai_summary['technology_assessment']}")
            
            print(f"\n⏰ Generated: {summary_data['generated_at']}")
            
            return True
        else:
            print(f"❌ Summary failed: {response.status_code}")
            print(response.text)
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        os.remove(zip_path)

if __name__ == "__main__":
    success = test_project_summary()
    if success:
        print("\n🎉 Project Summary Endpoint Working!")
    else:
        print("\n❌ Fix issues before deployment")