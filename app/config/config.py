import os

class Config:
    PHASE = 'default'
    DATABASE_URL = os.environ.get('DATABASE_URL')

class ProductionConfig(Config):
    PHASE = 'production'

class DevelopmentConfig(Config):
    PHASE = 'development'

config_by_name = dict(
    development=DevelopmentConfig,
    production=ProductionConfig,
)
