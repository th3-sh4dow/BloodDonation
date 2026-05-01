#!/usr/bin/env python
"""
Comprehensive System Test for Blood Donation Management System
Tests all API endpoints and core functionality
"""

import requests
import json
from datetime import date, timedelta

BASE_URL = 'http://127.0.0.1:8000/api'
session = requests.Session()

def get_csrf_token():
    """Get CSRF token from cookies"""
    return session.cookies.get('csrftoken', '')

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

test_results = {'passed': 0, 'failed': 0, 'total': 0}

def print_test(name, status, message=''):
    """Print test result with color"""
    test_results['total'] += 1
    if status:
        test_results['passed'] += 1
        print(f"{GREEN}✓{RESET} {name}")
        if message:
            print(f"  {BLUE}{message}{RESET}")
    else:
        test_results['failed'] += 1
        print(f"{RED}✗{RESET} {name}")
        if message:
            print(f"  {RED}{message}{RESET}")

def test_endpoint(method, endpoint, data=None, expected_status=200, description=''):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        headers = {'X-CSRFToken': get_csrf_token()}
        if method == 'GET':
            response = session.get(url, headers=headers)
        elif method == 'POST':
            response = session.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = session.put(url, json=data, headers=headers)
        
        success = response.status_code == expected_status
        msg = f"Status: {response.status_code}"
        if success and response.content:
            try:
                result = response.json()
                if isinstance(result, dict) and len(result) <= 3:
                    msg += f" | Response: {result}"
            except:
                pass
        
        print_test(f"{method} {endpoint} - {description}", success, msg)
        return response
    except Exception as e:
        print_test(f"{method} {endpoint} - {description}", False, str(e))
        return None

print(f"\n{BLUE}{'='*70}{RESET}")
print(f"{BLUE}Blood Donation System - Comprehensive Test Suite{RESET}")
print(f"{BLUE}{'='*70}{RESET}\n")

# Test 1: Server Health
print(f"\n{YELLOW}[1] Server Health Check{RESET}")
# First request to get CSRF token
session.get(f"{BASE_URL}/stats/")
test_endpoint('GET', '/stats/', description='Check server is running')

# Test 2: Authentication - Register
print(f"\n{YELLOW}[2] User Registration{RESET}")
test_user = {
    'username': f'testuser_{date.today().strftime("%Y%m%d")}',
    'email': f'test_{date.today().strftime("%Y%m%d")}@example.com',
    'password': 'testpass123',
    'first_name': 'Test',
    'last_name': 'User',
    'blood_group': 'O+',
    'phone': '9876543210',
    'city': 'Mumbai',
    'state': 'Maharashtra',
    'date_of_birth': '1995-01-15'
}
response = test_endpoint('POST', '/register/', data=test_user, expected_status=201, 
                        description='Register new user')

# Test 3: Authentication - Login
print(f"\n{YELLOW}[3] User Login{RESET}")
login_data = {
    'username': test_user['username'],
    'password': test_user['password']
}
response = test_endpoint('POST', '/login/', data=login_data, expected_status=200,
                        description='Login with credentials')

# Test 4: Check Auth Status
print(f"\n{YELLOW}[4] Authentication Status{RESET}")
response = test_endpoint('GET', '/auth/check/', description='Check if authenticated')
if response and response.json().get('authenticated'):
    print_test('User is authenticated', True)
else:
    print_test('User is authenticated', False)

# Test 5: Profile Management
print(f"\n{YELLOW}[5] Profile Management{RESET}")
test_endpoint('GET', '/profile/', description='Get user profile')
profile_update = {'is_available': True, 'city': 'Mumbai'}
test_endpoint('PUT', '/profile/', data=profile_update, description='Update profile')

# Test 6: Donor Search
print(f"\n{YELLOW}[6] Donor Search{RESET}")
test_endpoint('GET', '/donors/', description='List all donors')
test_endpoint('GET', '/donors/?blood_group=O+', description='Search by blood group')
test_endpoint('GET', '/donors/?city=Mumbai', description='Search by city')
test_endpoint('GET', '/donors/?blood_group=A+&city=Mumbai', 
             description='Search with multiple filters')

# Test 7: Blood Requests
print(f"\n{YELLOW}[7] Blood Request Management{RESET}")
blood_request = {
    'patient_name': 'John Doe',
    'blood_group_needed': 'A+',
    'units_needed': 2,
    'hospital_name': 'City Hospital',
    'city': 'Mumbai',
    'contact_number': '9876543210',
    'urgency': 'urgent',
    'notes': 'Required for surgery'
}
response = test_endpoint('POST', '/requests/', data=blood_request, expected_status=201,
                        description='Create blood request')

