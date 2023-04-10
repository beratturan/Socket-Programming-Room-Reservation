import json
import socket 
import RoomParser as rp ## Import parser
import os

## HTTP Error messages initialized
general_404_err = "HTTP/1.1 404 Not Found\nContent-Type: text/html\n\n<html><head><title>Error</title></head><body><h1>Page Not Found</h1></body></html>"
general_400_err = "HTTP/1.1 400 Bad Request\nContent-Type: text/html\n\n<html><head><title>Bad Request</title></head><body></body></html>"

JSON_FNAME="rooms.json"
JSON_FPATH=os.getcwd() + '/'
JSON_ATTR_ROOMS="rooms"
JSON_ATTR_ROOM_NAME="room_name"
JSON_ATTR_SCHED="schedule"
JSON_ATTR_DAY="day"
JSON_ATTR_UNRES="unres_hours" 
JSON_ATTR_RES="res_hours" 

"""
This method checks the availabilty of the room by interacting JSON Database. Method interacts the JSON Database 
by using its parameter which are arranged in main. 
- To prepare proper http message, day of the week obtained by using given day parameter (DAY_STRING)
- Method interacts to JSON Database and gets the unreserved hours values of requested day by comparing room names in JSON and
  given parameter
- Once it get the unreserved hours of the day, method arranges to data for the proper http response.
- If requested room does not exist, method returns a proper http 404 message as a server response for future use.
"""
def check_availability(given_name,given_day,
                      JSON_FNAME,JSON_FPATH,JSON_ATTR_ROOMS,JSON_ATTR_ROOM_NAME,
                      JSON_ATTR_SCHED,JSON_ATTR_DAY,JSON_ATTR_UNRES):
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    given_day = int(given_day)
    DAY_STRING=days_of_week[given_day - 1]
    try:
        with open(f"{JSON_FPATH}{JSON_FNAME}", "r") as f:
            json_database = json.load(f)

        for room in json_database[JSON_ATTR_ROOMS]:
            if str(room[JSON_ATTR_ROOM_NAME]).upper() == str(given_name).upper():
                for schedule in room[JSON_ATTR_SCHED]:
                    if str(schedule[JSON_ATTR_DAY]) == str(given_day):
                        available_hours = schedule[JSON_ATTR_UNRES]
                        formatted_hours = [f"{hour}:00" for hour in available_hours]
                        body = " ".join(formatted_hours)
                        return f"HTTP/1.1 200 OK\nContent-Type: text/plain\n\nAvailable hours for the {given_name} on {DAY_STRING} -  {body}"
        
        return f"HTTP/1.1 404 Not Found\nContent-Type: text/html\n\n<html><head><title>Error</title></head><body><h1>Not Found</h1><p>No room named {given_name} found on the database.</p></body></html>"
    except Exception as e:
        return f"HTTP/1.1 404 Not Found\nContent-Type: text/html\n\n<html><body><p>Somethings went wrog :/.</p></body></html>"

"""
This method deletes the record of requested room which is indicated by name in client's request message.
- Special http responses defined in the method(200, 403).
- Method uses a flag variable to check if requested room is exits in database or not
- Once method loads the JSON data into a python dictionary, it searches given room name by using loop and enumerator. 
  When given room is found, method deltes the record in dictionary according to given room name's index.
- Method returns proper http messages as a response in different conditions.
"""
def remove_room(givenRoomName,JSON_FNAME,JSON_FPATH,JSON_ATTR_ROOMS,JSON_ATTR_ROOM_NAME):
  
  RMV_200_OK = f"HTTP/1.1 200 OK\nContent-Type: text/html\n\n<html><body><h1>Room Removed</h1><p>Room with name {givenRoomName} is successfully removed.</p></body></html>"
  RMV_403_FORBIDDEN = f"HTTP/1.1 403 Forbidden\nContent-Type: text/html\n\n<html><body><h1>Error</h1><p>A room with the name {givenRoomName} does not exists in the database.</p></body></html>"
  
  with open(f"{JSON_FPATH}{JSON_FNAME}", "r") as f:
    json_database = json.load(f)

  rooms = json_database[JSON_ATTR_ROOMS]
  found_flag = False
  for i, room in enumerate(rooms):
    if str(room[JSON_ATTR_ROOM_NAME]).upper() == str(givenRoomName).upper():
      del rooms[i]
      found_flag = True
      break

  if not found_flag:
    return RMV_403_FORBIDDEN

  with open(f"{JSON_FPATH}{JSON_FNAME}", "w") as f:
    json.dump(json_database, f)
  return RMV_200_OK

