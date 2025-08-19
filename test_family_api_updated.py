#!/usr/bin/env python3
"""
가족 연결 API 테스트 스크립트 (기존 테이블 구조 활용)
초대코드 생성부터 가족 연결까지 전체 플로우를 테스트합니다.
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_family_api():
    """가족 연결 API 테스트"""
    print("=== 🧪 가족 연결 API 테스트 시작 (기존 테이블 구조 활용) ===")
    
    # 1. 초대코드 생성 (시니어 역할)
    print("\n1️⃣ 초대코드 생성 테스트...")
    headers = {"X-User-ID": "1"}  # 이미자 (시니어)
    
    invite_data = {
        "invitee_email": "test@example.com",
        "relationship_type_id": 5  # 보호자
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/family/invite-code",
            json=invite_data,
            headers=headers
        )
        
        if response.status_code == 200:
            invitation = response.json()
            print(f"✅ 초대코드 생성 성공!")
            print(f"  - 코드: {invitation['code']}")
            print(f"  - 만료시간: {invitation['expires_at']}")
            print(f"  - 생성시간: {invitation['created_at']}")
            
            # 생성된 코드 저장
            generated_code = invitation['code']
        else:
            print(f"❌ 초대코드 생성 실패: {response.status_code}")
            print(f"  응답: {response.text}")
            return
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
        return
    
    # 2. 초대코드 상태 확인
    print("\n2️⃣ 초대코드 상태 확인 테스트...")
    try:
        response = requests.get(f"{BASE_URL}/family/invite-code/{generated_code}")
        
        if response.status_code == 200:
            status_info = response.json()
            print(f"✅ 초대코드 상태 확인 성공!")
            print(f"  - 코드: {status_info['code']}")
            print(f"  - 유효성: {status_info['is_valid']}")
            print(f"  - 사용여부: {status_info['is_used']}")
            print(f"  - 초대자: {status_info['inviter_name']}")
            print(f"  - 관계유형: {status_info['relationship_type']}")
        else:
            print(f"❌ 초대코드 상태 확인 실패: {response.status_code}")
            print(f"  응답: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
    
    # 3. 가족 연결 (보호자 역할)
    print("\n3️⃣ 가족 연결 테스트...")
    headers = {"X-User-ID": "7"}  # testuser (보호자)
    
    connect_data = {
        "code": generated_code,
        "relationship_type_id": 5  # 보호자
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/family/connect",
            json=connect_data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✅ 가족 연결 성공!")
                print(f"  - 메시지: {result['message']}")
                print(f"  - 관계ID: {result['family_relationship_id']}")
            else:
                print(f"❌ 가족 연결 실패: {result['message']}")
        else:
            print(f"❌ 가족 연결 요청 실패: {response.status_code}")
            print(f"  응답: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
    
    # 4. 가족 구성원 조회 (보호자 입장)
    print("\n4️⃣ 가족 구성원 조회 테스트 (보호자 입장)...")
    headers = {"X-User-ID": "7"}  # testuser (보호자)
    
    try:
        response = requests.get(f"{BASE_URL}/family/members", headers=headers)
        
        if response.status_code == 200:
            members = response.json()
            print(f"✅ 가족 구성원 조회 성공!")
            print(f"  - 돌보는 시니어: {len(members['seniors'])}명")
            print(f"  - 보호자: {len(members['guardians'])}명")
            
            for senior in members['seniors']:
                print(f"    - 시니어: {senior['full_name'] or senior['username']} (관계: {senior['relationship_type']})")
        else:
            print(f"❌ 가족 구성원 조회 실패: {response.status_code}")
            print(f"  응답: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
    
    # 5. 가족 구성원 조회 (시니어 입장)
    print("\n5️⃣ 가족 구성원 조회 테스트 (시니어 입장)...")
    headers = {"X-User-ID": "1"}  # 이미자 (시니어)
    
    try:
        response = requests.get(f"{BASE_URL}/family/members", headers=headers)
        
        if response.status_code == 200:
            members = response.json()
            print(f"✅ 가족 구성원 조회 성공!")
            print(f"  - 돌보는 시니어: {len(members['seniors'])}명")
            print(f"  - 보호자: {len(members['guardians'])}명")
            
            for guardian in members['guardians']:
                print(f"    - 보호자: {guardian['full_name'] or guardian['username']} (관계: {guardian['relationship_type']})")
        else:
            print(f"❌ 가족 구성원 조회 실패: {response.status_code}")
            print(f"  응답: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
    
    # 6. 초대코드 목록 조회
    print("\n6️⃣ 초대코드 목록 조회 테스트...")
    headers = {"X-User-ID": "1"}  # 이미자 (시니어)
    
    try:
        response = requests.get(f"{BASE_URL}/family/invitations", headers=headers)
        
        if response.status_code == 200:
            invitations = response.json()
            print(f"✅ 초대코드 목록 조회 성공!")
            print(f"  - 총 개수: {invitations['total_count']}개")
            
            for inv in invitations['invitations']:
                print(f"    - 코드: {inv['code']}, 상태: {'사용됨' if inv['is_used'] else '대기중'}")
        else:
            print(f"❌ 초대코드 목록 조회 실패: {response.status_code}")
            print(f"  응답: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패: {e}")
    
    print("\n=== 🎉 API 테스트 완료! ===")
    print(f"테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        test_family_api()
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. user-service가 실행 중인지 확인해주세요.")
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
