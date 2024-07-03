import os
import uuid
from bson import ObjectId
from pydantic import ValidationError 
from .models import salaryslip_collection
from django.http import JsonResponse
from auth_functions.verifyAccessTokens import verify_access_token
from .models import SalarySlipValidator
from rest_framework import status
from .others.extract_form_data import extract_form_salary_slip
from common_routes.aws.aws_delete import delete_user_images
from common_routes.other_functions.update import add_new_image,update_data, get_image_object
from .others.extract_form_update import extract_form__update_salary_slip
from datetime import datetime, timezone
####################################################################
accessTokenSecret = os.environ.get("ACCESS_TOKEN_SECRET")
####################################################################


####################################################################
def index(request):
    return JsonResponse({"message":"App is running"})


""" 
add a new salary slip to the database
complete end point: http://localhost:8000/api/salarySlip/add/
"""
def add_salaryslip(request):
    if request.method == 'POST':
        token_info = verify_access_token(request)
        if isinstance(token_info, JsonResponse):
            return token_info
        user_id = token_info[0]
        
        # Retrieve the POST data from the request
        data = extract_form_salary_slip(request)

        data_dict = data['others']
        companyLogo = data['companyLogo']
        signature = data['signature']
        slipImage = data['slipImage']
        unique_uuid_salary_slip = str(uuid.uuid4())


        if signature:
            signature_obj = add_new_image(signature, user_id, unique_uuid_salary_slip, "salaryslip_signature")
            data_dict['signature'] = {
                "signature_id": signature_obj['id'],
                "signature_url": signature_obj['url']
            }
        else:
            unique_uuid_salaryslip_signature = str(uuid.uuid4())
            data_dict['signature'] = {
                "signature_id": unique_uuid_salaryslip_signature,
                "signature_url": ""
            }
        
        if companyLogo:
            company_logo_obj = add_new_image(companyLogo, user_id, unique_uuid_salary_slip, "salaryslip_company_logo") 
            data_dict['companyLogo'] = {
                "logo_id": company_logo_obj['id'],
                "logo_url": company_logo_obj['url']
            }
        else:
            unique_uuid_salaryslip_logo = str(uuid.uuid4())
            data_dict['companyLogo'] = {
                "logo_id": unique_uuid_salaryslip_logo,
                "logo_url": ""
            }
        
        if slipImage:
            slip_image_obj = add_new_image(slipImage, user_id, unique_uuid_salary_slip, "salaryslip_image")
            data_dict['slipImage'] = {
                "slip_image_id": slip_image_obj['id'],
                "slip_image_url": slip_image_obj['url']
            }
        else:
            unique_uuid_salaryslip_image = str(uuid.uuid4())
            data_dict['slipImage'] = {
                "slip_image_id": unique_uuid_salaryslip_image,
                "slip_image_url": ""
            }

        data_dict['user_id'] = user_id
        data_dict['unique_uuid'] =  unique_uuid_salary_slip
        
        # validate the incoming data
        try:
            SalarySlipValidator(**data_dict)
        except ValidationError as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY, safe=False)
        
        # Add createdAt and updatedAt timestamps
        current_time = datetime.now(timezone.utc)  # Use timezone-aware object
        data_dict['createdAt'] = current_time
        data_dict['updatedAt'] = current_time
        

        # Insert the received data into the database
        try:
            salaryslip_collection.insert_one(data_dict)
            data_dict['_id'] = str(data_dict['_id'])
            return JsonResponse(data_dict, status=200, safe=False)
        except Exception as e:
            error_message = "An error occurred during the salary slip adding process."
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            if isinstance(e, JsonResponse):
                error_message = e.content.decode('utf-8')
                status_code = e.status_code 
            
            # Return the error message as a JsonResponse
            return JsonResponse({"error": error_message}, status=status_code, safe=False)
    else:
        return JsonResponse({"error": "Only POST requests are allowed for this endpoint!"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)




"""
get all salary slips in the database
complete end point: http://localhost:8000/api/salarySlip/getAll
"""
def get_all_salaryslips(request):
    if request.method == 'GET':
        token_info = verify_access_token(request)
        if isinstance(token_info, JsonResponse):
            return token_info
        user_id = token_info[0]
        
        try:
            # send invoices user owned
            salary_slips = list(salaryslip_collection.find({"user_id":user_id}))
            if not salary_slips:
                return JsonResponse({"message":"No salary slips found for this user!"}, status=status.HTTP_404_NOT_FOUND)

            # Convert ObjectId to str for JSON serialization
            for slip in salary_slips:
                slip['_id'] = str(slip['_id'])

            return JsonResponse({"salary_slips": salary_slips}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500, safe=False)
    else:
        return JsonResponse({"error": "Only GET requests are allowed for this endpoint!"}, status=405)
    

def get_one_salary_slip(request,salary_slip_id):
    if request.method == 'GET':
        token_info = verify_access_token(request)
        if isinstance(token_info, JsonResponse):
            return token_info
        user_id = token_info[0]
        
        try:
            # send invoices user owned
            found_salary_slip = salaryslip_collection.find_one({"_id":ObjectId(salary_slip_id)})
            if not found_salary_slip:
                return JsonResponse({"error":"No salary slip found with given ID"}, status=status.HTTP_404_NOT_FOUND)
            
            if found_salary_slip['user_id'] != user_id:
                return JsonResponse({"error": "You do not have permission to perform this action"}, status=403)

            # Convert ObjectId to str for JSON serialization
            found_salary_slip['_id'] = str(found_salary_slip['_id'])

            return JsonResponse(found_salary_slip, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500, safe=False)
    else:
        return JsonResponse({"error": "Only GET requests are allowed for this endpoint!"}, status=405)

""" 
delete existing salary slips in the database using Salary slip ID(_id attribute in MongoDB)
complete end point: http://localhost:8000/api/salarySlip/delete/65e262f1e7238f1f11f7bb8f
"""
def delete_salaryslip(request, unique_uuid):
    if request.method == 'DELETE':
        token_info = verify_access_token(request)
        if isinstance(token_info, JsonResponse):
            return token_info
        user_id = token_info[0]
        try:
            document = salaryslip_collection.find_one({"unique_uuid": unique_uuid})
            if not document:
                return JsonResponse({"error": "Salary slip not found"}, status=status.HTTP_404_NOT_FOUND)
            
            if document['user_id'] != user_id:
                return JsonResponse({"error": "You do not have permission to perform this action"}, status=403)

            # Find the invoice by its ID and delete it
            salaryslip_collection.find_one_and_delete({"unique_uuid": unique_uuid})
            is_deleted_aws_images = delete_user_images(unique_uuid)
            
            return JsonResponse(
                {
                    "message": "Salary Slip successfully deleted!",
                    "is_aws_images_deleted": is_deleted_aws_images
                }, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500, safe=False)
    else:
        return JsonResponse({"error": "Only DELETE requests are allowed for this endpoint!"}, status=405)



""" 
update salary slip endpoint
complete end point: http://localhost:8000/api/salarySlip/update/65e262f1e7238f1f11f7bb8f
"""
def update_salaryslip(request, salary_slip_id):
    if request.method == 'POST':
        token_info = verify_access_token(request)
        if isinstance(token_info, JsonResponse):
            return token_info
        user_id = token_info[0]
        
        data = extract_form__update_salary_slip(request)

        data_dict = data['others']
        companyLogo = data['companyLogo']
        signature = data['signature']

        # Retrieve existing invoice data from the database
        existing_salaryslip = salaryslip_collection.find_one({'_id': ObjectId(salary_slip_id)})

        if existing_salaryslip is None:
            return JsonResponse({"error": "Salary slip not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if existing_salaryslip['user_id'] != user_id:
            return JsonResponse({"error": "You do not have permission to perform this action"}, status=403)
        
        unique_uuid_salary_slip = existing_salaryslip['unique_uuid']

        if signature is not None:
            existing_signature_obj = existing_salaryslip.get('signature')
            signature_id = existing_signature_obj['signature_id']
            obj = get_image_object(signature_id, signature, user_id, unique_uuid_salary_slip, "salaryslip_signature")
            data_dict['signature'] =  {
                "signature_id": obj['id'],
                "signature_url": obj['url']
            }
        
        if companyLogo is not None:
            existing_companyLogo_obj = existing_salaryslip.get('companyLogo')
            logo_id = existing_companyLogo_obj['logo_id']
            obj = get_image_object(logo_id, companyLogo, user_id, unique_uuid_salary_slip, "salaryslip_companyLogo")
            data_dict['companyLogo'] = {
                "logo_id": obj['id'],
                "logo_url": obj['url']
            }

        # Applying the patch updates
        updated_salary_slip = update_data(data_dict, existing_salaryslip)

        current_time = datetime.now(timezone.utc)  # Use timezone-aware object
        updated_salary_slip['updatedAt'] = current_time

        # Update the existing invoice in the database
        try:
            # Update the existing invoice based on the provided invoice_id
            salaryslip_collection.update_one({'_id': ObjectId(salary_slip_id)}, {'$set': updated_salary_slip})
            updated_salary_slip['_id'] = str(updated_salary_slip['_id'])
            return JsonResponse(updated_salary_slip, status=200, safe=False)
            
        except Exception as e:
            error_message = "An error occurred during the update process."
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
            if isinstance(e, JsonResponse):
                error_message = e.content.decode('utf-8')
                status_code = e.status_code
            
            # Return the error message as a JsonResponse
            return JsonResponse({"error": error_message}, status=status_code)
    else:
        return JsonResponse({"error": "Only POST requests are allowed for this endpoint!"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)





        