# 
import requests
import sys
import time
from time import sleep
from threading import Thread

class Clash:
    def __init__(self, url):
        self.url = url

    def get(self, key):
        response = requests.get(f'{self.url}/?{key}')
        assert response.status_code == 200
        return response.text

    def put(self, key, val):
        response = requests.get(f'{self.url}/?{key}={val}')
        assert response.status_code == 200

class ClashLobby:
    def __init__(self, clash, lobby_key):
        self.clash = clash
        self.lobby_key = lobby_key

    def enter(self, name):
        registered = False
        while not registered:
            print('+')
            name_list = self.clash.get(self.lobby_key)
            names = name_list.split(',')
            if name in names:
                registered = True
            else:
                names.append(name)
                name_list = ','.join(names)
                self.clash.put(self.lobby_key, name_list)
                sleep(0.5)

    def exit(self, name):
        registered = True
        while registered:
            print('-')
            name_list = self.clash.get(self.lobby_key)
            names = name_list.split(',')
            if name not in names:
                registered = False
            else:
                names.remove(name)
                name_list = ','.join(names)
                self.clash.put(self.lobby_key, name_list)
                sleep(0.5)

    def lobbyists(self):
        return self.clash.get(self.lobby_key).split(',')
        
def main():
    clash = Clash("http://key-value-pairs.appspot.com")
    lobby = ClashLobby(clash, "lobby")

    name = input("What's your name? ")
    lobby.exit(name)
    print(f"Lobby contains: {lobby.lobbyists()}")

    input("press Enter to enter the lobby")
    lobby.enter(name)
    print("Your are now in the lobby")
    print(f"Lobby contains: {lobby.lobbyists()}")

    #play(name)
    #unregister(name)


if __name__ == '__main__':
    main()
