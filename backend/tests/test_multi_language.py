#!/usr/bin/env python3
"""
Test multi-language support for Code Lantern
Tests Java, C++, and Rust file analysis
"""

import requests
import zipfile
import io
import os
import time

BASE_URL = "http://localhost:8000"

# Sample Java code
JAVA_CODE = '''
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
    
    public int multiply(int a, int b) {
        return a * b;
    }
    
    public static void main(String[] args) {
        Calculator calc = new Calculator();
        int result = calc.add(5, 3);
        System.out.println("Result: " + result);
    }
}
'''

# Sample C++ code
CPP_CODE = '''
#include <iostream>
#include <vector>

int add(int a, int b) {
    return a + b;
}

int multiply(int a, int b) {
    return a * b;
}

void printResult(int value) {
    std::cout << "Result: " << value << std::endl;
}

int main() {
    int result = add(5, 3);
    printResult(result);
    return 0;
}
'''

# Sample Rust code
RUST_CODE = '''
fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn multiply(a: i32, b: i32) -> i32 {
    a * b
}

fn print_result(value: i32) {
    println!("Result: {}", value);
}

fn main() {
    let result = add(5, 3);
    print_result(result);
}
'''

def create_test_zip():
    """Create a ZIP file with Java, C++, and Rust files"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('Calculator.java', JAVA_CODE)
        zip_file.writestr('calculator.cpp', CPP_CODE)
        zip_file.writestr('calculator.rs', RUST_CODE)
    
    zip_buffer.seek(0)
    return zip_buffer

def test_multi_language_support():
    """Test the complete workflow with multi-language files"""
    print("=" * 60)
    print("Testing Multi-Language Support (Java, C++, Rust)")
    print("=" * 60)
    
    # Step 1: Upload ZIP file
    print("\n1. Uploading multi-language project...")
    zip_file = create_test_zip()
    
    files = {'file': ('test_project.zip', zip_file, 'application/zip')}
    response = requests.post(f"{BASE_URL}/api/upload", files=files)
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.status_code}")
        print(response.text)
        return False
    
    upload_data = response.json()
    repo_id = upload_data['repo_id']
    print(f"✅ Upload successful! Repo ID: {repo_id}")
    
    # Step 2: Analyze the project
    print("\n2. Analyzing project architecture...")
    response = requests.get(f"{BASE_URL}/api/analyze/{repo_id}")
    
    if response.status_code != 200:
        print(f"❌ Analysis failed: {response.status_code}")
        print(response.text)
        return False
    
    analysis_data = response.json()
    print(f"✅ Analysis complete! Files analyzed: {analysis_data['files_analyzed']}")
    
    # Step 3: Check architecture map
    architecture_map = analysis_data['architecture_map']
    files = architecture_map['listOfFiles']
    
    print(f"\n3. Checking detected files and functions...")
    
    java_found = False
    cpp_found = False
    rust_found = False
    
    for file_data in files:
        file_path = file_data['filePath']
        functions = file_data['listOfFunctions']
        
        print(f"\n   📄 {file_path}")
        print(f"      Functions found: {len(functions)}")
        
        if file_path.endswith('.java'):
            java_found = True
            print(f"      ✅ Java file detected")
            for func in functions:
                func_name = func['functionName'].split('-')[-1]
                print(f"         - {func_name}")
        
        elif file_path.endswith('.cpp'):
            cpp_found = True
            print(f"      ✅ C++ file detected")
            for func in functions:
                func_name = func['functionName'].split('-')[-1]
                print(f"         - {func_name}")
        
        elif file_path.endswith('.rs'):
            rust_found = True
            print(f"      ✅ Rust file detected")
            for func in functions:
                func_name = func['functionName'].split('-')[-1]
                print(f"         - {func_name}")
    
    # Step 4: Test function details endpoint
    print(f"\n4. Testing AI function descriptions...")
    
    # Test Java function
    if java_found:
        print(f"\n   Testing Java function...")
        response = requests.get(
            f"{BASE_URL}/api/function/{repo_id}",
            params={'file_path': 'Calculator.java', 'function_name': 'add'}
        )
        if response.status_code == 200:
            details = response.json()['details']
            print(f"   ✅ Java function 'add': {details.get('description', 'N/A')[:100]}...")
        else:
            print(f"   ⚠️  Java function details failed: {response.status_code}")
    
    # Test C++ function
    if cpp_found:
        print(f"\n   Testing C++ function...")
        response = requests.get(
            f"{BASE_URL}/api/function/{repo_id}",
            params={'file_path': 'calculator.cpp', 'function_name': 'add'}
        )
        if response.status_code == 200:
            details = response.json()['details']
            print(f"   ✅ C++ function 'add': {details.get('description', 'N/A')[:100]}...")
        else:
            print(f"   ⚠️  C++ function details failed: {response.status_code}")
    
    # Test Rust function
    if rust_found:
        print(f"\n   Testing Rust function...")
        response = requests.get(
            f"{BASE_URL}/api/function/{repo_id}",
            params={'file_path': 'calculator.rs', 'function_name': 'add'}
        )
        if response.status_code == 200:
            details = response.json()['details']
            print(f"   ✅ Rust function 'add': {details.get('description', 'N/A')[:100]}...")
        else:
            print(f"   ⚠️  Rust function details failed: {response.status_code}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Java support:  {'✅ Working' if java_found else '❌ Failed'}")
    print(f"C++ support:   {'✅ Working' if cpp_found else '❌ Failed'}")
    print(f"Rust support:  {'✅ Working' if rust_found else '❌ Failed'}")
    
    all_passed = java_found and cpp_found and rust_found
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    print("\n🔧 Make sure the backend server is running on http://localhost:8000")
    print("   Run: cd backend && python main.py\n")
    
    input("Press Enter to start tests...")
    
    try:
        success = test_multi_language_support()
        exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to backend server")
        print("   Make sure the server is running: cd backend && python main.py")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
