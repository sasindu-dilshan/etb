import os
import json
import uuid
import bcrypt
from bson import ObjectId
import jwt
from pydantic import ValidationError
from .models import user_collection, UserValidator
from django.http import JsonResponse
from invoiceGenerator.models import invoice_collection
from auth_functions.getAccessToken import get_access_token
from auth_functions.getRefreshToken import get_refresh_token
from auth_functions.verifyAccessTokens import verify_access_token
from rest_framework import status
from common_routes.aws.aws_delete import delete_user_images
from datetime import datetime, timedelta, timezone
from .extract_form_data import extract_form_data_update
from common_routes.other_functions.update import add_new_image, get_image_object
from .models import UserAccount
from .serializers import UserAccountSerializer
from rest_framework.response import Response 
from djoser.social.views import ProviderAuthView
from django.conf import settings
###############################################################################################

def index(request):
    return JsonResponse({"message":"App is running"})
class CustomProviderAuthView(ProviderAuthView):
    def get(self, request, *args, **kwargs):
        # Extract the provider from kwargs
        provider = kwargs.get('provider')
        if not provider:
            return Response({'error': 'Provider not specified'}, status=status.HTTP_400_BAD_REQUEST)
        self.kwargs['provider'] = provider
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
            # Extract the provider from kwargs
            provider = kwargs.get('provider')
            if not provider:
                return Response({'error': 'Provider not specified'}, status=status.HTTP_400_BAD_REQUEST)

            # Set the provider in self.kwargs for further processing
            self.kwargs['provider'] = provider

            # Call super to handle the original Djoser token creation
            response = super().post(request, *args, **kwargs)

            # Check if Djoser response has tokens
            if 'access' in response.data and 'refresh' in response.data:

                data = response.data
                access_token = data['access']
                accessTokenSecret = settings.SECRET_KEY
                decoded_access_token = jwt.decode(access_token, accessTokenSecret, algorithms=['HS256'])
                user_id = decoded_access_token['user_id']
                try:
                    found_user = UserAccount.objects.get(id=user_id)
                except UserAccount.DoesNotExist:
                    return JsonResponse({"error": "User not found"}, status=404)
                
                except Exception as e:
                    return JsonResponse({"error": str(e)}, status=500, safe=False)

                access_token = get_access_token(found_user.unique_uuid_user, found_user.auth_level, found_user.plan)
                refresh_token = get_refresh_token(found_user.unique_uuid_user, found_user.auth_level, found_user.plan)
                return JsonResponse({"accessToken": access_token, "refreshToken": refresh_token}, status=200)

            else:
                return JsonResponse({"error": "An error occurred during the token creation process"}, status=500)

    def _action(self, serializer):
        # Save the user using the original method
        user = serializer.save()
        # Check if the user already exists in CustomUser
        custom_user, created = UserAccount.objects.get_or_create(
            username=user.username,
            defaults={
                'plan': 'free',
                'email': user.email,
                'password': user.password,
                'is_superuser': user.is_superuser,
                'unique_uuid_user': str(uuid.uuid4())
            }
        )
        if created:
            custom_user.save()
        
        # You can add any additional logic here, for example, updating fields
        return Response(status=status.HTTP_204_NO_CONTENT)





