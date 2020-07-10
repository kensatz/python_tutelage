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
            names = name_list.split(',') if name_list else []
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
            names = name_list.split(',') if name_list else []
            if name not in names:
                registered = False
            else:
                names.remove(name)
                name_list = ','.join(names)
                self.clash.put(self.lobby_key, name_list)
                sleep(0.5)

    def lobbyists(self):
        return self.clash.get(self.lobby_key).split(',')

class C4_game:
    def __init__(self, playerX, playerO):
        self.playerX, self.playerO = playerX, playerO
        self.ply = 0
        self.board = [[] for _ in range(7)]

    def make_move(self, column):
        assert column in range(7)
        assert len(self.board[column]) < 6
        turn = self.ply % 2
        checker = 'X' if turn == 0 else 'O'
        self.board[column].append(checker)
        self.ply += 1

    def winner(self):
        # possible return values are:
        #     'X'
        #     'O'
        #     '!'  (tie game)
        #     None (game incomplete)
        pass

    def update_game_state(self):
        turn = self.ply % 2
        current_player = self.playerX if turn == 0 else self.playerO
        if current_player.ilk == 'local':
            self.display_board()
        pass # TBD: post game state to clash 

    def display_board(self):
        pass

    def __str__(self):
        pass

class C4_player:
    def __init__(self, name, color, ilk):
        assert color in ('X', 'O')
        assert ilk in ('local', 'remote')
        self.name, self.color, self.ilk = name, color, ilk

    def get_move(self):
        return self.get_local_move() if self.ilk == 'local' else self.get_remote_move()

    def get_local_move(self):
        column = -1
        while column not in range(7):
            column = input('Place your checker in what column?')

    def get_remote_move(self):
        # wait for change in game state, determine move, and return it
        pass

        
def main():
    clash = Clash("http://key-value-pairs.appspot.com")
    lobby = ClashLobby(clash, "lobby")

    name = input("What's your name? ")
    lobby.exit(name)
    print(f"Lobby contains: {lobby.lobbyists()}")

    input("press Enter to enter the lobby ")
    lobby.enter(name)
    print("Your are now in the lobby")
    print(f"Lobby contains: {lobby.lobbyists()}")

    #play(name)
    #unregister(name)


if __name__ == '__main__':
    main()
