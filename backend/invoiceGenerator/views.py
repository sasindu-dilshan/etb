import os
import uuid
from bson import ObjectId
from pydantic import ValidationError 
from .models import invoice_collection
from django.http import JsonResponse
from auth_functions.verifyAccessTokens import verify_access_token
from .models import InvoiceValidator
from common_routes.aws.aws_delete import delete_user_images
from .others.extract_form_data import extract_form
from.others.extract_form_data_update import extract_form_update
from common_routes.other_functions.update import get_image_object, update_data, add_new_image
from datetime import datetime, timezone
from rest_framework import status
####################################################################



####################################################################
def index(request):
    return JsonResponse({"message":"invoice end points are live"})


""" 
add a new invoice to the database
complete end point: http://localhost:8000/api/invoice/add/
"""
def add_invoice(request):
    if request.method == 'POST':
        # Retrieve user_id from access token
        token_info = verify_access_token(request)
        
        if isinstance(token_info, JsonResponse):
            return token_info  # Return the error response
    
        user_id = token_info[0]
        data = extract_form(request)

        data_dict = data['others']
        companyLogo = data['companyLogo']
        signature = data['signature']
        invoiceImage = data['invoiceImage']
        unique_uuid_invoice = str(uuid.uuid4())

        if signature:
            signature_obj = add_new_image(signature, user_id, unique_uuid_invoice, "invoice_signature")
            data_dict['signature'] = {
                "signature_id": signature_obj['id'],
                "signature_url": signature_obj['url']
            }
        else:
            unique_uuid_invoice_signature = str(uuid.uuid4())
            data_dict['signature'] = {
                "signature_id": unique_uuid_invoice_signature,
                "signature_url": ""
            }
        
        if companyLogo:
            company_logo_obj = add_new_image(companyLogo, user_id, unique_uuid_invoice, "invoice_company_logo") 
            data_dict['companyLogo'] = {
                "logo_id": company_logo_obj['id'],
                "logo_url": company_logo_obj['url']
            }
        else:
            unique_uuid_invoice_logo = str(uuid.uuid4())
            data_dict['companyLogo'] = {
                "logo_id": unique_uuid_invoice_logo,
                "logo_url": ""
            }
        
        if invoiceImage:
            invoice_image_obj = add_new_image(invoiceImage, user_id, unique_uuid_invoice, "invoice_image")
            data_dict['invoiceImage'] = {
                "invoice_img_id": invoice_image_obj['id'],
                "invoice_img_url": invoice_image_obj['url']
            }
        else:
            unique_uuid_invoice_image = str(uuid.uuid4())
            data_dict['invoiceImage'] = {
                "invoice_img_id": unique_uuid_invoice_image,
                "invoice_img_url": ""
            }
        

        data_dict['user_id'] = user_id
        data_dict['unique_uuid'] = unique_uuid_invoice

        
        #! validate information before upload to database ##
        try:
            InvoiceValidator(**data_dict)
        except ValidationError as e:
            error_message = "Validation error occurred. Missing fields or invalid fields"
            return JsonResponse({"error": error_message}, status=400, safe=False)

        # Add createdAt and updatedAt timestamps
        current_time = datetime.now(timezone.utc)
        data_dict['createdAt'] = current_time
        data_dict['updatedAt'] = current_time
        
        try:
            invoice_collection.insert_one(data_dict)
            data_dict['_id'] = str(data_dict['_id'])
            return JsonResponse(data_dict, status=200, safe=False)
        except Exception as e:
            print(e)
            error_message = "An error occurred during the invoice adding process."
            status_code = 500
            if isinstance(e, JsonResponse):
                error_message = e.content.decode('utf-8')
                status_code = e.status_code 
            
            return JsonResponse({"error": error_message}, status=status_code)
    else:
        return JsonResponse({"error": "Only POST requests are allowed for this endpoint!"})


"""
get all invoices in the database
complete end point: http://localhost:8000/api/invoice/getAll
"""
def get_all_invoices(request):
    token_info = verify_access_token(request)
        
    if isinstance(token_info, JsonResponse):
        return token_info  # Return the error response

    user_id = token_info[0]
    
    try:
        # send invoices user owned
        invoices = list(invoice_collection.find({"user_id":user_id}))

        if not invoices:
            return JsonResponse({"message":"No invoices found for this user!"}, status=404)

        # Convert ObjectId to str for JSON serialization
        for invoice in invoices:
            invoice['_id'] = str(invoice['_id'])

        return JsonResponse({"invoices": invoices}, status=200)
    except Exception as e:
        error_message = "An error occurred during the get all invoices process."
        status_code = 500
        
        if isinstance(e, JsonResponse):
            error_message = e.content.decode('utf-8')
            status_code = e.status_code
        
        # Return the error message as a JsonResponse
        return JsonResponse({"error": error_message}, status=status_code)
    



 