# user registration endpoint
def register(request):
    if request.method == 'POST':
        try:
            post_data = json.loads(request.body)
            
            # validate incoming data
            try:
                UserValidator(**post_data)
            except ValidationError as e:
                # If validation fails, return a JsonResponse with the validation errors
                error_message = "Validation error occurred. Missing fields or invalid fields"
                return JsonResponse({"error": error_message}, status=status.HTTP_400_BAD_REQUEST, safe=False)

            email = post_data.get('email')
            email = email.lower()
            username = post_data.get('username')
            name = post_data.get('name')
            password = post_data.get('password')
            phone_number = post_data.get('phone_number')
            plan = 'free'
            unique_uuid_user = str(uuid.uuid4())
            dp = {
                "dp_id": unique_uuid_user,
                "dp_url": ""
            }
            # hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))

            # if user_collection.find_one({"username":username}):
                # return JsonResponse({"error": "Username already exists"}, status=status.HTTP_409_CONFLICT)
            if UserAccount.objects.filter(username=username).first():
                return JsonResponse({"error": "Username already exists"}, status=status.HTTP_409_CONFLICT)
            
            if UserAccount.objects.filter(email=email).first():
                return JsonResponse({"error": "Email already exists"}, status=status.HTTP_409_CONFLICT)
            
            # if user_collection.find_one({"email":email}):
                # return JsonResponse({"error": "Email already exists"}, status=status.HTTP_409_CONFLICT)

            user_data = {
            'username': username,
            'name': name,
            'password': password,
            'email': email,
            'phone_number': phone_number,
            'unique_uuid_user':unique_uuid_user,
            'plan': plan,
            'auth_level': 'user',
            'dp': dp,
            }

            serializer = UserAccountSerializer(data=user_data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({"message": "Registration Successfull!"}, status=201)
            else:
                return JsonResponse({"error": "error occured. Please check your data and try again"}, status=400, safe=False)

            # user_collection.insert_one(user_data)            
            # return JsonResponse({"message": "Registration Successfull!"}, status=201)
        except Exception as e:
            return JsonResponse({"error": "something went wrong. Please try again.", "errorStack":str(e)}, status=500)
    else:
        return JsonResponse({"error": "Only POST requests are allowed for this endpoint!"}, status=405)

# user login endpoint
def user_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            if not (username and password):
                return JsonResponse({"error": "Please provide username and password"}, status=400)

            # user = user_coll.find_one({"username":username})
            user = UserAccount.objects.get(username=username)

            if user is not None:
                if user.check_password(password):
                    #Convert ObjectId to string
                    # user_id= str(user['_id'])
                    # auth_level = user['auth_level']
                    # plan = user['plan']
                    
                    user_id = user.unique_uuid_user
                    auth_level = user.auth_level
                    plan = user.plan

                    # getting access token
                    accessToken = get_access_token(user_id, auth_level, plan);

                    # getting refresh token
                    refreshToken = get_refresh_token(user_id, auth_level, plan)
                    
                    # Create a JsonResponse
                    return JsonResponse({"accessToken":accessToken, "refreshToken": refreshToken}, safe=False)
                else:
                    return JsonResponse({"error": "Invalid credentials"}, status=401)
            else:
                return JsonResponse({"error": "Invalid credentials"}, status=401)
        except Exception as e:
            error_message = "An error occurred during the login process."
            status_code = 500
            
            if isinstance(e, JsonResponse):
                error_message = e.content.decode('utf-8')
                status_code = e.status_code 
            
            # Return the error message as a JsonResponse
            return JsonResponse({"error": error_message, "errorStack": str(e)}, status=status_code, safe=False)
    else:
        return JsonResponse({"error": "Only POST requests are allowed for this endpoint!"}, status=405)


def get_user_info(request):
    if request.method == 'GET':
        token_info = verify_access_token(request)
        if isinstance(token_info, JsonResponse):
            return token_info
        
        user_id = token_info[0]

        try:
            user = UserAccount.objects.get(unique_uuid_user=user_id)
            serializer = UserAccountSerializer(user)
            # user['_id'] = str(user['_id'])
            # user.pop('password')
            return JsonResponse(serializer.data, safe=False)
        except UserAccount.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500, safe=False)
    else:
        return JsonResponse({"error": "Only GET requests are allowed for this endpoint!"}, status=405)

# user aupdate account
def update_user_account(request):
    if request.method == 'PUT':

        token_info = verify_access_token(request)
        if isinstance(token_info, JsonResponse):
            return token_info

        user_id = token_info[0]
        
        # Update the existing user in the database
        try:

            # find is there user by _id got from access token
            user = UserAccount.objects.get(unique_uuid_user=user_id)
            serializer = UserAccountSerializer(user)
            found_user_by_id = serializer.data
            
            data = extract_form_data_update(request)

            data_dict = data['others']
            dp = data['dp']


            if dp is not None:
                existing_dp_obj = found_user_by_id.get('dp')
                dp_id = existing_dp_obj['dp_id']
                obj = get_image_object(dp_id, dp, user_id, found_user_by_id.get('unique_uuid_user'), "user_dp_images")
                data_dict['dp'] =  {
                    "dp_id": obj['id'],
                    "dp_url": obj['url']
                }

            update_serializer = UserAccountSerializer(user, data=data_dict, partial=True)

            if update_serializer.is_valid():
                    try:
                        update_serializer.save()
                        return JsonResponse({"message":"Account has been updated successfully"}, status=200)
                    except Exception as e:
                        error_status = getattr(e, 'status_code', status.HTTP_500_INTERNAL_SERVER_ERROR)
                        return JsonResponse({"error": str(e)}, status=error_status ,safe=False)
            else:
                return JsonResponse({"error": update_serializer.errors}, status=400, safe=False)

            # Update the existing user based on the provided user_id
            # user_collection.update_one({'_id': ObjectId(user_id)}, {'$set': data_dict})
            # return JsonResponse({"message":"Account has been updated successfully"})
        
        except UserAccount.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500, safe=False)
    else:
        return JsonResponse({"error": "Only PUT requests are allowed for this endpoint!"}, status=405)
    
