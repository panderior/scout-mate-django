import os
from datetime import datetime
import uuid
from scout_mate.settings import BASE_DIR

def saveFile(uploaded_file):
    current_time = datetime.now().strftime('%Y%m%d%H%M%S')
    file_path = os.path.join(BASE_DIR, 'users_data', f"{current_time}_{uploaded_file.name}")
    with open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    return file_path

def generate_unique_token():
    # Generate a UUID
    unique_id = uuid.uuid4()
    current_time = datetime.now().strftime('%Y%m%d%H%M%S')
    # Combine UUID and current time to create a unique token
    unique_token = f"{unique_id}-{current_time}"
    return unique_token