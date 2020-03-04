import json
import requests
import time
from queue import SimpleQueue as Q
import os


# sets variables for making post requests to the server
token = os.environ["SERVER_KEY"]
url = 'https://lambda-treasure-hunt.herokuapp.com/api/adv/'
headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}
hr = "---------------------------------"


# Class houses follow path functions
class Follow():
    def __init__(self, map, end=0, command=None):
        self.map = None
        self.start = 0
        self.end = end
        self.ve = 1
        self.cmd = command
        self.pick_up_things = False
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
        actual_start = self.start
        status = self.who_am_i()
        try:
            actual_start = self.where_am_i()
        except:
            print("ERROR: You must find yourself.")
            return
        
        # This logic processes commands given on CLI
        if self.cmd == "find":
            self.find_path(actual_start)

        elif self.cmd == "sell":
            self.sell_treasure(status)

        elif self.cmd == "status":
            print(f"{hr}")

        elif self.cmd == "pray":
            self.pray()
        
        elif self.cmd == "changename":
            self.change_name()

        else:
            print(f"Valid commands are find, sell, status, pray, changename")

    # gets the path and directions to follow that path
    def find_path(self, start):
        path = self.find_room(start)
        directions = self.get_directions(path)
        if self.ve >= 1:
            print(f"\n {hr}")
            print(f"Directions from {start} to {self.end}: \n {directions}")
        self.follow_path(directions, start)

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
    def follow_path(self, directions, start):
        current_room = start
        for direct in directions:
            action = "move/"
            next_room = self.map[current_room][str(direct)]

            print(f'   next_room in follow path: {next_room} \n   direct: {direct} ')

            data = {'direction': f'{direct}', 'next_room_id': f'{str(next_room)}'}
            resp = requests.post(f"{url}{action}", data=json.dumps(data), headers=headers )
            temp_content = json.loads(resp.content)
            chillout = temp_content['cooldown']

            if self.ve >= 1:
                print(f"\n {hr}")
                print(f"Response from {url}{action}")
                print(f" response = {resp}")
                print(f" chill = {chillout}s")
                print(f" room id = {temp_content['room_id']}")
                print(f" title = {temp_content['title']}")
                print(f" description = {temp_content['description']}")
                print(f" elevation = {temp_content['elevation']}")
                print(f" terrain = {temp_content['terrain']}")
                print(f" coordinates = {temp_content['coordinates']}")
                print(f" items in room = {temp_content['items']}")
                print(f" exits = {temp_content['exits']}")
                print(f" players in room = {temp_content['players']}")
                print(f" messages = {temp_content['messages']}")

            time.sleep(int(chillout + 2))

            if self.pick_up_things is True:
                items = temp_content['items']
                if len(items) > 0:
                    self.pick_up_items(items)
            current_room = str(next_room)

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
                print(f" sell treasure ", sell.content)
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
                print(f" ... praying ... ", prayer.content)
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
                print(f" name changed to {new_name} \n {name_change.content}")
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
            print(f"\n {hr}")
            print(f"Response from {url}{action}")
            print(f"\n room_id = {json_response['room_id']}")
            print(f" exits = {json_response['exits']}\n")
        resp.close()
        time.sleep(int(chill))
        return str(json_response['room_id'])

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
