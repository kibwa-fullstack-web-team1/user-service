#!/usr/bin/env python3
"""
간단한 데이터베이스 연결 테스트
복잡한 모델 로딩 없이 DB 상태를 확인합니다.
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_config():
    """데이터베이스 설정 가져오기"""
    # 환경변수에서 설정 가져오기
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'user_service')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'password')
    
    return {
        'host': db_host,
        'port': db_port,
        'database': db_name,
        'user': db_user,
        'password': db_password
    }

def check_database_simple():
    """간단한 데이터베이스 상태 확인"""
    print("=== 🔍 간단한 데이터베이스 상태 확인 ===")
    
    try:
        # 데이터베이스 연결
        config = get_db_config()
        print(f"📡 데이터베이스 연결 시도: {config['host']}:{config['port']}/{config['database']}")
        
        conn = psycopg2.connect(**config)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ 데이터베이스 연결 성공!")
        
        # 1. 테이블 목록 조회
        print("\n1️⃣ 테이블 목록 확인...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        if tables:
            print("📋 존재하는 테이블들:")
            for table in tables:
                print(f"  - {table['table_name']}")
        else:
            print("  ❌ 테이블이 없습니다.")
        
        # 2. 주요 테이블의 컬럼 구조 확인
        print("\n2️⃣ 주요 테이블 구조 확인...")
        
        # users 테이블
        try:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'users'
                ORDER BY ordinal_position
            """)
            users_columns = cursor.fetchall()
            if users_columns:
                print("👥 users 테이블 구조:")
                for col in users_columns:
                    print(f"  - {col['column_name']}: {col['data_type']} (NULL: {col['is_nullable']})")
            else:
                print("  ❌ users 테이블이 없습니다.")
        except Exception as e:
            print(f"  ❌ users 테이블 조회 오류: {e}")
        
        # family_relationships 테이블
        try:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'family_relationships'
                ORDER BY ordinal_position
            """)
            rel_columns = cursor.fetchall()
            if rel_columns:
                print("👨‍👩‍👧‍👦 family_relationships 테이블 구조:")
                for col in rel_columns:
                    print(f"  - {col['column_name']}: {col['data_type']} (NULL: {col['is_nullable']})")
            else:
                print("  ❌ family_relationships 테이블이 없습니다.")
        except Exception as e:
            print(f"  ❌ family_relationships 테이블 조회 오류: {e}")
        
        # invitations 테이블
        try:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'invitations'
                ORDER BY ordinal_position
            """)
            inv_columns = cursor.fetchall()
            if inv_columns:
                print("📨 invitations 테이블 구조:")
                for col in inv_columns:
                    print(f"  - {col['column_name']}: {col['data_type']} (NULL: {col['is_nullable']})")
            else:
                print("  ❌ invitations 테이블이 없습니다.")
        except Exception as e:
            print(f"  ❌ invitations 테이블 조회 오류: {e}")
        
        # 3. 데이터 개수 확인
        print("\n3️⃣ 데이터 개수 확인...")
        
        for table_name in ['users', 'family_relationships', 'invitations', 'relationship_types']:
            try:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                result = cursor.fetchone()
                if result:
                    print(f"  📊 {table_name}: {result['count']}개")
                else:
                    print(f"  ❌ {table_name}: 조회 실패")
            except Exception as e:
                print(f"  ❌ {table_name}: {e}")
        
        # 4. 샘플 데이터 확인
        print("\n4️⃣ 샘플 데이터 확인...")
        
        try:
            cursor.execute("SELECT * FROM users LIMIT 3")
            users = cursor.fetchall()
            if users:
                print("👥 사용자 샘플:")
                for user in users:
                    print(f"  - ID: {user['id']}, 이름: {user.get('username', 'N/A')}, 역할: {user.get('role', 'N/A')}")
            else:
                print("  사용자 데이터가 없습니다.")
        except Exception as e:
            print(f"  사용자 데이터 조회 오류: {e}")
        
        cursor.close()
        conn.close()
        
        print("\n=== 📊 데이터베이스 상태 확인 완료 ===")
        
    except psycopg2.OperationalError as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        print("\n💡 해결 방법:")
        print("1. 데이터베이스가 실행 중인지 확인")
        print("2. 환경변수 설정 확인 (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)")
        print("3. docker-compose로 서비스 시작")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def main():
    """메인 함수"""
    print("기억의 정원 - 데이터베이스 상태 확인")
    print("=" * 50)
    
    check_database_simple()

if __name__ == "__main__":
    main()
