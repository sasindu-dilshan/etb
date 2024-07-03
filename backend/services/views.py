import json
import uuid
from bson import ObjectId
from .models import tools_collection, ToolsValidator
from user.models import user_collection
from django.http import JsonResponse
from auth_functions.verifyAccessTokens import verify_access_token
###############################################################################################



def index(request):
    return JsonResponse({"message":"App is running"})

def add_tools_and_properties(request):
    if request.method == 'POST':
        token_info = verify_access_token(request)
        if isinstance(token_info, JsonResponse):
            return token_info

        if token_info[1] != 'admin':
            return JsonResponse({"error": "You do not have permission to perform this action"}, status=403)

        try:
            
            if not request.body:
                return JsonResponse({"error": "No data provided"}, status=400)

            body_data = json.loads(request.body)

            if not isinstance(body_data, list):
                return JsonResponse({"error": "Input data should be an array of service objects"}, status=400)
            
            if body_data == []:
                return JsonResponse({"error": "No services to insert"}, status=400)

            validated_tools = []
            for tool in body_data:
                try:
                    validated_tool = ToolsValidator(**tool)
                    found_tool = tools_collection.find_one({"tool_name": validated_tool.tool_name})
                    if found_tool:
                        return JsonResponse({"error": f"Tool name '{validated_tool.tool_name}' already exists. Tool name must be unique"}, status=400)
                    model_dumped_tool = validated_tool.model_dump()
                    for feature in model_dumped_tool['features']:
                        feature['_id'] = str(uuid.uuid4())
                    validated_tools.append(model_dumped_tool)
                except Exception as e:
                    return JsonResponse({"error": f"Validation error for service: {tool.get('tool_name', 'Unknown')} - {str(e)}"}, status=400)

            if not validated_tools:
                return JsonResponse({"error": "No valid services to insert"}, status=400)

            result = tools_collection.insert_many(validated_tools)
            for service, inserted_id in zip(validated_tools, result.inserted_ids):
                service['_id'] = str(inserted_id)

            return JsonResponse(validated_tools, status=201, safe=False)
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data provided"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Only POST requests are allowed for this endpoint!"}, status=405)


###############################################################################################

def get_all_tools(request):
    if request.method == 'GET':
        try:
            tools = list(tools_collection.find())
            for tool in tools:
                tool['_id'] = str(tool['_id'])
            return JsonResponse(tools, status=200, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500, safe=False)
    else:
        return JsonResponse({"error": "Only GET requests are allowed for this endpoint!"}, status=405)
    

###############################################################################################

def get_tool_by_id(request, tool_id):
    if request.method == 'GET':
        token_info = verify_access_token(request)
        if isinstance(token_info, JsonResponse):
            return token_info
        
        if token_info[1] != 'admin':
            return JsonResponse({"error": "You do not have permission to perform this action"}, status=403)
        try:
            tool = tools_collection.find_one({"_id": ObjectId(tool_id)})
            if tool:
                tool['_id'] = str(tool['_id'])
                return JsonResponse(tool, status=200)
            else:
                return JsonResponse({"error": "Tool not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500, safe=False)
    else:
        return JsonResponse({"error": "Only GET requests are allowed for this endpoint!"}, status=405)
    

###############################################################################################

def update_tool_by_id(request, tool_id):
    if request.method == 'PUT':
        token_info = verify_access_token(request)
        if isinstance(token_info, JsonResponse):
            return token_info
        
        if token_info[1] != 'admin':
            return JsonResponse({"error": "You do not have permission to perform this action"}, status=403)
        try:
            body_data = json.loads(request.body)
            ToolsValidator(**body_data)
            updated_tool = tools_collection.find_one_and_update({"_id": ObjectId(tool_id)}, {"$set": body_data}, return_document=True)
            if updated_tool:
                updated_tool['_id'] = str(updated_tool['_id'])
                return JsonResponse(updated_tool, status=200)
            else:
                return JsonResponse({"error": "Tool not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500, safe=False)
    else:
        return JsonResponse({"error": "Only PUT requests are allowed for this endpoint!"}, status=405)
    
###############################################################################################

def delete_tool_by_id(request, tool_id):
    if request.method == 'DELETE':
        token_info = verify_access_token(request)
        if isinstance(token_info, JsonResponse):
            return token_info
        
        if token_info[1] != 'admin':
            return JsonResponse({"error": "You do not have permission to perform this action"}, status=403)
        try:
            deleted_tool = tools_collection.find_one_and_delete({"_id": ObjectId(tool_id)})
            if deleted_tool:
                deleted_tool['_id'] = str(deleted_tool['_id'])
                return JsonResponse(deleted_tool, status=200)
            else:
                return JsonResponse({"error": "Tool not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500, safe=False)
    else:
        return JsonResponse({"error": "Only DELETE requests are allowed for this endpoint!"}, status=405)



def check_validity(request):
    if request.method == 'POST':
        try:
            body_data = json.loads(request.body)
            tool_id = body_data.get("tool_id")
            feature_id = body_data.get("feature_id")

            if not tool_id or not feature_id:
                return JsonResponse({"error": "Tool ID and Feature ID are required"}, status=400)
            
            found_tool = tools_collection.find_one({"_id": ObjectId(tool_id)})
            if not found_tool:
                return JsonResponse({"error": "Tool not found"}, status=404)
            
            found_feature = next((feature for feature in found_tool['features'] if feature['_id'] == feature_id), None)

            if not found_feature:
                return JsonResponse({"error": "Feature not found"}, status=404)
            
            allowed_list = found_feature.get("allowed", [])
            

            #! if unauthorized, check tool feature available for all (including unauthorized users)
            #! if so, return allowed
            #! else, return signin
            token_info = verify_access_token(request)
            if isinstance(token_info, JsonResponse):
                if token_info.status_code == 401:
                    if "all" in allowed_list:
                        return JsonResponse({"message": "allowed"}, status=200)
                    else:
                        return JsonResponse({"message": "signin"}, status=200)
                else:
                    return token_info
                

            user_id = token_info[0]
            found_user = user_collection.find_one({"_id": ObjectId(user_id)})

            if not found_user:
                return JsonResponse({"error": "User not found"}, status=404)
            
            user_plan = found_user.get("plan", "free")
            if user_plan in allowed_list:
                return JsonResponse({"message": "allowed"}, status=200)
            else:
                return JsonResponse({"message": "upgrade"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return JsonResponse({"error": "Only POST requests are allowed for this endpoint!"}, status=405)