request_id = None
if response:
    try:
        request_id = response.json().get('id')
    except:
        pass

test_endpoint('GET', '/requests/', description='List all requests')
test_endpoint('GET', '/requests/?status=open', description='Filter by status')
test_endpoint('GET', '/requests/?blood_group=A+', description='Filter by blood group')

if request_id:
    test_endpoint('GET', f'/requests/{request_id}/', description='Get specific request')
    test_endpoint('PUT', f'/requests/{request_id}/', 
                 data={'status': 'fulfilled'}, description='Update request status')

# Test 8: Donations
print(f"\n{YELLOW}[8] Donation Management{RESET}")
donation = {
    'donation_date': date.today().isoformat(),
    'units': 1,
    'blood_group': 'O+',
    'hospital_name': 'City Hospital',
    'notes': 'Regular donation'
}
test_endpoint('POST', '/donations/', data=donation, expected_status=201,
             description='Record donation')
test_endpoint('GET', '/donations/', description='List user donations')

# Test 9: Notifications
print(f"\n{YELLOW}[9] Notification System{RESET}")
response = test_endpoint('GET', '/notifications/', description='Get notifications')
if response:
    try:
        notifications = response.json().get('notifications', [])
        if notifications:
            notif_id = notifications[0]['id']
            test_endpoint('PUT', f'/notifications/{notif_id}/read/', 
                         description='Mark notification as read')
    except:
        pass
test_endpoint('PUT', '/notifications/read-all/', description='Mark all as read')

# Test 10: Inventory
print(f"\n{YELLOW}[10] Blood Inventory{RESET}")
test_endpoint('GET', '/inventory/', description='Get blood inventory')

# Test 11: Statistics
print(f"\n{YELLOW}[11] Dashboard Statistics{RESET}")
response = test_endpoint('GET', '/stats/', description='Get system statistics')
if response:
    try:
        stats = response.json()
        print(f"  {BLUE}Total Donors: {stats.get('total_donors', 0)}{RESET}")
        print(f"  {BLUE}Available Donors: {stats.get('available_donors', 0)}{RESET}")
        print(f"  {BLUE}Total Requests: {stats.get('total_requests', 0)}{RESET}")
        print(f"  {BLUE}Lives Saved: {stats.get('lives_saved', 0)}{RESET}")
    except:
        pass

# Test 12: Contact Form
print(f"\n{YELLOW}[12] Contact Form{RESET}")
contact_data = {
    'name': 'Test User',
    'email': 'test@example.com',
    'subject': 'Test Message',
    'message': 'This is a test message'
}
test_endpoint('POST', '/contact/', data=contact_data, expected_status=201,
             description='Submit contact message')

# Test 13: Logout
print(f"\n{YELLOW}[13] User Logout{RESET}")
test_endpoint('POST', '/logout/', description='Logout user')
response = test_endpoint('GET', '/auth/check/', description='Verify logged out')
if response:
    try:
        if not response.json().get('authenticated'):
            print_test('User successfully logged out', True)
        else:
            print_test('User successfully logged out', False)
    except:
        pass

# Test 14: Error Handling
print(f"\n{YELLOW}[14] Error Handling{RESET}")
test_endpoint('POST', '/login/', data={'username': 'invalid', 'password': 'wrong'},
             expected_status=401, description='Invalid login credentials')
test_endpoint('GET', '/requests/99999/', expected_status=404,
             description='Non-existent resource')

# Print Summary
print(f"\n{BLUE}{'='*70}{RESET}")
print(f"{BLUE}Test Summary{RESET}")
print(f"{BLUE}{'='*70}{RESET}")
print(f"Total Tests: {test_results['total']}")
print(f"{GREEN}Passed: {test_results['passed']}{RESET}")
print(f"{RED}Failed: {test_results['failed']}{RESET}")

success_rate = (test_results['passed'] / test_results['total'] * 100) if test_results['total'] > 0 else 0
print(f"\nSuccess Rate: {success_rate:.1f}%")

if test_results['failed'] == 0:
    print(f"\n{GREEN}{'='*70}{RESET}")
    print(f"{GREEN}🎉 ALL TESTS PASSED! System is working perfectly!{RESET}")
    print(f"{GREEN}{'='*70}{RESET}\n")
else:
    print(f"\n{YELLOW}{'='*70}{RESET}")
    print(f"{YELLOW}⚠️  Some tests failed. Please review the errors above.{RESET}")
    print(f"{YELLOW}{'='*70}{RESET}\n")
