#!/usr/bin/env python3
"""
Comprehensive API Endpoint Test Suite
Tests all endpoints before GitHub push
"""
import requests
import json
import zipfile
import os
import tempfile
import time

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m' 
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text.center(60)}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def create_comprehensive_test_project():
    """Create a realistic test project with multiple files and functions"""
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "comprehensive_test.zip")
    
    test_files = {
        "main.py": '''def main():
    """Main application entry point"""
    config = load_configuration()
    app = initialize_app(config)
    start_server(app)

def load_configuration():
    """Load application configuration from environment"""
    return {
        "debug": True,
        "host": "localhost",
        "port": 8000
    }

def initialize_app(config):
    """Initialize the Flask application"""
    from flask import Flask
    app = Flask(__name__)
    setup_routes(app)
    configure_middleware(app, config)
    return app

def start_server(app):
    """Start the web server"""
    app.run(debug=True)
''',
        "services/auth.py": '''def authenticate_user(username, password):
    """Authenticate user with username and password"""
    user = find_user_by_username(username)
    if user and verify_password(password, user.password_hash):
        return generate_session_token(user)
    return None

def find_user_by_username(username):
    """Find user by username in database"""
    return database_query("SELECT * FROM users WHERE username = ?", username)

def verify_password(password, password_hash):
    """Verify password against stored hash"""
    import bcrypt
    return bcrypt.checkpw(password.encode(), password_hash)

def generate_session_token(user):
    """Generate JWT session token for user"""
    import jwt
    payload = {"user_id": user.id, "exp": get_expiration_time()}
    return jwt.encode(payload, get_secret_key(), algorithm="HS256")
''',
        "utils/helpers.js": '''function validateEmail(email) {
    // Validate email format using regex
    const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
    return emailRegex.test(email);
}

const formatCurrency = (amount, currency = 'USD') => {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
};

function calculateTotal(items) {
    // Calculate total price for shopping cart
    return items.reduce((total, item) => {
        return total + (item.price * item.quantity);
    }, 0);
}

async function fetchUserData(userId) {
    const response = await fetch(`/api/users/${userId}`);
    const userData = await response.json();
    
    if (!userData) {
        throw new Error('User not found');
    }
    
    return processUserData(userData);
}

function processUserData(userData) {
    return {
        id: userData.id,
        name: formatName(userData.firstName, userData.lastName),
        email: userData.email,
        isActive: userData.status === 'active'
    };
}
''',
        "database/models.py": '''class User:
    """User model for authentication and profile management"""
    
    def __init__(self, username, email, password_hash):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = get_current_timestamp()
    
    def save(self):
        """Save user to database"""
        return database_insert("users", self.__dict__)
    
    def update_profile(self, **kwargs):
        """Update user profile information"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self.save()

def create_user_table():
    """Create users table in database"""
    sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username VARCHAR(50) UNIQUE,
        email VARCHAR(100) UNIQUE,
        password_hash VARCHAR(255),
        created_at TIMESTAMP
    )
    """
    return execute_sql(sql)
''',
        "frontend/components.jsx": '''const UserProfile = ({ userId }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchUserProfile(userId)
            .then(setUser)
            .finally(() => setLoading(false));
    }, [userId]);

    if (loading) {
        return <LoadingSpinner />;
    }

    return (
        <div className="user-profile">
            <h2>{user?.name}</h2>
            <p>{user?.email}</p>
        </div>
    );
};

function LoadingSpinner() {
    return (
        <div className="spinner">
            <div className="spinner-circle"></div>
        </div>
    );
}

const Button = ({ onClick, children, variant = 'primary' }) => {
    return (
        <button 
            className={`btn btn-${variant}`}
            onClick={onClick}
        >
            {children}
        </button>
    );
};
''',
        "package.json": '{"name": "comprehensive-test", "version": "1.0.0"}',
        "README.md": "# Test Project\n\nThis is a comprehensive test project."
    }
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path, content in test_files.items():
            zipf.writestr(file_path, content)
    
    return zip_path

class APITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.repo_id = None
        self.test_results = {}
    
    def test_server_health(self):
        """Test if server is running and responding"""
        print_info("Testing server health...")
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                print_success(f"Server is running: {data.get('service', 'Unknown')}")
                return True
            else:
                print_error(f"Server returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print_error("Cannot connect to server! Make sure it's running on localhost:8000")
            return False
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            return False
    
    def test_upload_endpoint(self, zip_path):
        """Test POST /api/upload"""
        print_info("Testing upload endpoint...")
        try:
            with open(zip_path, 'rb') as f:
                files = {'file': ('comprehensive_test.zip', f, 'application/zip')}
                response = requests.post(f"{self.base_url}/api/upload", files=files)
            
            if response.status_code == 200:
                data = response.json()
                self.repo_id = data.get('repo_id')
                print_success(f"Upload successful: {self.repo_id}")
                print_info(f"Extracted to: {data.get('extracted_to')}")
                self.test_results['upload'] = True
                return True
            else:
                error_data = response.json() if response.content else {}
                print_error(f"Upload failed: {response.status_code}")
                print_error(f"Error: {error_data.get('detail', 'Unknown error')}")
                self.test_results['upload'] = False
                return False
        except Exception as e:
            print_error(f"Upload test failed: {e}")
            self.test_results['upload'] = False
            return False
    
    def test_analyze_endpoint(self):
        """Test GET /api/analyze/{repo_id}"""
        if not self.repo_id:
            print_error("No repo_id available for analysis test")
            return False
        
        print_info("Testing analyze endpoint...")
        try:
            response = requests.get(f"{self.base_url}/api/analyze/{self.repo_id}")
            
            if response.status_code == 200:
                data = response.json()
                files_analyzed = data.get('files_analyzed', 0)
                architecture_map = data.get('architecture_map', {})
                list_of_files = architecture_map.get('listOfFiles', [])
                
                print_success(f"Analysis successful: {files_analyzed} files analyzed")
                print_info(f"Architecture map contains {len(list_of_files)} files")
                
                # Validate structure
                if list_of_files:
                    sample_file = list_of_files[0]
                    print_info(f"Sample file: {sample_file.get('filePath')}")
                    functions = sample_file.get('listOfFunctions', [])
                    print_info(f"Functions found: {len(functions)}")
                    
                    if functions:
                        sample_function = functions[0]
                        print_info(f"Sample function: {sample_function.get('functionName')}")
                        calls = sample_function.get('calls', [])
                        print_info(f"Function calls: {len(calls)}")
                
                self.test_results['analyze'] = True
                return True
            else:
                error_data = response.json() if response.content else {}
                print_error(f"Analysis failed: {response.status_code}")
                print_error(f"Error: {error_data.get('detail', 'Unknown error')}")
                self.test_results['analyze'] = False
                return False
        except Exception as e:
            print_error(f"Analysis test failed: {e}")
            self.test_results['analyze'] = False
            return False
    
    def test_files_endpoint(self):
        """Test GET /api/files/{repo_id}"""
        if not self.repo_id:
            print_error("No repo_id available for files test")
            return False
        
        print_info("Testing files endpoint...")
        try:
            response = requests.get(f"{self.base_url}/api/files/{self.repo_id}")
            
            if response.status_code == 200:
                data = response.json()
                total_files = data.get('totalFiles', 0)
                files = data.get('files', [])
                
                print_success(f"Files endpoint successful: {total_files} files")
                
                # Show file details
                for file_info in files[:3]:  # Show first 3 files
                    file_path = file_info.get('filePath')
                    function_count = file_info.get('functionCount', 0)
                    functions = file_info.get('functions', [])
                    print_info(f"📄 {file_path}: {function_count} functions")
                    if functions:
                        print_info(f"   Functions: {', '.join(functions[:3])}...")
                
                self.test_results['files'] = True
                return True
            else:
                error_data = response.json() if response.content else {}
                print_error(f"Files endpoint failed: {response.status_code}")
                print_error(f"Error: {error_data.get('detail', 'Unknown error')}")
                self.test_results['files'] = False
                return False
        except Exception as e:
            print_error(f"Files test failed: {e}")
            self.test_results['files'] = False
            return False
    
    def test_function_endpoint(self):
        """Test GET /api/function/{repo_id}"""
        if not self.repo_id:
            print_error("No repo_id available for function test")
            return False
        
        print_info("Testing function endpoint...")
        try:
            # First get files to find a function to test
            files_response = requests.get(f"{self.base_url}/api/files/{self.repo_id}")
            if files_response.status_code != 200:
                print_error("Cannot get files for function test")
                return False
            
            files_data = files_response.json()
            files = files_data.get('files', [])
            
            if not files or not files[0].get('functions'):
                print_error("No functions found for testing")
                return False
            
            # Test first function from first file
            test_file = files[0]
            test_function = test_file['functions'][0]
            file_path = test_file['filePath']
            
            print_info(f"Testing function: {test_function} in {file_path}")
            
            params = {
                'file_path': file_path,
                'function_name': test_function
            }
            
            response = requests.get(f"{self.base_url}/api/function/{self.repo_id}", params=params)
            
            if response.status_code == 200:
                data = response.json()
                details = data.get('details', {})
                
                function_name = details.get('function_name')
                inputs = details.get('inputs')
                outputs = details.get('outputs')
                description = details.get('description')
                
                print_success(f"Function details retrieved successfully")
                print_info(f"Function: {function_name}")
                print_info(f"Inputs: {inputs[:50]}..." if len(str(inputs)) > 50 else f"Inputs: {inputs}")
                print_info(f"Outputs: {outputs[:50]}..." if len(str(outputs)) > 50 else f"Outputs: {outputs}")
                print_info(f"Description: {description[:100]}..." if len(str(description)) > 100 else f"Description: {description}")
                
                self.test_results['function'] = True
                return True
            else:
                error_data = response.json() if response.content else {}
                print_error(f"Function endpoint failed: {response.status_code}")
                print_error(f"Error: {error_data.get('detail', 'Unknown error')}")
                self.test_results['function'] = False
                return False
        except Exception as e:
            print_error(f"Function test failed: {e}")
            self.test_results['function'] = False
            return False
    
    def test_error_handling(self):
        """Test error handling with invalid requests"""
        print_info("Testing error handling...")
        
        tests_passed = 0
        total_tests = 3
        
        # Test invalid repo ID
        try:
            response = requests.get(f"{self.base_url}/api/files/invalid-repo-id")
            if response.status_code == 404:
                print_success("404 error handling works for invalid repo ID")
                tests_passed += 1
            else:
                print_warning(f"Expected 404, got {response.status_code}")
        except Exception as e:
            print_error(f"Error handling test failed: {e}")
        
        # Test invalid file type upload
        try:
            files = {'file': ('test.txt', b'invalid content', 'text/plain')}
            response = requests.post(f"{self.base_url}/api/upload", files=files)
            if response.status_code == 400:
                print_success("400 error handling works for invalid file type")
                tests_passed += 1
            else:
                print_warning(f"Expected 400, got {response.status_code}")
        except Exception as e:
            print_error(f"File type error test failed: {e}")
        
        # Test function not found
        try:
            params = {'file_path': 'nonexistent.py', 'function_name': 'fake_function'}
            response = requests.get(f"{self.base_url}/api/function/invalid-repo", params=params)
            if response.status_code == 404:
                print_success("404 error handling works for nonexistent function")
                tests_passed += 1
            else:
                print_warning(f"Expected 404, got {response.status_code}")
        except Exception as e:
            print_error(f"Function error test failed: {e}")
        
        success_rate = tests_passed / total_tests
        self.test_results['error_handling'] = success_rate >= 0.66
        
        print_info(f"Error handling tests: {tests_passed}/{total_tests} passed")
        return success_rate >= 0.66
    
    def test_cors(self):
        """Test CORS headers"""
        print_info("Testing CORS headers...")
        try:
            response = requests.options(
                f"{self.base_url}/api/upload",
                headers={'Origin': 'http://localhost:3000'}
            )
            
            cors_origin = response.headers.get('Access-Control-Allow-Origin')
            cors_methods = response.headers.get('Access-Control-Allow-Methods')
            
            if cors_origin == '*':
                print_success("CORS allows all origins")
                self.test_results['cors'] = True
                return True
            else:
                print_warning(f"CORS origin: {cors_origin}")
                self.test_results['cors'] = False
                return False
        except Exception as e:
            print_error(f"CORS test failed: {e}")
            self.test_results['cors'] = False
            return False
    
    def run_all_tests(self):
        """Run complete test suite"""
        print_header("🧪 COMPREHENSIVE API TEST SUITE")
        
        # Create test project
        print_info("Creating comprehensive test project...")
        zip_path = create_comprehensive_test_project()
        
        try:
            # Test sequence
            tests = [
                ("Server Health", self.test_server_health),
                ("CORS Headers", self.test_cors),
                ("Upload Endpoint", lambda: self.test_upload_endpoint(zip_path)),
                ("Analyze Endpoint", self.test_analyze_endpoint),
                ("Files Endpoint", self.test_files_endpoint), 
                ("Function Endpoint", self.test_function_endpoint),
                ("Error Handling", self.test_error_handling)
            ]
            
            results = {}
            for test_name, test_func in tests:
                print_header(f"🔍 {test_name}")
                results[test_name] = test_func()
                time.sleep(1)  # Small delay between tests
            
            # Summary
            print_header("📊 TEST RESULTS SUMMARY")
            
            passed_count = sum(1 for result in results.values() if result)
            total_count = len(results)
            
            for test_name, result in results.items():
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{status} {test_name}")
            
            print(f"\n{Colors.BOLD}Overall Result: {passed_count}/{total_count} tests passed{Colors.END}")
            
            if passed_count == total_count:
                print_success("🎉 ALL TESTS PASSED! API is ready for production")
                return True
            else:
                print_error(f"❌ {total_count - passed_count} tests failed. Fix issues before deployment")
                return False
        
        finally:
            # Cleanup
            os.remove(zip_path)

def main():
    """Main test runner"""
    print_header("🏮 CODE LANTERN API TEST SUITE")
    print_info("Starting comprehensive endpoint testing...")
    
    tester = APITester()
    success = tester.run_all_tests()
    
    if success:
        print_header("🚀 READY FOR GITHUB PUSH")
        print_success("All endpoints working correctly")
        print_success("Error handling implemented")
        print_success("CORS configured properly")
        print_success("AI integration functional")
        print("\n" + Colors.GREEN + Colors.BOLD + "✅ SAFE TO PUSH TO GITHUB!" + Colors.END)
    else:
        print_header("⚠️  FIX REQUIRED")
        print_error("Some tests failed - fix issues before pushing")
    
    return success

if __name__ == "__main__":
    main()