"""
This method reserves the room according to given day, hour and duration values. Reservation process is done by arranging JSON file.
In room object in JSON Database, There are 2 lists which are represents to unreserved and reserved hours of each day.
- In the method, there are some variables defined for proper http response. DAY_STRING is word representation of the day of week and
  INTERVAL is the representation for reservation hours interval.
- Proper http messages defined for different conditions.
- Method uses flag variable to check if given room is exists in the database or not.
- Once method found the given room in the database, it gets the reserved and unreserved hours list of the matching day.
- Method controls if given hours is already reserved. It takes given hour and duration and with the help of list comprehension, 
  method checks reserved hour list to controls if requested hours is in the or not.
- If requested hours are not allocated, method arranges the unreserved hours and hours lists by using list comprehension.
- Method returns proper http responses for different conditions.
"""
def reserve_room(given_room_name,given_day,given_hour,given_duration,
                      JSON_FNAME,JSON_FPATH,JSON_ATTR_ROOMS,JSON_ATTR_ROOM_NAME,
                      JSON_ATTR_SCHED,JSON_ATTR_DAY,JSON_ATTR_UNRES,JSON_ATTR_RES):
  
  given_day = int(given_day)
  given_hour = int(given_hour)
  given_duration = int(given_duration)
  days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
  DAY_STRING=days_of_week[given_day - 1]
  get_time_range = lambda hour, duration: f"{given_hour}:00 - {given_hour + given_duration}:00"
  INTERVAL = get_time_range(given_hour,given_duration)

  RES_200_OK = f"HTTP/1.1 200 OK\nContent-Type: text/html\n\n<html><body><h1>Reservation Successful</h1><p>Room with name {given_room_name} is successfully reserved on {DAY_STRING} {INTERVAL}.</p></body></html>"
  RES_403_FORBIDDEN_NOT_EXISTS = f"HTTP/1.1 403 Forbidden\nContent-Type: text/html\n\n<html><body><h1>Error</h1><p>A room with the name {given_room_name} does not exists in the database.</p></body></html>"
  RES_403_FORBIDDEN = f"HTTP/1.1 403 Forbidden\nContent-Type: text/html\n\n<html><body><h1>Error</h1><p>A room with the name {given_room_name} is already reserved.</p></body></html>"
  RES_404_NOT_FOUNT = f"HTTP/1.1 404 Not found\nContent-Type: text/html\n\n<html><body><h1>Sorry :/</h1><p>Somethings go wrong :/</p></body></html>"
  
  try:
    flag= False
    
    with open(f"{JSON_FPATH}{JSON_FNAME}", "r") as f:
      json_database = json.load(f)
      
      if json_database[JSON_ATTR_ROOMS] == []:
        return RES_403_FORBIDDEN_NOT_EXISTS
      else:
        for room in json_database[JSON_ATTR_ROOMS]:
    
          if room[JSON_ATTR_ROOM_NAME].upper() == given_room_name.upper():
            flag=True
            requested_schedule = room[JSON_ATTR_SCHED]
            for day_info in requested_schedule:
              if int(day_info[JSON_ATTR_DAY]) == int(given_day):
                unres_hours = day_info[JSON_ATTR_UNRES]
                res_hours = day_info[JSON_ATTR_RES]
                if any(h in res_hours for h in range(given_hour, given_hour + given_duration)):
                  return RES_403_FORBIDDEN
                unres_hours = [h for h in unres_hours if h < given_hour or h > given_hour + given_duration]
                res_hours += list(range(given_hour, given_hour + given_duration + 1))
                day_info[JSON_ATTR_RES] = res_hours
                day_info[JSON_ATTR_UNRES] = unres_hours
      if not flag:
        return RES_403_FORBIDDEN_NOT_EXISTS
      with open(f"{JSON_FPATH}{JSON_FNAME}", "w") as f:
          json.dump(json_database,f)
          return RES_200_OK
  except Exception as e:
    return RES_404_NOT_FOUNT

