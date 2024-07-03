import os
import json
import jwt
from django.http import JsonResponse
from auth_functions.verifyAccessTokens import verify_access_token
from auth_functions.getAccessToken import get_access_token
from auth_functions.getRefreshToken import get_refresh_token



# function to refresh the tokens and get new tokens
def refresh_token_fn(request):
    if request.method == 'POST':        
        try:
            body_unicode = request.body.decode('utf-8')
            body_data = json.loads(body_unicode)
            refreshToken = body_data.get('token')

            if not refreshToken:
                return JsonResponse({"message": "You are not authenticated!"}, status=401)
            
            
            # Verify refresh token
            try:
                refresh_secret_key = os.environ.get("REFRESH_TOKEN_SECRET")
                decoded_refresh_token = jwt.decode(refreshToken, refresh_secret_key, algorithms=['HS256'])
                
                print(decoded_refresh_token)
                
                # Generate new access token
                new_access_token = get_access_token(decoded_refresh_token['user_id'], decoded_refresh_token['auth_level'], decoded_refresh_token['plan'])
            
                # Generate new refresh token
                new_refresh_token = get_refresh_token(decoded_refresh_token['user_id'], decoded_refresh_token['auth_level'], decoded_refresh_token['plan'])
            
        
                # Return new tokens
                return JsonResponse({"accessToken": new_access_token, "refreshToken": new_refresh_token})
            except jwt.ExpiredSignatureError:
                return JsonResponse({"message": "Refresh token has expired!"}, status=403)
            except jwt.InvalidTokenError:
                return JsonResponse({"message": "Invalid refresh token!"}, status=403)
            
            
        except Exception as e:
            error_message = "An error occurred during the update process."
            status_code = 500
            
            if isinstance(e, JsonResponse):
                error_message = e.content.decode('utf-8')
                status_code = e.status_code
            return JsonResponse({"error": error_message}, status=status_code)

    else:
        return JsonResponse({"message": "Only POST requests are allowed for this endpoint!"}, status=405)