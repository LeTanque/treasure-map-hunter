import json
import requests
import time
from queue import SimpleQueue as Q
import os


# Globals
token = os.environ["SERVER_KEY"]
url = 'https://lambda-treasure-hunt.herokuapp.com/api/adv/'
bc_url = 'https://lambda-treasure-hunt.herokuapp.com/api/bc/'
headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}
hr = "---------------------------------"


# List to string 
def list_string(s):
    string = ","
    return string.join(s)


# Class houses follow path functions
class Follow():
    def __init__(self, map, end=0, command=None):
        self.map = None
        self.start = 0
        self.end = end
        self.ve = 1
        self.cmd = command
        self.auto_pickup = False
        # self.ve = int(verbosity)
        # self.direction = direction
        self.q = Q()
        self.load_map(map)

    # Loads the map file
    def load_map(self, mapfile):
        with open(mapfile) as json_file:
            self.map = json.load(json_file)
            if self.ve >= 1:
                print(f"Map length: {len(self.map)}")
            if self.ve >= 2:
                print('Loaded map: \n', self.map)
        self.run()

    # This pulls everything together
    # Finds path to room
    # Finds directions to room room id 55 -> 475
    def run(self):
        where_in_the_world = None
        status = None
        actual_start = self.start
        try:
            status = self.who_am_i()
            where_in_the_world = self.where_am_i()
            actual_start = str(where_in_the_world["room_id"])
        except:
            print("WAIT: You must find yourself.")
        
        # This logic processes commands given on CLI
        if self.cmd == "find":
            self.find_path(actual_start, "find")

        elif self.cmd == "dash":
            self.find_path(actual_start, "dash")
   
        elif self.cmd == "fly":
            self.find_path(actual_start, "fly")

        elif self.cmd == "sell":
            self.sell_treasure(status)

        elif self.cmd == "status":
            print(f"{hr}")

        elif self.cmd == "pray":
            self.pray()
        
        elif self.cmd == "changename":
            self.change_name()

        elif self.cmd == "pickup":
            self.pick_up_items(where_in_the_world["items"])

        elif self.cmd == "examineplace":
            self.examine(where_in_the_world["title"])

        elif self.cmd == "examineplayer":
            self.examine(where_in_the_world["players"][0])

        elif self.cmd == "balance":
            self.balance()

        else:
            print(f"Valid commands are find, dash, fly, sell, status, pray, changename, pickup, examineplace, examineplayer, balance")

    # gets the path and directions to follow that path
    def find_path(self, start, travel_method):
        path = self.find_room(start)
        directions = self.get_directions(path)
        
        if travel_method is "find":
            self.follow_path(directions, start)
        if travel_method is "dash":
            self.dash_prepare(directions, path, start)
        if travel_method is "fly":
            self.follow_path(directions, start, True)

    def find_room(self, starter):
        self.q.put([starter])
        visited = set()
        while self.q.qsize() > 0:
            path = self.q.get()
            last_room = path[-1]
            if last_room == self.end:
                return(path)
            if last_room not in visited:
                visited.add(last_room)
                for next in self.map[last_room]:
                    if next == 'info':
                        break
                    if self.map[last_room][next] != '?':
                        new_path = path.copy()
                        new_path.append(str(self.map[last_room][next]))
                        self.q.put(new_path)

    # a function to get the directions needed to follow an input path
    def get_directions(self, path):
        directions = []
        temp_path = []
        for x in path:
            temp_path.append(str(x))
        path = temp_path
        for i in range(len(path)-1):
            dirs = self.map[path[i]]
            for dir in dirs:
                if str(self.map[path[i]][dir]) == str((path[i+1])):
                    directions.append(dir)
        return directions

    # Executes the moves to follow the path
    def follow_path(self, directions, start, fly=False):
        current_room = start

        if self.ve >= 1:
            print(f"\n {hr}")
            print(f"Directions from {start} to {self.end}: \n {directions}")

        for direct in directions:
            next_room = self.map[current_room][str(direct)]
            if fly is True:
                action = "fly/"
                data = {'direction': f'{direct}', 'next_room_id': f'{str(next_room)}'}
                resp = requests.post(f"{url}{action}", data=json.dumps(data), headers=headers )
            else:
                action = "move/"
                data = {'direction': f'{direct}', 'next_room_id': f'{str(next_room)}'}
                resp = requests.post(f"{url}{action}", data=json.dumps(data), headers=headers )

            json_response = json.loads(resp.content)
            chillout = json_response['cooldown']

            if self.ve >= 1:
                print(f'   next_room in follow path: {next_room} \n   direct: {direct} \n   directions: {directions} ')
                self.movement_message(action, resp, json_response)
                if fly is True:
                    print(f"\n\
                   _/\n\
  _/_/_/_/_/  _/  _/    _/_/_/  _/          _/\n\
         _/  _/  _/  _/        _/_/_/    _/_/_/_/\n\
      _/    _/  _/  _/  _/_/  _/    _/    _/\n\
   _/      _/  _/  _/    _/  _/    _/    _/\n\
_/        _/  _/    _/_/_/  _/    _/      _/_/\n\
             _/\n\
            _/\n\
                    ")

            time.sleep(int(chillout + 1))

            if self.auto_pickup is True:
                items = json_response['items']
                if len(items) > 0:
                    self.pick_up_items(items)
            current_room = str(next_room)

    def dash_prepare(self, directions, path, start):
        if self.ve >= 1:
            print(f"\n {hr}")
            print(f"Directions from {start} to {self.end}: \n {directions} \n  {path[1:]}")
        
        if len(directions) <= 1:
            print(f"  WARNING: path too short to dash")
            self.follow_path(directions, start)
        
        corrected_path = path[1:]
        dash_direction = {}
        dash_path = []
        dash_direction["compass"] = directions[0]

        while len(corrected_path) != 0:
            for eachway in directions:
                print(f"Each way: {eachway}")
                if dash_direction["compass"] == eachway:
                    dash_path.append(corrected_path.pop(0))
                    print(f" this is the way {dash_path}")
                if dash_direction["compass"] != eachway:
                    print(f" this is the way if direction != eachway {dash_path}")
                    # Execute a dash with given direction and paths
                    self.dash(dash_direction["compass"], dash_path)
                    # set new direction
                    dash_direction["compass"] = eachway
                    # clear the path
                    dash_path = []
                    # Add first move in new direction
                    dash_path.append(corrected_path.pop(0))

    def dash(self, direct, path_array):
        action = "dash/"
        num_of_rooms = len(path_array)
        dash_coordinates = {'direction': f'{direct}', 'num_rooms': f'{num_of_rooms}', 'next_room_ids': f'{list_string(path_array)}'}
        dasher = requests.post(f"{url}{action}", data=json.dumps(dash_coordinates), headers=headers )
        json_response = json.loads(dasher.content)
        chill = json_response['cooldown']

        print(f'\n   dash_coordinates: \n   {dash_coordinates} \n   json: \n   {json_response["messages"]}')
        if self.ve >= 1:
            self.movement_message(action, dasher, json_response)
            print(f"\n\
         _/                      _/\n\
    _/_/_/    _/_/_/    _/_/_/  _/_/_/\n\
 _/    _/  _/    _/  _/_/      _/    _/\n\
_/    _/  _/    _/      _/_/  _/    _/\n\
 _/_/_/    _/_/_/  _/_/_/    _/    _/\n\
")

        time.sleep(int(chill))
        time.sleep(.3)

    def flight(self, direction):
        # curl -X POST -H 'Authorization: Token 7a375b52bdc410eebbc878ed3e58b2e94a8cb607' 
        # -H "Content-Type: application/json" -d '{"direction":"n"}' https://lambda-treasure-hunt.herokuapp.com/api/adv/fly/
        action = "fly/"
        flight_data = {'direction': f'{direction}'}
        fly_me_a_river = requests.post(f"{url}{action}", data=json.dumps(flight_data), headers=headers )
        json_response = json.loads(fly_me_a_river.content)
        chill = json_response['cooldown']
        time.sleep(int(chill))
        time.sleep(.3)


    def pick_up_items(self, item_array):
        action = "take/"
        item = item_array[0]
        treasure = {'name': f'{item}'}
        pickup = requests.post(f"{url}{action}", data=json.dumps(treasure), headers=headers )
        json_response = json.loads(pickup.content)
        chill = json_response['cooldown']

        if self.ve >= 1:
                print(f"\n {hr}")
                print(f"Response from {url}{action}")
                print(f" pickup content ", pickup.content)

        time.sleep(int(chill))
        time.sleep(.3)
        self.who_am_i()

    def sell_treasure(self, status):
        items = status["inventory"]
        action = "sell/"
        treasure = {'name': f'{items[0]}', 'confirm':'yes'}
        sell = requests.post(f"{url}{action}", data=json.dumps(treasure), headers=headers )
        json_response = json.loads(sell.content)
        chill = json_response['cooldown']

        if self.ve >= 1:
                print(f"\n {hr}")
                print(f"Response from {url}{action}")
                print(f" sell treasure ", sell.content["messages"])

        time.sleep(int(chill))
        time.sleep(.3)

    def pray(self):
        action = "pray/"
        prayer = requests.post(f"{url}{action}", headers=headers )
        json_response = json.loads(prayer.content)
        chill = json_response['cooldown']

        if self.ve >= 1:
                print(f"\n {hr}")
                print(f"Response from {url}{action}")
                print(f" ... praying ... ", json_response["messages"])
                print(f" ... praying ... ", json_response)

        time.sleep(int(chill))
        time.sleep(.3)

    def change_name(self):
        new_name = "LeTanque"
        action = "change_name/"
        treasure = {'name': f'{new_name}', 'confirm':'aye'}
        name_change = requests.post(f"{url}{action}", data=json.dumps(treasure), headers=headers )
        json_response = json.loads(name_change.content)
        chill = json_response['cooldown']

        if self.ve >= 1:
            print(f"\n {hr}")
            print(f"Response from {url}{action}")
            print(f" name changed to {new_name}", json_response["messages"])

        time.sleep(int(chill))
        time.sleep(.3)

    def examine(self, query):
        # '{"name":"[NAME OF ITEM OR PLAYER]"}' 
        action = "examine/"
        treasure = {'name': f'{query}'}
        examiner = requests.post(f"{url}{action}", data=json.dumps(treasure), headers=headers )
        json_response = json.loads(examiner.content)
        chill = json_response['cooldown']

        if self.ve >= 1:
            print(f"\n {hr}")
            print(f"Response from {url}{action}")
            print(f" examining {query}", json_response["description"], f"\n  {json_response}")

        time.sleep(int(chill))
        time.sleep(.3)

    def balance(self):
        action = "get_balance/"
        response = requests.get(f"{bc_url}{action}", headers=headers )
        json_response = json.loads(response.content)
        chill = json_response['cooldown']

        if self.ve >= 1:
            print(f"\n {hr}")
            print(f"Response from {url}{action}")
            print(f" Lambda coin balance:", f" {json_response['messages'][0]}")

        time.sleep(int(chill))
        time.sleep(.3)


    def where_am_i(self):
        action = "init/"
        resp = requests.get(f"{url}{action}", headers=headers )
        json_response = json.loads(resp.content)
        chill = json_response['cooldown']

        if self.ve >= 2:
            print(f"\n {json_response} \n")

        if self.ve >= 1:
            self.movement_message(action, resp, json_response)
        
        resp.close()
        time.sleep(int(chill))
        return json_response

    def who_am_i(self):
        action = "status/"
        resp = requests.post(f"{url}{action}", headers=headers )
        json_response = json.loads(resp.content)
        chill = json_response['cooldown']

        if self.ve >= 1:
            print(f"\n {hr}")
            print(f"Response from {url}{action}")
            print(f" response = {resp}")
            print(f" chill = {chill}s")
            print(f" name = {json_response['name']}")
            print(f" encumbrance = {json_response['encumbrance']}")
            print(f" strength = {json_response['strength']}")
            print(f" speed = {json_response['speed']}")
            print(f" gold = {json_response['gold']}")
            print(f" bodywear = {json_response['bodywear']}")
            print(f" footwear = {json_response['footwear']}")
            print(f" inventory = {json_response['inventory']}")
            print(f" abilities = {json_response['abilities']}")
            print(f" status = {json_response['status']}")
            print(f" has_mined = {json_response['has_mined']}")
            print(f" errors = {json_response['errors']}")
            print(f" messages = {json_response['messages']} \n")
        
        time.sleep(int(chill))
        time.sleep(.3)
        return json_response
    
    def movement_message(self, action, response, json_response):
        cooldown = json_response['cooldown']
        print(f"\n {hr}")
        print(f"Response from {url}{action}")
        print(f" response = {response}")
        print(f" chill = {cooldown}s")
        print(f" room id = {json_response['room_id']}")
        print(f" title = {json_response['title']}")
        print(f" description = {json_response['description']}")
        print(f" elevation = {json_response['elevation']}")
        print(f" terrain = {json_response['terrain']}")
        print(f" coordinates = {json_response['coordinates']}")
        print(f" items in room = {json_response['items']}")
        print(f" exits = {json_response['exits']}")
        print(f" players in room = {json_response['players']}")
        print(f" messages = {json_response['messages']}")