"""
This method adds new record of requested room which is indicated in client's request message.
- Special http responses defined in the method(200, 403).
- If our JSON database is empty method immediately adds the given room record.
- Once method loads the JSON data into a python dictionary, it appends the new room record whose structure is already defined in the function to the room list of JSON database.
- Method returns proper http messages as a response in different conditions.
"""
def add_room(given_name,JSON_FNAME,JSON_FPATH,JSON_ATTR_ROOMS,JSON_ATTR_ROOM_NAME):

  ADD_200_OK = f"HTTP/1.1 200 OK\nContent-Type: text/html\n\n<html><body><h1>Room Added</h1><p>Room with name {given_name} is successfully added.</p></body></html>"
  ADD_403_FORBIDDEN = f"HTTP/1.1 403 Forbidden\nContent-Type: text/html\n\n<html><body><h1>Error</h1><p>A room with the name {given_name} already exists in the database.</p></body></html>"
  ROOM_TO_BE_ADDED={
      "room_name": given_name.upper(),
      "schedule":
      [{"day": 1,"unres_hours": [9, 10, 11, 12, 13, 14, 15, 16, 17],"res_hours":[]},
      {"day": 2,"unres_hours": [9, 10, 11, 12, 13, 14, 15, 16, 17],"res_hours":[]},
      {"day": 3,"unres_hours": [9, 10, 11, 12, 13, 14, 15, 16, 17],"res_hours":[]},
      {"day": 4,"unres_hours": [9, 10, 11, 12, 13, 14, 15, 16, 17],"res_hours":[]},
      {"day": 5,"unres_hours": [9, 10, 11, 12, 13, 14, 15, 16, 17],"res_hours":[]},
      {"day": 6,"unres_hours": [9, 10, 11, 12, 13, 14, 15, 16, 17],"res_hours":[]},
      {"day": 7,"unres_hours": [9, 10, 11, 12, 13, 14, 15, 16, 17],"res_hours":[]}]
  }

  try:
    with open(f"{JSON_FPATH}{JSON_FNAME}", "r") as f:
      json_room_database = json.load(f)
      if json_room_database[JSON_ATTR_ROOMS] == []:
        json_room_database[JSON_ATTR_ROOMS].append(ROOM_TO_BE_ADDED)
      else:
        for room in json_room_database[JSON_ATTR_ROOMS]:
          if given_name.upper() == room[JSON_ATTR_ROOM_NAME].upper():
            return ADD_403_FORBIDDEN
        json_room_database[JSON_ATTR_ROOMS].append(ROOM_TO_BE_ADDED)
    with open(f"{JSON_FPATH}{JSON_FNAME}", "w") as f:
      json.dump(json_room_database,f)
      return ADD_200_OK

  except Exception as e:
    print(e)
    return ADD_403_FORBIDDEN

"""
- This method represents the process of server listening for the client
- There are some variables defined which are useful to connect our JSON Database.
"""
def room_server_listen(BUFF_SIZE,ADDR,FORMAT,ROOM_SERVER):
    """
          While server listening the incomning requests from clients, 
          if a proper request comes,the server should interact with the our simple database(JSON File). 
          Therefore, there are some necessary initializations exists below for accessing the JSON Database
    """
    
    while True:
        socket , address = ROOM_SERVER.accept()                                                             ## accept client
        print("\n-------------> [CONNECTION ACCCEPTED HOST IP || ADDRESS] --> " , socket ," || ",address)   ## server log message
        message=socket.recv(BUFF_SIZE).decode(FORMAT)                                                       ## get client's message
        print(f"\n-------------> [CLIENT MESSAGE CAME BELOW] -->\n\n{message}")                             ## server log message
        server_response = ""
        parser_response=rp.main(message)
        try:
          if str(parser_response[0])==str(400):
              server_response=general_400_err
       
          elif str(parser_response[0])==str(404):
              server_response = general_404_err

          elif str(parser_response[0])==str(200):
            if str(parser_response[1])=="add":
              server_response=add_room(str(parser_response[2]),JSON_FNAME,JSON_FPATH,JSON_ATTR_ROOMS,JSON_ATTR_ROOM_NAME)
            elif str(parser_response[1])=="remove":
              server_response=remove_room(str(parser_response[2]),JSON_FNAME,JSON_FPATH,JSON_ATTR_ROOMS,JSON_ATTR_ROOM_NAME)
            elif str(parser_response[1])=="checkavailability":
              server_response=check_availability(str(parser_response[2]),int(parser_response[3]),
                      JSON_FNAME,JSON_FPATH,JSON_ATTR_ROOMS,JSON_ATTR_ROOM_NAME,
                      JSON_ATTR_SCHED,JSON_ATTR_DAY,JSON_ATTR_UNRES)
            elif str(parser_response[1])=="reserve":
              server_response=reserve_room(str(parser_response[2]),int(parser_response[3]),int(parser_response[4]),
                      int(parser_response[5]),JSON_FNAME,JSON_FPATH,JSON_ATTR_ROOMS,JSON_ATTR_ROOM_NAME,
                      JSON_ATTR_SCHED,JSON_ATTR_DAY,JSON_ATTR_UNRES,JSON_ATTR_RES)
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
    BUFF_SIZE = 2048                                                  ## set the chunk size
    PORT = 5051                                                       ## set port for server
    SERVER = socket.gethostbyname(socket.gethostname())               ## get hos ip
    ADDR = (SERVER, PORT)                                             ## fully address tupple
    FORMAT = 'utf-8'                                                  ## encode/decode format
    
    ## Room Server necessary initializations    
    ROOM_SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   ## create socket
    ROOM_SERVER.bind(ADDR)                                            ## binding
    ROOM_SERVER.listen()                                              ## server up
    print(f"\n/////////////////////////// -> ROOM SERVER IS CREATED AND READY TO LISTEN WITH THE ADDRESS OF {ADDR}] <- \\\\\\\\\\\\\\\\\\\\\\\\\\\\n")
    room_server_listen(BUFF_SIZE,ADDR,FORMAT,ROOM_SERVER)