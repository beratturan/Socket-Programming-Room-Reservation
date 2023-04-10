import json
import os
import socket 
import ActivityParser as ap ## Import parser
import logging

## HTTP Error messages initialized
general_404_err = "HTTP/1.1 404 Not Found\nContent-Type: text/html\n\n<html><head><title>Error</title></head><body><h1>Page Not Found</h1></body></html>"
general_400_err = "HTTP/1.1 400 Bad Request\nContent-Type: text/html\n\n<html><head><title>Bad Request</title></head><body></body></html>"


JSON_FNAME="activities.json"
JSON_FPATH= os.getcwd() + '/'
JSON_ATTR_ACTIVITIES="activities"
JSON_ATTR_ACT_NAME="activity_name"
"""
This method deletes the record of requested activitie which is indicated by name in client's request message.
- Special http responses defined in the method(200, 403).
- Method uses a flag variable to check if requested activity is exits in database or not
- Once method loads the JSON data into a python dictionary, it searches given activity name by using loop and enumerator. 
  When given activity is found, method deltes the record in dictionary according to given room name's index.
- Writes updated data into the JSON Database 
- Method returns proper http messages as a response in different conditions.
"""
def remove_activity(given_name,JSON_FNAME,JSON_FPATH,JSON_ATTR_ACTIVITIES,JSON_ATTR_ACT_NAME):
  
  RMV_200_OK = f"HTTP/1.1 200 OK\nContent-Type: text/html\n\n<html><body><h1>Activity Removed</h1><p>Activity with name {given_name} is successfully removed.</p></body></html>"
  RMV_403_FORBIDDEN = f"HTTP/1.1 403 Forbidden\nContent-Type: text/html\n\n<html><body><h1>Error</h1><p>An activity with the name {given_name} does not exists in the database.</p></body></html>"
  
  with open(f"{JSON_FPATH}{JSON_FNAME}", "r") as f:
    json_database = json.load(f)

  activities = json_database[JSON_ATTR_ACTIVITIES]
  found_flag = False
  for i, room in enumerate(activities):
    if str(room[JSON_ATTR_ACT_NAME]).upper() == str(given_name).upper():
      del activities[i]
      found_flag = True
      break

  if not found_flag:
    return RMV_403_FORBIDDEN

  with open(f"{JSON_FPATH}{JSON_FNAME}", "w") as f:
    json.dump(json_database, f)
  return RMV_200_OK

"""
This method checks the given activity is exists or not in the JSON database. Method interacts the JSON Database 
by using its parameter which are arranged in main. 
- Method interacts to JSON Database and gets the unreserved hours values of requested day by comparing room names in JSON and
  given parameter
- Method uses a flag variable to indicate requested activity is found or not after scanning the database.
- Method returns a proper http messages as a server response.
"""
def is_activity_exists(given_name,JSON_FNAME,JSON_FPATH,JSON_ATTR_ACTIVITIES,JSON_ATTR_ACT_NAME):
  
  EXISTS_200_OK = f"HTTP/1.1 200 OK\nContent-Type: text/html\n\n<html><body><h1>Activity Exists</h1><p>Activity with name {given_name} is exists.</p></body></html>"
  EXISTS_403_FORBIDDEN = f"HTTP/1.1 403 Forbidden\nContent-Type: text/html\n\n<html><body><h1>Error</h1><p>An activity with the name {given_name} does not exist.</p></body></html>"
  
  with open(f"{JSON_FPATH}{JSON_FNAME}", "r") as f:
    json_database = json.load(f)

  activities = json_database[JSON_ATTR_ACTIVITIES]
  found_flag = False
  for i, room in enumerate(activities):
    if str(room[JSON_ATTR_ACT_NAME]).upper() == str(given_name).upper():
      found_flag = True
      break

  if not found_flag:
    return EXISTS_403_FORBIDDEN
  return EXISTS_200_OK
  