def update_password(request):
    if request.method == 'PATCH':
        user_id = verify_access_token(request)
        if isinstance(user_id, JsonResponse):
            return user_id

        user_id = user_id[0]
            
        
        # Update the existing user in the database
        try:
            # Retrieve the PUT data from the request
            put_data = json.loads(request.body)

            if put_data is None:
                return JsonResponse({"error": "Request body is required to update password"}, status=400)

            # find is there user by _id got from access token
            # found_user_by_id = user_collection.find_one({"_id":ObjectId(user_id)})
            found_user_by_id = UserAccount.objects.get(unique_uuid_user=user_id)
            # if not found_user_by_id:
                # return JsonResponse({"error": "User doesn't exists"}, status=404)

            current_password = put_data.get('current_password')
            new_pass = put_data.get('new_password')
            repeat_new_pass = put_data.get('repeat_new_password')

            if not current_password or not new_pass or not repeat_new_pass:
                return JsonResponse({"error": "Current Password, New Password and Repeat New Password Required"}, status=401)
            
            check_password = found_user_by_id['password']
            if not bcrypt.checkpw(current_password.encode('utf-8'), check_password):
                return JsonResponse({"error": "Current Password is incorrect"}, status=401)
            
            if new_pass != repeat_new_pass:
                return JsonResponse({"error": "New Password and Repeated New Password must be same"}, status=400)


            new_hashed_pw =  bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt(rounds=12))

            updated_password = {
                'password': new_hashed_pw
            }

            update_serializer = UserAccountSerializer(found_user_by_id, data=updated_password, partial=True)

            if update_serializer.is_valid():
                    try:
                        update_serializer.save()
                        return JsonResponse({"message":"Password has been updated successfully"}, status=200)
                    except Exception as e:
                        error_status = getattr(e, 'status_code', status.HTTP_500_INTERNAL_SERVER_ERROR)
                        return JsonResponse({"error": str(e)}, status=error_status ,safe=False)
            else:
                return JsonResponse({"error": update_serializer.errors}, status=400, safe=False)

            # Update the existing user based on the provided user_id
            # user_collection.update_one({'_id': ObjectId(user_id)}, {'$set': updated_password})
            # return JsonResponse({"message":"Password has been updated successfully"})
        
        except UserAccount.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        except json.JSONDecodeError as e:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)    
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500, safe=False)
    else:
        return JsonResponse({"error": "Only PATCH requests are allowed for this endpoint!"}, status=405)


#! below are not updated

# user delete account
async def delete_user_account(request):
    if request.method == 'DELETE':
        refresh_secret_key = os.environ.get("REFRESH_TOKEN_SECRET")
        access_secret_key = os.environ.get("ACCESS_TOKEN_SECRET")
        user_id = verify_access_token(request)
        # If verify_access_token encountered an error, return the response immediately
        if isinstance(user_id, JsonResponse):
            return user_id
        
        try:

            # Find the invoice by its ID and delete it
            deleted_document = user_collection.find_one_and_delete({"_id": ObjectId(user_id)})

            # Check if the invoice exists
            if not deleted_document:
                return JsonResponse({"Error":"User has not been found! try again."}, status=404)

            is_invoices_deleted = False
            try:
                # delete all invoices belongs to user from database
                invoice_collection.delete_many({"user_id":user_id})
                is_invoices_deleted = True
            
            except Exception as e:
                is_invoices_deleted = False
            
            is_deleted_aws_images = delete_user_images(user_id)
        
            return JsonResponse({
                "message": "Account has been successfully deleted!", 
                "is_database_invoices_cleared": is_invoices_deleted,
                "is_aws_docs_cleared": is_deleted_aws_images
                }, status=200)
        except Exception as e:
            return JsonResponse({"error": "something went wrong. Please try again.", "errorStack":str(e)}, status=500)
    else:
        return JsonResponse({"error": "Only DELETE requests are allowed for this endpoint!"}, status=405)
    

