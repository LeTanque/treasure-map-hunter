import json
import requests
import time
from queue import SimpleQueue as Q
import os


# sets variables for making post requests to the server
token = os.environ["SERVER_KEY"]
url = 'https://lambda-treasure-hunt.herokuapp.com/api/adv'
headers = {
    'Authorization': f'Token {token}', 
    'Content-Type': 'application/json'
}


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
    # Finds directions to room
    def run(self):
        path = self.find_room()
        directions = self.get_directions(path)
        if self.ve >= 1:
            print(f"Directions from {self.start} to {self.end}: \n {directions}")

        self.follow_path(directions)

    # gets the path and directions to follow that path
    def find_room(self):
        self.q.put([self.start])
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
    def follow_path(self, directions):
        current_room = self.start
        for dir in directions:
            next_room = str(self.map[current_room][dir])
            data = {'direction': f'{dir}', 'next_room_id': f'{next_room}'}
            resp = requests.post(url + '/move/',
                                data=json.dumps(data),
                                headers=headers
                                )
            temp_content = json.loads(resp.content)
            CD = temp_content['cooldown']
            current_room = str(temp_content['room_id'])
            items = temp_content['items']
            print(f'moved to {current_room}')
            print(f'items {items}')
            time.sleep(CD + .1)