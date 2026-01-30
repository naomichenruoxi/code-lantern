#!/usr/bin/env python3
"""
Frontend Integration Test
Tests the API endpoints that frontend will use
"""
import requests
import json

def test_api_health():
    """Test API health check"""
    try:
        response = requests.get('http://localhost:8000/')
        if response.status_code == 200:
            result = response.json()
            print("✅ API Health Check:")
            print(f"   Service: {result['service']}")
            print(f"   Version: {result['version']}")
            print(f"   Endpoints: {result['endpoints']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server not running!")
        return False

def test_cors():
    """Test CORS headers for frontend"""
    try:
        response = requests.options('http://localhost:8000/api/upload',
                                   headers={'Origin': 'http://localhost:3000'})
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        print("✅ CORS Headers:")
        for header, value in cors_headers.items():
            print(f"   {header}: {value}")
        return True
    except Exception as e:
        print(f"❌ CORS test failed: {e}")
        return False

def main():
    """Run frontend integration tests"""
    print("🔧 Frontend Integration Test")
    print("=" * 40)
    
    # Test 1: API Health
    if not test_api_health():
        return
    
    print()
    
    # Test 2: CORS
    if not test_cors():
        return
    
    print()
    print("🚀 Backend is ready for frontend integration!")
    print()
    print("📚 API Documentation: backend/API_DOCS.md")
    print("🌐 Interactive Docs: http://localhost:8000/docs")
    print("💡 Example frontend code available in API_DOCS.md")

if __name__ == "__main__":
    main()