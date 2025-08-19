#!/usr/bin/env python3
"""
기존 invitations 테이블 상세 구조 확인
새로운 기능 구현을 위한 정확한 테이블 구조 파악
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def check_invitations_structure():
    """invitations 테이블 상세 구조 확인"""
    print("=== 🔍 기존 invitations 테이블 상세 구조 확인 ===")
    
    # Neon PostgreSQL 연결 정보
    db_url = "postgresql://neondb_owner:npg_JmHTASslW8B6@ep-summer-frost-a1ojuc9i-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ 데이터베이스 연결 성공!")
        
        # 1. invitations 테이블 상세 구조
        print("\n1️⃣ invitations 테이블 상세 구조...")
        cursor.execute("""
            SELECT 
                column_name, 
                data_type, 
                is_nullable, 
                column_default,
                character_maximum_length,
                numeric_precision,
                numeric_scale
            FROM information_schema.columns 
            WHERE table_name = 'invitations'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        if columns:
            print("📋 invitations 테이블 컬럼 상세:")
            for col in columns:
                nullable = "NULL 허용" if col['is_nullable'] == 'YES' else "NULL 불허"
                default = f"기본값: {col['column_default']}" if col['column_default'] else "기본값 없음"
                
                if col['character_maximum_length']:
                    data_type = f"{col['data_type']}({col['character_maximum_length']})"
                elif col['numeric_precision']:
                    data_type = f"{col['data_type']}({col['numeric_precision']},{col['numeric_scale']})"
                else:
                    data_type = col['data_type']
                
                print(f"  - {col['column_name']}: {data_type} ({nullable}) {default}")
        else:
            print("  ❌ invitations 테이블이 없습니다.")
        
        # 2. relationship_types 테이블 데이터 확인
        print("\n2️⃣ relationship_types 테이블 데이터...")
        cursor.execute("SELECT * FROM relationship_types ORDER BY id")
        types = cursor.fetchall()
        if types:
            print("🏷️ 관계 유형 목록:")
            for rel_type in types:
                print(f"  - ID: {rel_type['id']}, 이름: {rel_type['name']}, 한국어: {rel_type['display_name_ko']}")
        else:
            print("  관계 유형 데이터가 없습니다.")
        
        # 3. users 테이블 역할별 분포
        print("\n3️⃣ 사용자 역할별 분포...")
        cursor.execute("""
            SELECT role, COUNT(*) as count 
            FROM users 
            GROUP BY role 
            ORDER BY role
        """)
        roles = cursor.fetchall()
        if roles:
            print("👥 사용자 역할별 분포:")
            for role in roles:
                print(f"  - {role['role']}: {role['count']}명")
        else:
            print("  사용자 데이터가 없습니다.")
        
        # 4. family_relationships 테이블 샘플
        print("\n4️⃣ 기존 가족 관계 샘플...")
        cursor.execute("""
            SELECT 
                fr.id,
                fr.senior_id,
                fr.guardian_id,
                fr.relationship_type_id,
                fr.created_at,
                s.username as senior_name,
                g.username as guardian_name,
                rt.display_name_ko as relationship_name
            FROM family_relationships fr
            JOIN users s ON fr.senior_id = s.id
            JOIN users g ON fr.guardian_id = g.id
            LEFT JOIN relationship_types rt ON fr.relationship_type_id = rt.id
            LIMIT 5
        """)
        relationships = cursor.fetchall()
        if relationships:
            print("👨‍👩‍👧‍👦 기존 가족 관계:")
            for rel in relationships:
                print(f"  - 시니어: {rel['senior_name']} (ID: {rel['senior_id']})")
                print(f"    보호자: {rel['guardian_name']} (ID: {rel['guardian_id']})")
                print(f"    관계: {rel['relationship_name'] or '미정'} (생성: {rel['created_at']})")
                print()
        else:
            print("  가족 관계 데이터가 없습니다.")
        
        # 5. invitations 테이블 샘플 (현재는 비어있음)
        print("\n5️⃣ invitations 테이블 샘플...")
        cursor.execute("SELECT * FROM invitations LIMIT 3")
        invitations = cursor.fetchall()
        if invitations:
            print("📨 기존 초대 데이터:")
            for inv in invitations:
                print(f"  - 코드: {inv['code']}, 초대자: {inv['inviter_id']}, 상태: {inv['is_used']}")
        else:
            print("  초대 데이터가 없습니다. (새로 생성할 예정)")
        
        cursor.close()
        conn.close()
        
        print("\n=== 📊 테이블 구조 확인 완료 ===")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def main():
    """메인 함수"""
    print("기억의 정원 - 기존 테이블 구조 상세 분석")
    print("=" * 60)
    
    check_invitations_structure()

if __name__ == "__main__":
    main()
