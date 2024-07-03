import json
import uuid
from bson import ObjectId
from .models import qr_collection, QRValidator
from django.http import JsonResponse
from auth_functions.verifyAccessTokens import verify_access_token
from .others.extract_form_data import extract_form
from .others.extract_form_data_update import extract_form_update
from common_routes.other_functions.update import get_image_object, update_data, add_new_image
from common_routes.aws.aws_delete import delete_user_images
from datetime import datetime, timezone
###############################################################################################



def index(request):
    return JsonResponse({"message":"App is running"})

def add_new_qr(request):
    if request.method == 'POST':
        token_info = verify_access_token(request)
        if isinstance(token_info, JsonResponse):
            return token_info
        user_id = token_info[0]
        try:
            data = extract_form(request)
            data_dict = data['others']
            logo = data['logo']
            qr = data['qr']
            unique_uuid_qr = str(uuid.uuid4())
            data_dict['user_id'] = user_id
            data_dict['unique_uuid'] = unique_uuid_qr
            
            #! adding timestamps
            # Add createdAt and updatedAt timestamps
            current_time = datetime.now(timezone.utc)
            data_dict['createdAt'] = current_time
            data_dict['updatedAt'] = current_time

            #! validate the data
            QRValidator(**data_dict)

            if logo:
                logo_obj = add_new_image(logo, user_id, unique_uuid_qr, "qr_logo_images")
                data_dict['logo'] = {
                    "logo_id": logo_obj['id'],
                    "logo_url": logo_obj['url']
                }
            else:
                unique_uuid_qr_logo = str(uuid.uuid4())
                data_dict['logo'] = {
                    "logo_id": unique_uuid_qr_logo,
                    "logo_url": ""
                }
            
            if qr:
                company_logo_obj = add_new_image(qr, user_id, unique_uuid_qr, "generated_qr_images") 
                data_dict['qr'] = {
                    "qr_id": company_logo_obj['id'],
                    "qr_url": company_logo_obj['url']
                }
            else:
                unique_uuid_generated_qr = str(uuid.uuid4())
                data_dict['qr'] = {
                    "qr_id": unique_uuid_generated_qr,
                    "qr_url": ""
                }
            
            qr_collection.insert_one(data_dict)
            data_dict['_id'] = str(data_dict['_id'])
            return JsonResponse(data_dict, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500, safe=False)

    else:
        return JsonResponse({"error": "Only POST requests are allowed for this endpoint!"}, status=405)


###############################################################################################

def get_all_qrs(request):
    if request.method == 'GET':
        token_info = verify_access_token(request)
        if isinstance(token_info, JsonResponse):
            return token_info
        user_id = token_info[0]
        try:
            found_qrs = list(qr_collection.find({"user_id": user_id}))
            for qr in found_qrs:
                qr['_id'] = str(qr['_id'])
            return JsonResponse(found_qrs, status=200, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500, safe=False)
    else:
        return JsonResponse({"error": "Only GET requests are allowed for this endpoint!"}, status=405)
    

###############################################################################################

def get_qr_by_id(request, qr_id):
    if request.method == 'GET':
        token_info = verify_access_token(request)
        if isinstance(token_info, JsonResponse):
            return token_info
        user_id = token_info[0]
        try:
            found_qr = qr_collection.find_one({"_id": ObjectId(qr_id)})

            if not found_qr:
                return JsonResponse({"error": "QR not found!"}, status=404, safe=False)
            
            if found_qr['user_id'] != user_id:
                return JsonResponse({"error": "You are not authorized to view this QR!"}, status=403, safe=False)
            
            found_qr['_id'] = str(found_qr['_id'])
            return JsonResponse(found_qr, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500, safe=False)
    else:
        return JsonResponse({"error": "Only GET requests are allowed for this endpoint!"}, status=405)
    

###############################################################################################

def update_qr_by_id(request, qr_id):
    if request.method == 'POST':
        token_info = verify_access_token(request)
        if isinstance(token_info, JsonResponse):
            return token_info
        user_id = token_info[0]
        
        data = extract_form_update(request)
        data_dict = data['others']
        logo = data['logo']
        qr = data['qr']

        existing_qr = qr_collection.find_one({'_id': ObjectId(qr_id)})
        if existing_qr is None:
            return JsonResponse({"error": "QR not found"}, status=404)

        if existing_qr['user_id'] != user_id:
            return JsonResponse({"error": "You do not have permission to update this QR"}, status=403)

        unique_uuid_qr = existing_qr['unique_uuid']
        
        if logo is not None:
            existing_logo_obj = existing_qr.get('logo')
            logo_id = existing_logo_obj['logo_id']
            obj = get_image_object(logo_id, logo, user_id, unique_uuid_qr, "qr_logo_images")
            data_dict['logo'] =  {
                "logo_id": obj['id'],
                "logo_url": obj['url']
            }
        
        if qr is not None:
            existing_qr_obj = existing_qr.get('qr')
            logo_id = existing_qr_obj['logo_id']
            obj = get_image_object(logo_id, qr, user_id, unique_uuid_qr, "generated_qr_images")
            data_dict['qr'] = {
                "qr_id": obj['id'],
                "qr_url": obj['url']
            }
        
        
        updated_qr = update_data(data_dict, existing_qr)
        
        current_time = datetime.now(timezone.utc)
        updated_qr['updatedAt'] = current_time

        try:
            qr_collection.update_one({'_id': ObjectId(qr_id)}, {'$set': updated_qr})
            updated_qr['_id'] = str(updated_qr['_id'])
            return JsonResponse(updated_qr, status=200)
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500, safe=False)
    else:
        return JsonResponse({"error": "Only POST requests are allowed for this endpoint!"}, status=405)
    
###############################################################################################

def delete_qr_by_id(request, unique_uuid):
    if request.method == 'DELETE':
        token_info = verify_access_token(request)
        if isinstance(token_info, JsonResponse):
            return token_info
        user_id = token_info[0]

        try:
            document = qr_collection.find_one({"unique_uuid": unique_uuid})
            if document is None:
                return JsonResponse({"error": "QR document not found"}, status=404)
            
            if document['user_id'] != user_id:
                return JsonResponse({"error": "You do not have permission to delete this QR document"}, status=403)

            # Find the invoice by its ID and delete it
            qr_collection.find_one_and_delete({"unique_uuid": unique_uuid})
            is_deleted_aws_images = delete_user_images(unique_uuid)
            
            return JsonResponse(
                {
                    "message": "QR document successfully deleted!",
                    "is_aws_images_deleted": is_deleted_aws_images
                }, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500, safe=False)
    else:
        return JsonResponse({"error": "Only DELETE requests are allowed for this endpoint!"}, status=405)
