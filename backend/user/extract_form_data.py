from django.http import QueryDict
from django.http.multipartparser import MultiPartParser, MultiPartParserError

def extract_form_data_update(request):
    # Initialize the others dictionary
    others = {}

    try:
        # Create a MultiPartParser to handle multipart form data
        parser = MultiPartParser(request.META, request, request.upload_handlers)
        put_data, files = parser.parse()

        # Check each field in the parsed PUT data and add to others if not null
        username = put_data.get('username')
        if username:
            others['username'] = username

        name = put_data.get('name')
        if name:
            others['name'] = name

        email = put_data.get('email')
        if email:
            others['email'] = email

        phone_number = put_data.get('phone_number')
        if phone_number:
            others['phone_number'] = phone_number

        # Get the file (from files)
        dp = files.get('dp')

        # Create the final data dictionary
        data = {
            "others": others,
            "dp": dp
        }

        return data

    except MultiPartParserError as e:
        raise e
