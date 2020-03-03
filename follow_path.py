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
    def __init__(self, map, start, end, verbosity=0):
        self.map = None
        self.start = start
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
            print(f" Directions from {actual_start} (not {self.start}) to {self.end}: \n {directions}")

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
            print(f" >>> current_room \n {current_room} \n {self.map[str(current_room)][direct]} \n {direct} ")
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
                print(f" chill = {chillout}s")
                print(f" response content = {resp.content}")
                print(f" current room = {temp_content['room_id']}")
                print(f" items in room = {temp_content['items']}")
                print(f" exits = {temp_content['exits']}")
                print(f" players in room = {temp_content['players']}")

            current_room = temp_content['room_id']
            # items = temp_content['items']

            print(f"moved to {current_room}")
            time.sleep(int(chillout + 2))
    
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
        return str(json_response['room_id'])

            