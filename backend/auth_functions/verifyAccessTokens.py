import os
import jwt
from django.http import JsonResponse




def verify_access_token(request):
    accessTokenSecret = os.environ.get('ACCESS_TOKEN_SECRET')
    auth_header = request.headers.get('Authorization', None)
    
    if auth_header is not None and auth_header.startswith('Bearer '):
        # Extract the token value from the Authorization header
        access_token = auth_header.split(' ')[1]  # Split the header by space and take the second part

        # check database, if access token is available or not
        if not access_token:
            return JsonResponse({"error": "Unauthorized"}, status=401)

        try:
            
            # Verify access token
            decoded_access_token = jwt.decode(access_token, accessTokenSecret, algorithms=['HS256'])
            token_type = decoded_access_token['token_type']

            if token_type != 'access':
                return JsonResponse({"error": "Invalid token type"}, status=403)

            user_id = decoded_access_token['user_id']
            auth_level = decoded_access_token['auth_level']
            return [user_id, auth_level]
        
        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Access token has expired!"}, status=403)
        except jwt.InvalidTokenError:
            return JsonResponse({"error": "Invalid access token!"}, status=403)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500, safe=False)
                
    else:
        # Handle cases where Authorization header is missing or not in the expected format
        return JsonResponse({"error": "Unauthorized"}, status=401)