# user forgot password and update password
def update_password_only(request):
    if request.method == 'PUT' or request.method == 'PATCH':
        # Retrieve the PUT data from the request
        put_data = json.loads(request.body)

        user_email = put_data.get('email')
        new_pass = put_data.get('password')

        if not user_email or not new_pass:
            return JsonResponse({"error": "User Email and New Password Required"}, status=401)

        new_hashed_pw =  bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt(rounds=12))
        put_data['password'] = new_hashed_pw    
        
        # find is there user by _id got from access token
        found_user_by_email = user_collection.find_one({"email":user_email})
        if not found_user_by_email:
            return JsonResponse({"error": "User doesn't exists"}, status=404)

        # Update the existing user in the database
        try:
            # Update the existing user based on the provided user_id
            user_collection.update_one({'email': user_email}, {'$set': put_data})
            return JsonResponse({"message":"Password has been updated successfully"})
            
        except Exception as e:
            error_message = "An error occurred during the update process."
            status_code = 500
            
            if isinstance(e, JsonResponse):
                # If the exception is a JsonResponse object, extract the error message and status code
                error_message = e.content.decode('utf-8')  # Extract the error message from JsonResponse
                status_code = e.status_code  # Extract the status code from JsonResponse
            
            # Return the error message as a JsonResponse
            return JsonResponse({"error": error_message}, status=status_code)
    else:
        return JsonResponse({"error": "Only PUT and PATCH requests are allowed for this endpoint!"}, status=405)
    


def upgrade_user_account_pro(request):
    if request.method == 'PUT' or request.method == 'PATCH':

        # Retrieve user id with access token verification
        user_id = verify_access_token(request)

        # If verify_access_token encountered an error, return the response immediately
        if isinstance(user_id, JsonResponse):
            return user_id  # Return the error response
        
        if not request.body:
            return JsonResponse({"error": "Request body is required to upgrade account"}, status=400)

        body = json.loads(request.body)
        months = body.get('months')
        if not months:
            return JsonResponse({"error": "Months required to upgrade account"}, status=400)
        
        # find is there user by _id got from access token
        found_user_by_id = user_collection.find_one({"_id":ObjectId(user_id)})
        if not found_user_by_id:
            return JsonResponse({"error": "User doesn't exists"}, status=404)
        

        activating_date = datetime.now(timezone.utc)
        expiring_date = activating_date + timedelta(days=months * 30)  # Approximation to 30 days per month

        put_data = {
            'plan': 'pro',
            'activating_date': activating_date,
            'expiring_date': expiring_date
        }

        # Update the existing user in the database
        try:
            # Update the existing user based on the provided user_id
            user_collection.update_one({'_id': ObjectId(user_id)}, {'$set': put_data})
            return JsonResponse({"message":"Account has been updated successfully"})
            
        except Exception as e:
            error_message = "An error occurred during the update process."
            status_code = 500
            
            if isinstance(e, JsonResponse):
                # If the exception is a JsonResponse object, extract the error message and status code
                error_message = e.content.decode('utf-8')  # Extract the error message from JsonResponse
                status_code = e.status_code  # Extract the status code from JsonResponse
            
            # Return the error message as a JsonResponse
            return JsonResponse({"error": error_message}, status=status_code)
    else:
        return JsonResponse({"error": "Only PUT and PATCH requests are allowed for this endpoint!"}, status=405)



