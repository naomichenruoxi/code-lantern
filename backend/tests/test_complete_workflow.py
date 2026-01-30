#!/usr/bin/env python3
"""
Test the complete workflow with Gemini API integration
"""
import requests
import zipfile
import os
import tempfile
import json

def create_test_zip():
    """Create a test ZIP file with more complex functions"""
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "test_repo.zip")
    
    # Create test files with realistic functions (no leading spaces)
    test_files = {
        "user_service.py": '''def create_user(username, email, age):
    """Creates a new user with validation"""
    if age < 18:
        raise ValueError("User must be 18 or older")
    
    user = {
        "id": generate_id(),
        "username": username,
        "email": email,
        "age": age
    }
    
    return save_user(user)

def validate_email(email):
    """Validates email format using regex"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def generate_id():
    """Generates a unique UUID for user"""
    import uuid
    return str(uuid.uuid4())
''',
        "utils.js": '''function calculateTotalPrice(items, taxRate) {
    const subtotal = items.reduce((sum, item) => {
        return sum + (item.price * item.quantity);
    }, 0);
    
    const tax = subtotal * taxRate;
    return formatCurrency(subtotal + tax);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function processPayment(userId, amount, paymentMethod) {
    const user = getUserById(userId);
    if (!user) {
        throw new Error('User not found');
    }
    
    return chargePayment(amount, paymentMethod);
}
''',
        "package.json": '{"name": "test-project", "version": "1.0.0"}'
    }
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path, content in test_files.items():
            zipf.writestr(file_path, content)
    
    return zip_path

def test_complete_workflow():
    """Test upload -> analyze -> files -> function details"""
    print("🚀 Testing Complete Workflow with Gemini API")
    print("=" * 50)
    
    # Step 1: Upload
    zip_path = create_test_zip()
    try:
        print("📦 Step 1: Uploading project...")
        with open(zip_path, 'rb') as f:
            files = {'file': ('test_repo.zip', f, 'application/zip')}
            response = requests.post('http://localhost:8000/api/upload', files=files)
        
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.status_code}")
            return
        
        repo_id = response.json()['repo_id']
        print(f"✅ Upload successful! Repo ID: {repo_id}")
        
        # Step 2: Analyze
        print("\n🔍 Step 2: Analyzing project...")
        response = requests.get(f'http://localhost:8000/api/analyze/{repo_id}')
        if response.status_code != 200:
            print(f"❌ Analysis failed: {response.status_code}")
            return
        
        analysis = response.json()
        print(f"✅ Analysis complete! Files: {analysis['files_analyzed']}")
        
        # Step 3: Get file list
        print("\n📁 Step 3: Getting file list...")
        response = requests.get(f'http://localhost:8000/api/files/{repo_id}')
        if response.status_code != 200:
            print(f"❌ File list failed: {response.status_code}")
            return
        
        files_data = response.json()
        print(f"✅ Found {files_data['totalFiles']} files")
        
        # Display files and functions
        for file_info in files_data['files']:
            print(f"\n📄 File: {file_info['filePath']}")
            print(f"   Functions: {file_info['functionCount']}")
            for func in file_info['functions']:
                print(f"   - {func}")
        
        # Step 4: Test function details (pick first function)
        if files_data['files'] and files_data['files'][0]['functions']:
            test_file = files_data['files'][0]
            test_function = test_file['functions'][0]
            
            print(f"\n🔍 Step 4: Getting details for function '{test_function}' in file '{test_file['filePath']}'...")
            
            params = {
                'file_path': test_file['filePath'],
                'function_name': test_function
            }
            
            response = requests.get(f'http://localhost:8000/api/function/{repo_id}', params=params)
            
            if response.status_code == 200:
                func_details = response.json()
                print("✅ Function details retrieved!")
                print(f"\n🏷️  Function Details:")
                print(f"Name: {func_details['details']['function_name']}")
                print(f"Inputs: {func_details['details']['inputs']}")
                print(f"Outputs: {func_details['details']['outputs']}")
                print(f"Description: {func_details['details']['description']}")
            else:
                print(f"❌ Function details failed: {response.status_code}")
                print(response.text)
        
        print("\n🎉 Complete workflow test successful!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed! Make sure server is running.")
    finally:
        os.remove(zip_path)

if __name__ == "__main__":
    test_complete_workflow()