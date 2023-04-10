import json
import socket 
import ReservationParser as res_parser ## Import parser
import os

## HTTP Error messages initialized
general_404_err = "HTTP/1.1 404 Not Found\nContent-Type: text/html\n\n<html><head><title>Error</title></head><body><h1>Page Not Found</h1></body></html>"
general_400_err = "HTTP/1.1 400 Bad Request\nContent-Type: text/html\n\n<html><head><title>Bad Request</title></head><body></body></html>"

"""There are some variables defined which are 
useful to connect our JSON Database."""

JSON_FNAME="reservations.json"
JSON_FPATH=os.getcwd() + '/'
JSON_ATTR_RESERVATIONS="reservations"
JSON_ATTR_RESERVATION_ID="reservation_id"
JSON_ATTR_ROOM_NAME="room_name"
JSON_ATTR_ACT_NAME="activity_name"
JSON_ATTR_DAY="day"
JSON_ATTR_INTERVAL="interval" 
def room_reserver(parser_response):

    activity_name = parser_response[3]
    # Send the HTTP GET request
    RESERVATION_TO_ACTIVITY_SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   ## create socket for room server
    ip_name = socket.gethostbyname(socket.gethostname())
    RESERVATION_TO_ACTIVITY_SERVER.connect((ip_name, 5052))
    request = f'GET /check?name={activity_name} HTTP/1.1\r\nHost: {ip_name}:5052\r\n\r\n'
    RESERVATION_TO_ACTIVITY_SERVER.sendall(request.encode())
    response_str = RESERVATION_TO_ACTIVITY_SERVER.recv(2048).decode()
    RESERVATION_TO_ACTIVITY_SERVER.close()
    if "200 OK" in response_str:
      room_name = parser_response[2]
      day = parser_response[4]
      hour = parser_response[5]  
      duration = parser_response[6] 
       # Send the HTTP GET request
      RESERVATION_TO_ROOM_SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   ## create socket for room server
      RESERVATION_TO_ROOM_SERVER.connect((ip_name,5051))
      request = f'GET /reserve?name={room_name}&day={day}&hour={hour}&duration={duration} HTTP/1.1\r\nHost: {ip_name}:5051\r\n\r\n'
      RESERVATION_TO_ROOM_SERVER.sendall(request.encode())
      response_str = RESERVATION_TO_ROOM_SERVER.recv(2048).decode()
      RESERVATION_TO_ROOM_SERVER.close()
      if "200 OK" in response_str:

        interval= f"{hour}:00 - {int(hour)+int(duration)}:00"
        try:
          with open(f"{JSON_FPATH}{JSON_FNAME}", "r") as f:
            json_reservation_database = json.load(f)
            res_length = len(json_reservation_database[JSON_ATTR_RESERVATIONS])
            RESERVATION_TO_BE_ADDED={
              "reservation_id": res_length,
              "room_name": room_name,
              "activity_name": activity_name,
              "day": day,
              "hour": hour,
              "interval": interval
            }   
            json_reservation_database[JSON_ATTR_RESERVATIONS].append(RESERVATION_TO_BE_ADDED)

          with open(f"{JSON_FPATH}{JSON_FNAME}", "w") as f:
            json.dump(json_reservation_database,f)
            return f"HTTP/1.1 200 OK\nContent-Type: text/html\n\n<html><body><h1>Reservation Added</h1><p>Reservation added with {RESERVATION_TO_BE_ADDED}.</p></body></html>"
        except:
          return general_404_err
      else:
        return response_str

    else:
      return  response_str

def list_availablity_day(parser_response):
    ip_name = socket.gethostbyname(socket.gethostname())
    room_name = parser_response[2]
    day = parser_response[3]
    # Send the HTTP GET request
    RESERVATION_TO_ROOM_SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   ## create socket for room server
    RESERVATION_TO_ROOM_SERVER.connect((ip_name, 5051))
    request = f'GET /checkavailability?name={room_name}&day={day} HTTP/1.1\r\nHost: {ip_name}:5051\r\n\r\n'
    RESERVATION_TO_ROOM_SERVER.sendall(request.encode())
    response = RESERVATION_TO_ROOM_SERVER.recv(2048).decode()
    RESERVATION_TO_ROOM_SERVER.close()

    return response

