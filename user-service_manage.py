from app import create_app
import os

import uvicorn

config_name = os.getenv('PHASE') or 'development'
app = create_app(config_name)

if __name__ == '__main__':
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=8000,
    )