def upgrade_user_account_premium(request):
    if request.method == 'PUT' or request.method == 'PATCH':
        
        # Retrieve user id with access token verification
        user_id = verify_access_token(request)

        # If verify_access_token encountered an error, return the response immediately
        if isinstance(user_id, JsonResponse):
            return user_id  # Return the error response
        

        body = json.loads(request.body)
        months = body.get('months')
        if not months:
            return JsonResponse({"error": "Months required to upgrade account"}, status=400)
        
        # find is there user by _id got from access token
        found_user_by_id = user_collection.find_one({"_id":ObjectId(user_id)})
        if not found_user_by_id:
            return JsonResponse({"error": "User doesn't exists"}, status=404)
        
        activating_date = datetime.now(timezone.utc)
        expiring_date = activating_date + timedelta(days=months * 30)  # Approximation to 30 days per month

        put_data = {
            'plan': 'pro',
            'activating_date': activating_date,
            'expiring_date': expiring_date
        }

        # Update the existing user in the database
        try:
            # Update the existing user based on the provided user_id
            user_collection.update_one({'_id': ObjectId(user_id)}, {'$set': put_data})
            return JsonResponse({"message":"Account has been updated successfully"})
            
        except Exception as e:
            error_message = "An error occurred during the update process."
            status_code = 500
            
            if isinstance(e, JsonResponse):
                # If the exception is a JsonResponse object, extract the error message and status code
                error_message = e.content.decode('utf-8')  # Extract the error message from JsonResponse
                status_code = e.status_code  # Extract the status code from JsonResponse
            
            # Return the error message as a JsonResponse
            return JsonResponse({"error": error_message}, status=status_code)
    else:
        return JsonResponse({"error": "Only PUT and PATCH requests are allowed for this endpoint!"}, status=405)
   


def activate_free_trial_pro(request):
    if request.method == 'PUT' or request.method == 'PATCH':
        
        # Retrieve user id with access token verification
        user_id = verify_access_token(request)

        # If verify_access_token encountered an error, return the response immediately
        if isinstance(user_id, JsonResponse):
            return user_id  # Return the error response
        
        # find is there user by _id got from access token
        found_user_by_id = user_collection.find_one({"_id":ObjectId(user_id)})
        if not found_user_by_id:
            return JsonResponse({"error": "User doesn't exists"}, status=404)
        
        activating_date = datetime.now(timezone.utc)
        expiring_date = activating_date + timedelta(days=30)

        put_data = {
            'plan': 'pro',
            'activating_date': activating_date,
            'expiring_date': expiring_date
        }

        # Update the existing user in the database
        try:
            # Update the existing user based on the provided user_id
            user_collection.update_one({'_id': ObjectId(user_id)}, {'$set': put_data})
            return JsonResponse({"message":"Account has been updated successfully"})
            
        except Exception as e:
            error_message = "An error occurred during the update process."
            status_code = 500
            
            if isinstance(e, JsonResponse):
                # If the exception is a JsonResponse object, extract the error message and status code
                error_message = e.content.decode('utf-8')  # Extract the error message from JsonResponse
                status_code = e.status_code  # Extract the status code from JsonResponse
            
            # Return the error message as a JsonResponse
            return JsonResponse({"error": error_message}, status=status_code)
    else:
        return JsonResponse({"error": "Only PUT and PATCH requests are allowed for this endpoint!"}, status=405)





def activate_free_trial_premium(request):
    if request.method == 'PUT' or request.method == 'PATCH':
        
        # Retrieve user id with access token verification
        user_id = verify_access_token(request)

        # If verify_access_token encountered an error, return the response immediately
        if isinstance(user_id, JsonResponse):
            return user_id  # Return the error response
        
        # find is there user by _id got from access token
        found_user_by_id = user_collection.find_one({"_id":ObjectId(user_id)})
        if not found_user_by_id:
            return JsonResponse({"error": "User doesn't exists"}, status=404)
        
        activating_date = datetime.now(timezone.utc)
        expiring_date = activating_date + timedelta(days=30)

        put_data = {
            'plan': 'premium',
            'activating_date': activating_date,
            'expiring_date': expiring_date
        }

        # Update the existing user in the database
        try:
            # Update the existing user based on the provided user_id
            user_collection.update_one({'_id': ObjectId(user_id)}, {'$set': put_data})
            return JsonResponse({"message":"Account has been updated successfully"})
            
        except Exception as e:
            error_message = "An error occurred during the update process."
            status_code = 500
            
            if isinstance(e, JsonResponse):
                # If the exception is a JsonResponse object, extract the error message and status code
                error_message = e.content.decode('utf-8')  # Extract the error message from JsonResponse
                status_code = e.status_code  # Extract the status code from JsonResponse
            
            # Return the error message as a JsonResponse
            return JsonResponse({"error": error_message}, status=status_code)
    else:
        return JsonResponse({"error": "Only PUT and PATCH requests are allowed for this endpoint!"}, status=405)