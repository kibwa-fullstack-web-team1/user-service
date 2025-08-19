#!/usr/bin/env python3
"""
데이터베이스 마이그레이션 스크립트
새로운 테이블들을 생성하고 기본 데이터를 삽입합니다.
"""

import os
import sys

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.db import init_db, create_tables, drop_tables

def main():
    """메인 함수"""
    print("=== 기억의 정원 데이터베이스 마이그레이션 ===")
    
    while True:
        print("\n선택하세요:")
        print("1. 데이터베이스 초기화 (테이블 생성 + 기본 데이터 삽입)")
        print("2. 테이블만 생성")
        print("3. 모든 테이블 삭제 (주의: 개발 환경에서만)")
        print("4. 종료")
        
        choice = input("\n선택 (1-4): ").strip()
        
        if choice == "1":
            print("\n데이터베이스 초기화를 시작합니다...")
            try:
                init_db()
                print("✅ 데이터베이스 초기화가 완료되었습니다!")
            except Exception as e:
                print(f"❌ 오류 발생: {e}")
                
        elif choice == "2":
            print("\n테이블 생성을 시작합니다...")
            try:
                create_tables()
                print("✅ 테이블 생성이 완료되었습니다!")
            except Exception as e:
                print(f"❌ 오류 발생: {e}")
                
        elif choice == "3":
            confirm = input("\n⚠️  모든 테이블을 삭제하시겠습니까? (yes/no): ").strip().lower()
            if confirm == "yes":
                print("\n테이블 삭제를 시작합니다...")
                try:
                    drop_tables()
                    print("✅ 모든 테이블이 삭제되었습니다!")
                except Exception as e:
                    print(f"❌ 오류 발생: {e}")
            else:
                print("테이블 삭제가 취소되었습니다.")
                
        elif choice == "4":
            print("\n마이그레이션을 종료합니다.")
            break
            
        else:
            print("잘못된 선택입니다. 1-4 중에서 선택해주세요.")

if __name__ == "__main__":
    main()
