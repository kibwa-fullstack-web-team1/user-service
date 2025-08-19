#!/usr/bin/env python3
"""
기존 데이터베이스 상태 확인 스크립트
현재 어떤 테이블과 데이터가 있는지 확인합니다.
"""

import os
import sys

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.db import SessionLocal
from app.models import user as user_model

def check_database_status():
    """데이터베이스 상태 확인"""
    print("=== 🔍 기존 데이터베이스 상태 확인 ===")
    
    db = SessionLocal()
    try:
        # 1. 테이블 존재 여부 확인
        print("\n1️⃣ 테이블 존재 여부 확인...")
        
        # users 테이블
        try:
            user_count = db.query(user_model.User).count()
            print(f"✅ users 테이블: {user_count}개 사용자")
        except Exception as e:
            print(f"❌ users 테이블 오류: {e}")
        
        # family_relationships 테이블
        try:
            relationship_count = db.query(user_model.FamilyRelationship).count()
            print(f"✅ family_relationships 테이블: {relationship_count}개 관계")
        except Exception as e:
            print(f"❌ family_relationships 테이블 오류: {e}")
        
        # invitation_codes 테이블
        try:
            invitation_count = db.query(user_model.InvitationCode).count()
            print(f"✅ invitation_codes 테이블: {invitation_count}개 초대코드")
        except Exception as e:
            print(f"❌ invitation_codes 테이블 오류: {e}")
        
        # relationship_types 테이블
        try:
            type_count = db.query(user_model.RelationshipType).count()
            print(f"✅ relationship_types 테이블: {type_count}개 관계 유형")
        except Exception as e:
            print(f"❌ relationship_types 테이블 오류: {e}")
        
        # 2. 기존 사용자 데이터 확인
        print("\n2️⃣ 기존 사용자 데이터 확인...")
        try:
            users = db.query(user_model.User).limit(5).all()
            if users:
                print("기존 사용자 목록:")
                for user in users:
                    print(f"  - ID: {user.id}, 이름: {user.username}, 역할: {user.role}, 이메일: {user.email}")
            else:
                print("  기존 사용자가 없습니다.")
        except Exception as e:
            print(f"  사용자 조회 오류: {e}")
        
        # 3. 기존 가족 관계 확인
        print("\n3️⃣ 기존 가족 관계 확인...")
        try:
            relationships = db.query(user_model.FamilyRelationship).limit(5).all()
            if relationships:
                print("기존 가족 관계:")
                for rel in relationships:
                    print(f"  - 시니어 ID: {rel.senior_id}, 보호자 ID: {rel.guardian_id}")
            else:
                print("  기존 가족 관계가 없습니다.")
        except Exception as e:
            print(f"  가족 관계 조회 오류: {e}")
        
        # 4. 데이터베이스 연결 상태
        print("\n4️⃣ 데이터베이스 연결 상태...")
        try:
            # 간단한 쿼리로 연결 테스트
            result = db.execute("SELECT 1").fetchone()
            if result:
                print("✅ 데이터베이스 연결 성공")
            else:
                print("❌ 데이터베이스 연결 실패")
        except Exception as e:
            print(f"❌ 데이터베이스 연결 오류: {e}")
        
        print("\n=== 📊 데이터베이스 상태 확인 완료 ===")
        
    except Exception as e:
        print(f"❌ 데이터베이스 상태 확인 중 오류 발생: {e}")
    finally:
        db.close()

def create_missing_tables():
    """누락된 테이블만 생성"""
    print("\n=== 🔧 누락된 테이블 생성 ===")
    
    from app.utils.db import create_tables
    
    try:
        create_tables()
        print("✅ 누락된 테이블 생성 완료")
    except Exception as e:
        print(f"❌ 테이블 생성 오류: {e}")

def main():
    """메인 함수"""
    while True:
        print("\n선택하세요:")
        print("1. 데이터베이스 상태 확인")
        print("2. 누락된 테이블만 생성")
        print("3. 종료")
        
        choice = input("\n선택 (1-3): ").strip()
        
        if choice == "1":
            check_database_status()
        elif choice == "2":
            create_missing_tables()
        elif choice == "3":
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 선택입니다. 1-3 중에서 선택해주세요.")

if __name__ == "__main__":
    main()
