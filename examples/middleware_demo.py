#!/usr/bin/env python3
"""
Demo script to showcase the new error handling and middleware features.

This script makes various API calls to demonstrate:
1. Request ID tracking
2. Rate limiting
3. Validation errors
4. Error handling
5. Process time headers
"""

import requests
import time
from typing import Dict, Any


def print_response(title: str, response: requests.Response) -> None:
    """Print formatted response details."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"\nHeaders:")
    for key in ['X-Request-ID', 'X-Process-Time', 'X-RateLimit-Limit', 
                'X-RateLimit-Remaining', 'Retry-After']:
        if key in response.headers:
            print(f"  {key}: {response.headers[key]}")
    
    print(f"\nResponse Body:")
    try:
        import json
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)


def test_basic_request(base_url: str) -> None:
    """Test basic request with request ID and process time."""
    print("\n" + "="*60)
    print("TEST 1: Basic Request (Request ID & Process Time)")
    print("="*60)
    
    response = requests.get(f"{base_url}/api/v1/health")
    print_response("Health Check Response", response)


def test_validation_error(base_url: str) -> None:
    """Test validation error with field-level details."""
    print("\n" + "="*60)
    print("TEST 2: Validation Error (Invalid Port)")
    print("="*60)
    
    # Send invalid port (out of range)
    response = requests.post(
        f"{base_url}/api/v1/connect",
        json={"host": "localhost", "port": 999999}
    )
    print_response("Validation Error Response", response)


def test_validation_error_missing_field(base_url: str) -> None:
    """Test validation error with type mismatch."""
    print("\n" + "="*60)
    print("TEST 3: Validation Error (Type Mismatch)")
    print("="*60)
    
    # Send string for port instead of int
    response = requests.post(
        f"{base_url}/api/v1/connect",
        json={"host": "localhost", "port": "not_a_number"}
    )
    print_response("Type Validation Error Response", response)


def test_http_error(base_url: str) -> None:
    """Test HTTP 404 error."""
    print("\n" + "="*60)
    print("TEST 4: HTTP Error (404 Not Found)")
    print("="*60)
    
    response = requests.get(f"{base_url}/completely/invalid/path")
    print_response("404 Error Response", response)


def test_rate_limiting(base_url: str) -> None:
    """Test rate limiting by making multiple rapid requests."""
    print("\n" + "="*60)
    print("TEST 5: Rate Limiting (60 requests/minute)")
    print("="*60)
    
    print("\nMaking 5 requests rapidly...")
    
    for i in range(5):
        response = requests.get(f"{base_url}/api")
        status = response.status_code
        remaining = response.headers.get('X-RateLimit-Remaining', 'N/A')
        print(f"  Request {i+1}: Status {status}, Remaining: {remaining}")
        
        # If we get rate limited, show the full response
        if status == 429:
            print_response(f"Rate Limited at Request {i+1}", response)
            break
        
        # Small delay to avoid instant rate limiting
        time.sleep(0.1)


def test_process_time(base_url: str) -> None:
    """Test process time header."""
    print("\n" + "="*60)
    print("TEST 6: Process Time Tracking")
    print("="*60)
    
    print("\nMaking multiple requests to observe process times:")
    
    for i in range(3):
        response = requests.get(f"{base_url}/api")
        process_time = response.headers.get('X-Process-Time', 'N/A')
        request_id = response.headers.get('X-Request-ID', 'N/A')
        print(f"  Request {i+1}: {process_time}s (ID: {request_id[:8]}...)")


def test_request_id_consistency(base_url: str) -> None:
    """Test that request ID is consistent across response."""
    print("\n" + "="*60)
    print("TEST 7: Request ID Consistency")
    print("="*60)
    
    response = requests.get(f"{base_url}/completely/invalid/path")
    
    header_id = response.headers.get('X-Request-ID', 'N/A')
    body_id = response.json().get('request_id', 'N/A')
    
    print(f"\nRequest ID in Header: {header_id}")
    print(f"Request ID in Body:   {body_id}")
    print(f"Match: {'✓ Yes' if header_id == body_id else '✗ No'}")


def main():
    """Run all demonstration tests."""
    base_url = "http://localhost:8000"
    
    print("\n" + "="*60)
    print("LFS-Ayats API Error Handling & Middleware Demo")
    print("="*60)
    print(f"\nBase URL: {base_url}")
    print("\nThis demo showcases the new middleware features:")
    print("  • Request ID tracking")
    print("  • Error handling with consistent format")
    print("  • Validation error formatting")
    print("  • Rate limiting")
    print("  • Process time tracking")
    
    try:
        # Test if server is running
        response = requests.get(f"{base_url}/api/v1/health", timeout=2)
        print("\n✓ Server is running!")
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Error: Cannot connect to server at {base_url}")
        print(f"  Make sure the API is running with:")
        print(f"  uvicorn src.api.main:app --reload")
        return
    
    # Run all tests
    try:
        test_basic_request(base_url)
        test_validation_error(base_url)
        test_validation_error_missing_field(base_url)
        test_http_error(base_url)
        test_request_id_consistency(base_url)
        test_process_time(base_url)
        test_rate_limiting(base_url)
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nError during demo: {e}")
    
    print("\n" + "="*60)
    print("Demo Complete!")
    print("="*60)
    print("\nKey Features Demonstrated:")
    print("  ✓ Request IDs in all responses")
    print("  ✓ User-friendly validation errors")
    print("  ✓ Consistent error format")
    print("  ✓ Rate limiting protection")
    print("  ✓ Process time tracking")
    print("\nAll responses include X-Request-ID for tracing.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
