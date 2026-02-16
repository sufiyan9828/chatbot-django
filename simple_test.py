#!/usr/bin/env python3
import requests
import json

def test_chatbot():
    base_url = 'http://127.0.0.1:8000/api/webhook/'
    
    test_cases = [
        'hello',
        'contact', 
        'services',
        'hours',
        'location',
        'human',
        'menu',
        'help',
        'thanks',
        'bye'
    ]
    
    print('Testing chatbot API...')
    passed = 0
    failed = 0
    
    for i, message in enumerate(test_cases, 1):
        try:
            response = requests.post(base_url, json={
                'message': message,
                'platform': 'test',
                'user_id': f'test_user_{i}'
            })
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', 'No response')
                print(f'{i}. {message}: SUCCESS - {response_text[:50]}...')
                passed += 1
            else:
                print(f'{i}. {message}: FAILED - HTTP {response.status_code}')
                failed += 1
        except Exception as e:
            print(f'{i}. {message}: ERROR - {e}')
            failed += 1
    
    print(f'\nResults: {passed} passed, {failed} failed')
    success_rate = (passed / len(test_cases)) * 100
    print(f'Success rate: {success_rate:.1f}%')
    
    if success_rate >= 90:
        print('CHATBOT IS READY FOR LAUNCH!')
    else:
        print('CHATBOT NEEDS IMPROVEMENT')
    
    return success_rate

if __name__ == '__main__':
    test_chatbot()
