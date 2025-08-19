#!/usr/bin/env python3
"""
그룹 초대코드 관련 데이터베이스 마이그레이션 스크립트
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트 디렉토리로 경로 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# .env 파일 로드
from dotenv import load_dotenv
load_dotenv(project_root / '.env')

from sqlalchemy import create_engine, text
from app.config.config import DevelopmentConfig
from app.utils.db import Base

def migrate_database():
    """데이터베이스 마이그레이션 실행"""
    
    # 데이터베이스 URL 직접 설정
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        # 기본값 설정
        database_url = "postgresql://neondb_owner:npg_JmHTASslW8B6@ep-summer-frost-a1ojuc9i-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
        print("⚠️ 환경변수 DATABASE_URL이 설정되지 않아 기본값을 사용합니다.")
    
    print(f"데이터베이스 연결 중: {database_url}")
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as connection:
            print("데이터베이스 연결 성공!")
            
            # 1. invitations 테이블에 새로운 필드들 추가
            print("\n1. invitations 테이블에 새로운 필드들 추가 중...")
            
            # is_group_code 필드 추가
            try:
                connection.execute(text("""
                    ALTER TABLE invitations 
                    ADD COLUMN is_group_code BOOLEAN DEFAULT FALSE NOT NULL
                """))
                print("✅ is_group_code 필드 추가 완료")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print("ℹ️ is_group_code 필드가 이미 존재합니다")
                else:
                    print(f"⚠️ is_group_code 필드 추가 중 오류: {e}")
            
            # max_guardians 필드 추가
            try:
                connection.execute(text("""
                    ALTER TABLE invitations 
                    ADD COLUMN max_guardians INTEGER DEFAULT 10
                """))
                print("✅ max_guardians 필드 추가 완료")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print("ℹ️ max_guardians 필드가 이미 존재합니다")
                else:
                    print(f"⚠️ max_guardians 필드 추가 중 오류: {e}")
            
            # current_guardians 필드 추가
            try:
                connection.execute(text("""
                    ALTER TABLE invitations 
                    ADD COLUMN current_guardians INTEGER DEFAULT 0
                """))
                print("✅ current_guardians 필드 추가 완료")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print("ℹ️ current_guardians 필드가 이미 존재합니다")
                else:
                    print(f"⚠️ current_guardians 필드 추가 중 오류: {e}")
            
            # is_active 필드 추가
            try:
                connection.execute(text("""
                    ALTER TABLE invitations 
                    ADD COLUMN is_active BOOLEAN DEFAULT TRUE NOT NULL
                """))
                print("✅ is_active 필드 추가 완료")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print("ℹ️ is_active 필드가 이미 존재합니다")
                else:
                    print(f"⚠️ is_active 필드 추가 중 오류: {e}")
            
            # 2. 기존 데이터 업데이트
            print("\n2. 기존 데이터 업데이트 중...")
            
            # 기존 초대코드들을 개별 초대코드로 설정
            connection.execute(text("""
                UPDATE invitations 
                SET is_group_code = FALSE, is_active = TRUE 
                WHERE is_group_code IS NULL
            """))
            print("✅ 기존 초대코드 데이터 업데이트 완료")
            
            # 3. 변경사항 커밋
            connection.commit()
            print("\n✅ 데이터베이스 마이그레이션 완료!")
            
            # 4. 테이블 구조 확인
            print("\n3. invitations 테이블 구조 확인:")
            result = connection.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'invitations' 
                ORDER BY ordinal_position
            """))
            
            for row in result:
                print(f"  {row[0]}: {row[1]} (NULL: {row[2]}, DEFAULT: {row[3]})")
                
    except Exception as e:
        print(f"❌ 마이그레이션 실패: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 그룹 초대코드 데이터베이스 마이그레이션 시작")
    print("=" * 50)
    
    success = migrate_database()
    
    if success:
        print("\n🎉 마이그레이션이 성공적으로 완료되었습니다!")
        print("이제 그룹 초대코드 기능을 사용할 수 있습니다.")
    else:
        print("\n❌ 마이그레이션이 실패했습니다.")
        print("오류 메시지를 확인하고 다시 시도해주세요.")
