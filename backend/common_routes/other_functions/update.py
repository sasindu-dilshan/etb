from common_routes.aws.aws_delete import delete_user_images
from common_routes.aws.get_unique_name import get_unique_name
from common_routes.aws.aws_upload import upload_to_aws
from django.conf import settings
import uuid

# this function used in updating invoice
def update_data(data_dict, existing_invoice):
    for dd_key, dd_value in data_dict.items():
        if isinstance(dd_value, dict):
            for dd_v_key,dd_v_v in dd_value.items():
                for ei_key, ei_v in existing_invoice.items():
                    if isinstance(ei_v, dict):
                        for ei_v_key, ei_v_v in ei_v.items():
                            if (ei_v_key == dd_v_key):
                                ei_v[ei_v_key] = dd_v_v
        
        elif isinstance(dd_value, list):
            if len(dd_value) != 0:
                existing_invoice[dd_key] = dd_value
        else:
            if dd_value is not None:
                existing_invoice[dd_key] = dd_value
    return existing_invoice

        

# this function used in updating invoice
def get_image_object(id, file, user_id, unique_uuid_doc, folder_name):
    is_deleted_aws_images = delete_user_images(id)
    unique_name_for_file = get_unique_name(file.name, user_id, unique_uuid_doc, id)
    file_url = upload_to_aws(file, settings.AWS_BUCKET, unique_name_for_file, folder_name)
    new_obj = {
        "url": file_url,
        "id": id
        }
    return new_obj

# add new image to aws cloud and get the url
def add_new_image(file, user_id, unique_uuid_doc, folder_name):
    unique_uuid_image = str(uuid.uuid4())
    unique_name_for_signature = get_unique_name(file.name, user_id, unique_uuid_doc, unique_uuid_image)
    image_url = upload_to_aws(file, settings.AWS_BUCKET, unique_name_for_signature, folder_name)

    obj = {
        "id": unique_uuid_image,
        "url": image_url
    }

    return obj