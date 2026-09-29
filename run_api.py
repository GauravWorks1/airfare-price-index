import uvicorn
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from api.main import app
import config

if __name__ == '__main__':
    uvicorn.run(
        "api.main:app",
        host=getattr(config, 'API_HOST', '0.0.0.0'),
        port=getattr(config, 'API_PORT', 8000),
        reload=False
    )
