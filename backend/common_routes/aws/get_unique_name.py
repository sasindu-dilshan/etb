import uuid

def get_unique_name(file_name, user_id, document_id, image_id):
    unique_id = str(uuid.uuid4())
    new_file_name = f"{user_id}_{image_id}_{document_id}_{unique_id}_{file_name}"
    return new_file_name