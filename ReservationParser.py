import re

DAY_LIST = ['1', '2', '3', '4', '5', '6', '7']
HOUR_LIST = ['9', '10', '11', '12', '13', '14', '15', '16', '17']
NOT_FOUND = ['404']
BAD_REQUEST = ['400']

MAIN_PATTERN = ':\d{4}\/(.*)\?'
RESERVE_PATTERN = '\d+\/reserve\?room=([^&]*)&activity=([^&]*)&day=([^&]*)&hour=([^&]*)&duration=([^&]*)&{0,1}'
AVAILABILITY_PATTERN = '\d+\/listavailability\?room=([^&]*)&{0,1}(day=([^&]*)){0,1}&{0,1}'
DISPLAY_PATTERN = '\d+\/display\?id=([^&]*)&{0,1}'


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


def checkHourAndDurationRule(hour, duration):
    try:
        hour = int(hour)
        duration = int(duration)
    except ValueError:
        return False
    if (duration > 0) and (9 <= (hour + duration)) and (17 >= (hour + duration)):
        return True
    else:
        return False


def checkValues(variable_list, get_type):
    # check if any variable is null
    if ListContainsNull(variable_list):
        return False

    # check if variables contain any non-alphanumeric character
    if ListContainsAlphanumericCharacter(variable_list):
        return False

    if get_type == "reserve":
        if not variable_list[2] in DAY_LIST:
            return False
        if not variable_list[3] in HOUR_LIST:
            return False
        if not checkHourAndDurationRule(variable_list[3], variable_list[4]):
            return False
    elif get_type == "listavailability" and len(variable_list) == 2:
        if not variable_list[1] in DAY_LIST:
            return False

    return True


# 404 NOT FOUND FUNCTION
def check404(request, get_type):

    # Select a regex pattern according to the get type
    pattern = ""
    if get_type == "reserve":
        pattern = RESERVE_PATTERN
    elif get_type == "listavailability":
        pattern = AVAILABILITY_PATTERN
    elif get_type == "display":
        pattern = DISPLAY_PATTERN
    else:
        return NOT_FOUND

    # Parse the request according to the pattern.
    # If it's not parsed without an error, throw a NOT FOUND error.
    try:
        variables = re.search(pattern, request).groups()
        variables = [x for x in variables if x is not None]
        for item in variables:
            if 'day' in item:
                variables.remove(item)

    except AttributeError:
        return NOT_FOUND

    # ;\/?:@&=$, are delimiters in URLs, so they shouldn't be used in variable values.
    for item in variables:
        if re.search(r'[\s;\/?:@&=$,]', item):
            return NOT_FOUND

    # Check the correctness of the values.
    # If there is a problem with the values, throw a BAD REQUEST error.
    response = checkValues(variables, get_type)

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
        print(url)
        get_type = re.search(MAIN_PATTERN, url).group(1)

        if get_type in ["reserve", "listavailability", "display"]:
            return check404(url, get_type)
        else:
            raise AttributeError

    except AttributeError:
        return NOT_FOUND
