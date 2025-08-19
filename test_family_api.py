#!/usr/bin/env python3
"""
가족 연결 API 테스트 스크립트
초대코드 생성부터 가족 연결까지 전체 플로우를 테스트합니다.
"""

import requests
import json
import time
from datetime import datetime

# API 기본 URL
BASE_URL = "http://localhost:8000"

def test_family_api():
    """가족 연결 API 전체 플로우 테스트"""
    print("=== 🧪 가족 연결 API 테스트 시작 ===")
    
    # 1. 사용자 생성 (시니어)
    print("\n1️⃣ 시니어 사용자 생성...")
    senior_data = {
        "username": "김정원",
        "email": "senior@test.com",
        "phone_number": "010-1234-5678",
        "hashed_password": "senior123",
        "role": "senior"
    }
    
    senior_response = requests.post(f"{BASE_URL}/auth/register", json=senior_data)
    if senior_response.status_code == 200:
        senior_user = senior_response.json()
        print(f"✅ 시니어 생성 성공: {senior_user['username']}")
    else:
        print(f"❌ 시니어 생성 실패: {senior_response.text}")
        return
    
    # 2. 사용자 생성 (보호자)
    print("\n2️⃣ 보호자 사용자 생성...")
    guardian_data = {
        "username": "김민지",
        "email": "guardian@test.com",
        "phone_number": "010-8765-4321",
        "hashed_password": "guardian123",
        "role": "guardian"
    }
    
    guardian_response = requests.post(f"{BASE_URL}/auth/register", json=guardian_data)
    if guardian_response.status_code == 200:
        guardian_user = guardian_response.json()
        print(f"✅ 보호자 생성 성공: {guardian_user['username']}")
    else:
        print(f"❌ 보호자 생성 실패: {guardian_response.text}")
        return
    
    # 3. 시니어 로그인
    print("\n3️⃣ 시니어 로그인...")
    senior_login_data = {
        "email": "senior@test.com",
        "password": "senior123"
    }
    
    senior_login_response = requests.post(f"{BASE_URL}/auth/login", json=senior_login_data)
    if senior_login_response.status_code == 200:
        senior_token = senior_login_response.json()["access_token"]
        print("✅ 시니어 로그인 성공")
    else:
        print(f"❌ 시니어 로그인 실패: {senior_login_response.text}")
        return
    
    # 4. 보호자 로그인
    print("\n4️⃣ 보호자 로그인...")
    guardian_login_data = {
        "email": "guardian@test.com",
        "password": "guardian123"
    }
    
    guardian_login_response = requests.post(f"{BASE_URL}/auth/login", json=guardian_login_data)
    if guardian_login_response.status_code == 200:
        guardian_token = guardian_login_response.json()["access_token"]
        print("✅ 보호자 로그인 성공")
    else:
        print(f"❌ 보호자 로그인 실패: {guardian_login_response.text}")
        return
    
    # 5. 초대코드 생성 (시니어)
    print("\n5️⃣ 초대코드 생성...")
    headers = {"Authorization": f"Bearer {senior_token}"}
    invite_data = {
        "senior_user_id": senior_user["id"],
        "expires_in_hours": 24
    }
    
    invite_response = requests.post(f"{BASE_URL}/family/invite-code", 
                                  json=invite_data, 
                                  headers=headers)
    
    if invite_response.status_code == 200:
        invitation = invite_response.json()["results"]
        invite_code = invitation["invitation_code"]
        print(f"✅ 초대코드 생성 성공: {invite_code}")
    else:
        print(f"❌ 초대코드 생성 실패: {invite_response.text}")
        return
    
    # 6. 초대코드 상태 확인
    print("\n6️⃣ 초대코드 상태 확인...")
    status_response = requests.get(f"{BASE_URL}/family/invite-code/{invite_code}")
    if status_response.status_code == 200:
        status_data = status_response.json()["results"]
        print(f"✅ 초대코드 상태: {status_data['status']}")
        print(f"   시니어: {status_data['senior_name']}")
        print(f"   만료시간: {status_data['expires_at']}")
    else:
        print(f"❌ 초대코드 상태 확인 실패: {status_response.text}")
    
    # 7. 가족 연결 (보호자)
    print("\n7️⃣ 가족 연결...")
    connect_data = {
        "invitation_code": invite_code,
        "guardian_user_id": guardian_user["id"]
    }
    
    connect_response = requests.post(f"{BASE_URL}/family/connect", 
                                   json=connect_data, 
                                   headers={"Authorization": f"Bearer {guardian_token}"})
    
    if connect_response.status_code == 200:
        connect_result = connect_response.json()["results"]
        print(f"✅ 가족 연결 성공!")
        print(f"   시니어: {connect_result['senior_name']}")
        print(f"   관계 ID: {connect_result['relationship_id']}")
    else:
        print(f"❌ 가족 연결 실패: {connect_response.text}")
        return
    
    # 8. 가족 구성원 조회 (보호자)
    print("\n8️⃣ 가족 구성원 조회 (보호자)...")
    members_response = requests.get(f"{BASE_URL}/family/members", 
                                  headers={"Authorization": f"Bearer {guardian_token}"})
    
    if members_response.status_code == 200:
        members = members_response.json()["results"]
        print(f"✅ 보호자 가족 구성원 조회 성공")
        print(f"   돌보는 시니어: {len(members['seniors'])}명")
        for senior in members['seniors']:
            print(f"     - {senior['username']} ({senior['relationship_display_name']})")
    else:
        print(f"❌ 가족 구성원 조회 실패: {members_response.text}")
    
    # 9. 가족 구성원 조회 (시니어)
    print("\n9️⃣ 가족 구성원 조회 (시니어)...")
    senior_members_response = requests.get(f"{BASE_URL}/family/members", 
                                         headers={"Authorization": f"Bearer {senior_token}"})
    
    if senior_members_response.status_code == 200:
        senior_members = senior_members_response.json()["results"]
        print(f"✅ 시니어 가족 구성원 조회 성공")
        print(f"   연결된 보호자: {len(senior_members['guardians'])}명")
        for guardian in senior_members['guardians']:
            print(f"     - {guardian['username']} ({guardian['relationship_display_name']})")
    else:
        print(f"❌ 시니어 가족 구성원 조회 실패: {senior_members_response.text}")
    
    # 10. 초대코드 목록 조회
    print("\n🔟 초대코드 목록 조회...")
    invitations_response = requests.get(f"{BASE_URL}/family/invitations", 
                                      headers={"Authorization": f"Bearer {senior_token}"})
    
    if invitations_response.status_code == 200:
        invitations = invitations_response.json()["results"]
        print(f"✅ 초대코드 목록 조회 성공")
        print(f"   총 초대코드: {invitations['total']}개")
        for invite in invitations['invitations']:
            print(f"     - {invite['code']} ({invite['status']})")
    else:
        print(f"❌ 초대코드 목록 조회 실패: {invitations_response.text}")
    
    print("\n=== 🎉 API 테스트 완료! ===")
    print(f"테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        test_family_api()
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. user-service가 실행 중인지 확인해주세요.")
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