"""Lists all the available hours for all days of the week (after
contacting the Room Server probably several times). (HTTP 200 OK is returned in success. In
case of error relevant error messages will be sent as described above)."""
def list_availablity(parser_response):
    ip_name = socket.gethostbyname(socket.gethostname())
    room_name = parser_response[2]
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    result = []
    for i in range(1,7):
      # Send the HTTP GET request
      RESERVATION_TO_ROOM_SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   ## create socket for room server
      RESERVATION_TO_ROOM_SERVER.connect((ip_name,5051))
      request = f'GET /checkavailability?name={room_name}&day={i} HTTP/1.1\r\nHost: {ip_name}:5051\r\n\r\n'
      RESERVATION_TO_ROOM_SERVER.sendall(request.encode())
      response_str = RESERVATION_TO_ROOM_SERVER.recv(2048).decode()
      RESERVATION_TO_ROOM_SERVER.close()
      body = response_str.split("-")[2]
      iterate_day = f"{days_of_week[i-1]}: {body}\n"
      result.append(iterate_day)
    
    printed_result = ('\n'.join(map(str, result)))
    return f"HTTP/1.1 200 OK\nContent-Type: text/plain\n\nAvailable hours for the {room_name} on\n\n{printed_result}"

def display_reservation_id(parser_response):

    res_id = parser_response[2]
    res_details = {}
    LIST_200_OK = f"HTTP/1.1 200 OK\nContent-Type: text/html\n\n<html><body><p>Details about Reservation with id {res_id} is {res_details}.</p></body></html>"
    LIST_403_FORBIDDEN = f"HTTP/1.1 403 Forbidden\nContent-Type: text/html\n\n<html><body><h1>Error</h1><p>A reservation with the id {res_id} does not exists in the database.</p></body></html>"

    with open(f"{JSON_FPATH}{JSON_FNAME}", "r") as f:
      json_database = json.load(f)

    reservations = json_database[JSON_ATTR_RESERVATIONS]
    found_flag = False
    for i, reservation in enumerate(reservations):
      if str(reservation[JSON_ATTR_RESERVATION_ID]) == str(res_id):
        found_flag = True
        res_details = reservation
        break

    if not found_flag:
      return LIST_403_FORBIDDEN

    return f"HTTP/1.1 200 OK\nContent-Type: text/html\n\n<html><body><p>Details about Reservation with id {res_id} is {res_details}.</p></body></html>"


"""
This method represents the process of server listening for the client
"""
def reservation_server_listen(BUFF_SIZE,ADDR,FORMAT,RESERVATION_SERVER):

    while True:
        socket , address = RESERVATION_SERVER.accept()                                                      ## accept client
        print("\n-------------> [CONNECTION ACCCEPTED HOST IP || ADDRESS] --> " , socket ," || ",address)   ## server log message
        message=socket.recv(BUFF_SIZE).decode(FORMAT)                                                       ## get client's message
        print(f"\n-------------> [CLIENT MESSAGE CAME BELOW] -->\n\n{message}")                           ## server log message
        print(message)

        server_response = ""
        parser_response=res_parser.main(message)

        try:
          if str(parser_response[0])==str(400):
                server_response=general_400_err
        
          elif str(parser_response[0])==str(404):
                server_response = general_404_err

          elif str(parser_response[0])==str(200):     

            if str(parser_response[1])=="reserve":
              server_response=room_reserver(parser_response)
            elif str(parser_response[1])=="listavailability":
              if (len(parser_response) == 3):
                  server_response=list_availablity(parser_response)
              else:                 
                  server_response=list_availablity_day(parser_response)

            elif str(parser_response[1])=="display":                 
                server_response=display_reservation_id(parser_response)
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
    PORT = 5050                                                       ## set port for server
    SERVER = socket.gethostbyname(socket.gethostname())               ## get hos ip
    ADDR = (SERVER, PORT)                                             ## fully address tupple
    FORMAT = 'utf-8'                                                  ## encode/decode format
  
    RESERVATION_SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   ## create socket for reservation server
    RESERVATION_SERVER.bind(ADDR)                                            ## binding
    RESERVATION_SERVER.listen()                                              ## server up  

    print(f"\n////////////////////////// -> RESERVATION SERVER IS CREATED AND READY TO LISTEN WITH THE ADDRESS OF {ADDR}] <- \\\\\\\\\\\\\\\\\\\\\\\\\\\n")
    reservation_server_listen(BUFF_SIZE,ADDR,FORMAT,RESERVATION_SERVER)