"""
get specific Invoice by its ID
complete end point: http://localhost:8000/invoice/getOne/65e262e8e7238f1f11f7bb8e
"""
def get_one_invoice(request,invoice_id):
    if request.method == 'GET':
        token_info = verify_access_token(request)
        if isinstance(token_info, JsonResponse):
            return token_info
        user_id = token_info[0]
        
        try:
            # send invoices user owned
            found_invoice = invoice_collection.find_one({"_id":ObjectId(invoice_id)})
            if not found_invoice:
                return JsonResponse({"error":"No invoice found with given ID"}, status=status.HTTP_404_NOT_FOUND)
            
            if found_invoice['user_id'] != user_id:
                return JsonResponse({"error": "You do not have permission to perform this action"}, status=403)

            # Convert ObjectId to str for JSON serialization
            found_invoice['_id'] = str(found_invoice['_id'])

            return JsonResponse(found_invoice, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500, safe=False)
    else:
        return JsonResponse({"error": "Only GET requests are allowed for this endpoint!"}, status=405)





""" 
delete existing invoice in the database using Invoice ID(_id attribute in MongoDB)
complete end point: http://localhost:8000/api/invoice/delete/65e262f1e7238f1f11f7bb8f
"""
def delete_invoice(request, unique_uuid):
    if request.method == 'DELETE':
        token_info = verify_access_token(request)
        if isinstance(token_info, JsonResponse):
            return token_info
        user_id = token_info[0]
        try:
            document = invoice_collection.find_one({"unique_uuid": unique_uuid})
            if document is None:
                return JsonResponse({"error": "Invoice not found"}, status=404)
            
            if document['user_id'] != user_id:
                return JsonResponse({"error": "You do not have permission to delete this invoice"}, status=403)

            # Find the invoice by its ID and delete it
            invoice_collection.find_one_and_delete({"unique_uuid": unique_uuid})
            is_deleted_aws_images = delete_user_images(unique_uuid)
            
            return JsonResponse(
                {
                    "message": "Invoice successfully deleted!",
                    "is_aws_images_deleted": is_deleted_aws_images
                }, status=200)
        except Exception as e:
            error_message = "An error occurred during the invoice deleting process."
            status_code = 500
            
            if isinstance(e, JsonResponse):
                error_message = e.content.decode('utf-8')
                status_code = e.status_code
            
            # Return the error message as a JsonResponse
            return JsonResponse({"error": error_message}, status=status_code)
    else:
        return JsonResponse({"error": "Only DELETE requests are allowed for this endpoint!"}, status=405)



""" 
update invoice endpoint
"""
def update_invoice(request, invoice_id):
    if request.method == 'POST':
        token_info = verify_access_token(request)
        if isinstance(token_info, JsonResponse):
            return token_info
        user_id = token_info[0]
        
        data = extract_form_update(request)
        
        data_dict = data['others']
        companyLogo = data['companyLogo']
        signature = data['signature']
        invoiceImage = data['invoiceImage']

        existing_invoice = invoice_collection.find_one({'_id': ObjectId(invoice_id)})
        if existing_invoice is None:
            return JsonResponse({"error": "Invoice not found"}, status=404)

        if existing_invoice['user_id'] != user_id:
            return JsonResponse({"error": "You do not have permission to update this invoice"}, status=403)

        unique_uuid_invoice = existing_invoice['unique_uuid']
        
        if signature is not None:
            existing_signature_obj = existing_invoice.get('signature')
            signature_id = existing_signature_obj['signature_id']
            obj = get_image_object(signature_id, signature, user_id, unique_uuid_invoice, "invoice_signature")
            data_dict['signature'] =  {
                "signature_id": obj['id'],
                "signature_url": obj['url']
            }
        
        if companyLogo is not None:
            existing_companyLogo_obj = existing_invoice.get('companyLogo')
            logo_id = existing_companyLogo_obj['logo_id']
            obj = get_image_object(logo_id, companyLogo, user_id, unique_uuid_invoice, "invoice_companyLogo")
            data_dict['companyLogo'] = {
                "logo_id": obj['id'],
                "logo_url": obj['url']
            }
        
        if invoiceImage is not None:
            existing_invoiceImage_obj = existing_invoice.get('invoiceImage')
            invoice_img_id = existing_invoiceImage_obj['invoice_img_id']
            obj = get_image_object(invoice_img_id, invoiceImage, user_id, unique_uuid_invoice, "invoice_image")
            data_dict['invoiceImage'] = {
                "invoice_img_id": obj['id'],
                "invoice_img_url": obj['url']
            }
        
        updated_invoice = update_data(data_dict, existing_invoice)

        current_time = datetime.now(timezone.utc)
        updated_invoice['updatedAt'] = current_time
        try:
            # Update the existing invoice based on the provided invoice_id
            invoice_collection.update_one({'_id': ObjectId(invoice_id)}, {'$set': updated_invoice})
            updated_invoice['_id'] = str(updated_invoice['_id'])
            return JsonResponse(updated_invoice, status=200, safe=False)
            
        except Exception as e:
            error_message = "An error occurred during the update process."
            status_code = 500
            
            if isinstance(e, JsonResponse):
                error_message = e.content.decode('utf-8')
                status_code = e.status_code
            
            # Return the error message as a JsonResponse
            return JsonResponse({"error": error_message}, status=status_code)
    else:
        return JsonResponse({"error": "Only POST requests are allowed for this endpoint!"}, status=405)
        
