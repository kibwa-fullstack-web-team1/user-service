import os
import logging

class Config(object):
    PHASE = 'default'
    CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
    APP_NAME = 'user-service'
    APP_PREFIX = '/api/v0'
    
    # 환경변수에서 로드
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # 로깅 설정
    LOG_LEVEL = logging.INFO
    LOG_PATH = '/var/log/user-service'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

class ProductionConfig(Config):
    PHASE = 'production'
    LOG_LEVEL = logging.INFO
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True
    PHASE = 'development'
    LOG_LEVEL = logging.DEBUG
    LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')

class TestingConfig(Config):
    TESTING = True
    PHASE = 'testing'
    LOG_LEVEL = logging.DEBUG
    LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    DATABASE_URL = 'sqlite:///test.db'

config_by_name = dict(
    development=DevelopmentConfig,
    test=TestingConfig,
    production=ProductionConfig,
)
