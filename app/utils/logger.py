import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    """로깅 설정 초기화"""
    # 로그 디렉토리 생성
    log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(log_path, exist_ok=True)
    
    # 로그 레벨 설정 (기본값: INFO)
    log_level = logging.INFO
    
    # 로그 포맷 설정
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    
    # 파일 핸들러 설정
    file_handler = RotatingFileHandler(
        os.path.join(log_path, 'user-service.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    
    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 기존 핸들러 제거 (중복 방지)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logging.info("User Service Logger initialized")