"""
This method adds new record of requested activity which is indicated in client's request message.
- Special http responses defined in the method(200, 403).
- If our JSON database is empty method immediately adds the given room record.
- Once method loads the JSON data into a python dictionary, it appends the new activity record whose structure is already defined in the function to the room list of JSON database.
- Method returns proper http messages as a response in different conditions.
"""
def add_activity(given_name,JSON_FNAME,JSON_FPATH,JSON_ATTR_ACTIVITIES,JSON_ATTR_ACT_NAME):

  ADD_200_OK = f"HTTP/1.1 200 OK\nContent-Type: text/html\n\n<html><body><h1>Activity Added</h1><p>Activity with name {given_name} is successfully added.</p></body></html>"
  ADD_403_FORBIDDEN = f"HTTP/1.1 403 Forbidden\nContent-Type: text/html\n\n<html><body><h1>Error</h1><p>An activity with the name {given_name} already exists in the database.</p></body></html>"
  ACT_TO_BE_ADDED={
      "activity_name": given_name.upper(),
      }

  try:
    with open(f"{JSON_FPATH}{JSON_FNAME}", "r") as f:
      json_database = json.load(f)
      if json_database[JSON_ATTR_ACTIVITIES] == []:
        json_database[JSON_ATTR_ACTIVITIES].append(ACT_TO_BE_ADDED)
      else:
        for activities in json_database[JSON_ATTR_ACTIVITIES]:
          if given_name.upper() == activities[JSON_ATTR_ACT_NAME].upper():
            return ADD_403_FORBIDDEN
        json_database[JSON_ATTR_ACTIVITIES].append(ACT_TO_BE_ADDED)
    with open(f"{JSON_FPATH}{JSON_FNAME}", "w") as f:
      json.dump(json_database,f)
      return ADD_200_OK

  except Exception as e:
    print(e)
    return ADD_403_FORBIDDEN

"""
- This method represents the process of server listening for the client
- There are some variables defined which are useful to connect our JSON Database.
"""
def actv_server_listen(BUFF_SIZE,ADDR,FORMAT,ROOM_SERVER):
    """
          While server listening the incomning requests from clients, 
          if a proper request comes,the server should interact with the our simple database(JSON File). 
          Therefore, there are some necessary initializations exists below for accessing the JSON Database
    """

    while True:
        socket , address = ROOM_SERVER.accept()                                                             ## accept client
        print("\n-------------> [CONNECTION ACCCEPTED HOST IP || ADDRESS] --> " , socket ," || ",address)   ## server log message 
        message=socket.recv(BUFF_SIZE).decode(FORMAT)                                                       ## get client's message
      
        print(f"\n-------------> [CLIENT MESSAGE CAME BELOW] -->\n\n{message}")                             ## server log message

        server_response = ""
        parser_response=ap.main(message)
        try:
          if str(parser_response[0])==str(400):
              server_response=general_400_err
       
          elif str(parser_response[0])==str(404):
              server_response = general_404_err

          elif str(parser_response[0])==str(200):
            if str(parser_response[1])=="add":
              server_response=add_activity(str(parser_response[2]),JSON_FNAME,JSON_FPATH,JSON_ATTR_ACTIVITIES,JSON_ATTR_ACT_NAME)
            elif str(parser_response[1])=="remove":
              server_response=remove_activity(str(parser_response[2]),JSON_FNAME,JSON_FPATH,JSON_ATTR_ACTIVITIES,JSON_ATTR_ACT_NAME)
            elif str(parser_response[1])=="check":
              server_response=is_activity_exists(str(parser_response[2]),JSON_FNAME,JSON_FPATH,JSON_ATTR_ACTIVITIES,JSON_ATTR_ACT_NAME)
        except Exception as e:
          server_response=general_404_err        
        
        socket.send(server_response.encode(FORMAT))                                                                   ## sending proper http response to client
        print("-------------> [SENDING MESSAGE TO CLIENT] --> PROPER HTTP MESSAGE WILL BE SHOWN IN THE WEB BROWSER")  ## server log message
        socket.close()                                                                                                ## end session
        print(f"\n-------------> [CONNECTION CLOSING] --> Connection with {address} ended!")                          ## server log message
        print("\n********************************************   Cilent Session Log Messages Above   *********************************************************")

## Main method
if __name__ == "__main__":

    ## Socket attributes initializations
    BUFF_SIZE = 2048                                                     ## set the chunk size
    PORT = 5052                                                          ## set port for server
    SERVER = socket.gethostbyname(socket.gethostname())                  ## get hos ip
    ADDR = (SERVER, PORT)                                                ## fully address tupple
    FORMAT = 'utf-8'                                                     ## encode/decode format
    
    ## Room Server necessary initializations 
    ACTIVITY_SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  ## create socket
    ACTIVITY_SERVER.bind(ADDR)                                           ## binding
    ACTIVITY_SERVER.listen()                                             ## server up
    print(f"\n ////////////////////////// -> ACTIVITY SERVER IS CREATED AND READY TO LISTEN WITH THE ADDRESS OF {ADDR}] <- \\\\\\\\\\\\\\\\\\\\\\\\\\ \n")
    actv_server_listen(BUFF_SIZE,ADDR,FORMAT,ACTIVITY_SERVER)