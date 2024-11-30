import base64
import os
import sys

# Root directory를 Project Root로 설정
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(project_root)
os.chdir(project_root)

from core.config import settings

encoded_secret_key = base64.urlsafe_b64encode(settings.SECRET_KEY.encode()).decode()
print(encoded_secret_key)