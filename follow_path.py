import json
import requests
import time
from queue import SimpleQueue as Q
import os


# sets variables for making post requests to the server
token = os.environ["SERVER_KEY"]
url = 'https://lambda-treasure-hunt.herokuapp.com/api/adv/'
headers = {
    'Authorization': f'Token {token}', 
    'Content-Type': 'application/json'
}
hr = "---------------------------------"


# Class houses follow path functions
class Follow():
    def __init__(self, map, end, verbosity=0):
        self.map = None
        self.start = 0
        self.end = end
        self.ve = int(verbosity)
        self.q = Q()
        self.load_map(map)

    # Loads the map file
    def load_map(self, mapfile):
        with open(mapfile) as json_file:
            self.map = json.load(json_file)
            if self.ve >= 2:
                print('Loaded map: \n', self.map)

        self.run()

    # This pulls everything together
    # Finds path to room
    # Finds directions to room room id 55 -> 475
    def run(self):
        actual_start = None
        try:
            actual_start = self.where_am_i()
        except:
            print("ERROR: You must find yourself.")
            return

        path = self.find_room(actual_start)
        directions = self.get_directions(path)
        if self.ve >= 1:
            print(f"\nDirections from {actual_start} (not {self.start}) to {self.end}: \n {directions}")

        self.start = actual_start
        self.follow_path(directions, actual_start)

    # gets the path and directions to follow that path
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
        return(directions)

    # follows the path with the directions
    def follow_path(self, directions, start):
        current_room = start
        for direct in directions:
            action = "move/"
            next_room = str(self.map[str(current_room)][direct])
            data = {"direction": f"{direct}", "next_room_id": f"{next_room}"}
            resp = requests.post(f"{url}{action}",
                                data=json.dumps(data),
                                headers=headers
                                )
            temp_content = json.loads(resp.content)
            chillout = temp_content['cooldown']

            if self.ve >= 1:
                print(f"\n {hr}")
                print(f"Response from {url}{action}")
                print(f" response = {resp}")
                # print(f" response content = {resp.content}")
                print(f" chill = {chillout}s")
                print(f" room id = {temp_content['room_id']}")
                print(f" title = {temp_content['title']}")
                print(f" description = {temp_content['description']}")
                print(f" elevation = {temp_content['elevation']}")
                print(f" terrain = {temp_content['terrain']}")
                print(f" coordinates = {temp_content['coordinates']}")
                print(f" current room = {temp_content['room_id']}")
                print(f" items in room = {temp_content['items']}")
                print(f" exits = {temp_content['exits']}")
                print(f" players in room = {temp_content['players']}")
                print(f" messages = {temp_content['messages']}")

            items = temp_content['items']

            if len(items) > 0:
                self.pick_up_items(items)

            time.sleep(int(chillout + 2))

    def pick_up_items(self, item_array):
        action = "take/"
        treasure = {"name": item_array[0]}
        pickup = requests.post(f"{url}{action}",
                            data=treasure,
                            headers=headers 
                            )
        if self.ve >= 1:
                print(f"\n {hr}")
                print(f"Response from {url}{action}")
                print(f" response = {resp}")
                print(f" pickup content ", pickup.content)

        time.sleep(15)
        self.who_am_i()

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
            print(f" messages = {json_response['messages']} \n {hr}")
        time.sleep(int(chill))
    
    def where_am_i(self):
        action = "init/"
        resp = requests.get(f"{url}{action}", headers=headers )
        json_response = json.loads(resp.content)
        chill = json_response['cooldown']
        if self.ve >= 2:
            print(f"\n {json_response} \n")
        if self.ve >= 1:
            print(f"\n{hr}\nResponse from {url}{action} \n {resp}")
            print(f"\n room_id = {json_response['room_id']}\n")
        resp.close()
        time.sleep(int(chill))
        self.who_am_i()
        return str(json_response['room_id'])

            