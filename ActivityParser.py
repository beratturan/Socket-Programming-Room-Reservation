import re
NOT_FOUND = ['404']
BAD_REQUEST = ['400']

MAIN_PATTERN = ':\d{4}\/(.*)\?'
ADD_PATTERN = '\d+\/add\?name=([^&]*)&{0,1}'
REMOVE_PATTERN = '\d+\/remove\?name=([^&]*)&{0,1}'
CHECK_PATTERN = '\d+\/check\?name=([^&]*)&{0,1}'

# GENERAL PURPOSE FUNCTIONS
def ListContainsNull(variable_list):
    for item in variable_list:
        if item:
            continue
        else:
            return True
    return False


def ListContainsAlphanumericCharacter(variable_list):
    for item in variable_list:
        if re.search(r'[^0-9a-zA-Z]', item):
            return True
    return False

# 400 BAD REQUEST FUNCTION
def checkValues(variable_list):
    # check if any variable is null
    if ListContainsNull(variable_list):
        return False

    # check if variables contain any non-alphanumeric character
    if ListContainsAlphanumericCharacter(variable_list):
        return False

    return True


# 404 NOT FOUND FUNCTION
def check404(request, get_type):

    # Select a regex pattern according to the get type
    pattern = ""
    if get_type == "add":
        pattern = ADD_PATTERN
    elif get_type == "remove":
        pattern = REMOVE_PATTERN
    elif get_type == "check":
        pattern = CHECK_PATTERN
    else:
        return NOT_FOUND

    # Parse the request according to the pattern.
    # If it's not parsed without an error, throw a NOT FOUND error.
    try:
        variables = re.search(pattern, request).groups()

    except AttributeError:
        return NOT_FOUND

    # ;\/?:@&=$, are delimiters in URLs, so they shouldn't be used in variable values.
    for item in variables:
        if re.search(r'[\s;\/?:@&=$,]', item):
            return NOT_FOUND

    # Check the correctness of the values.
    # If there is a problem with the values, throw a BAD REQUEST error.
    response = checkValues(variables)

    # If there is a BAD REQUEST, return ['400']
    # If there is no error, return ['200', 'V', ..., 'V'] where 'V' is a value of the request.
    if not response:
        return BAD_REQUEST
    else:
        response = ['200', get_type]
        for variable in variables:
            response.append(variable)
        return response


def ROOM_client_message_to_url(message):
    message = message.replace('\r', '')
    message_firstline_arr = message.split('\n')[0].split(' ')

    protocol = message_firstline_arr[2].split('/')[0].lower() + "://"
    address=message_firstline_arr[1]
    host=message.split('\n')[1].split("Host: ")[1]
    URL = protocol+host+address
    return URL


def main(request):
    try:
        url = ROOM_client_message_to_url(request)
        if "favicon.ico" in url:
            return ['200', 'favicon']

        get_type = re.search(MAIN_PATTERN, url).group(1)

        if get_type in ["add", "remove", "check"]:
            return check404(url, get_type)
        else:
            raise AttributeError

    except AttributeError:
        return NOT_FOUND
