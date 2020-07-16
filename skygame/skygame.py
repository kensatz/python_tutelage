# 
import requests
import sys
import time
from time import sleep
from threading import Thread

#---------------------------------------------------------------
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

#---------------------------------------------------------------
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

#---------------------------------------------------------------
class C4_game:
    def __init__(self, playerX, playerO):
        self.playerX, self.playerO = playerX, playerO
        self.board = [[' '] * 6 for _ in range(7)]
        self.ply = 0

    def get_checker(self, column, rank):
        return self.board[column][rank] if column in range(7) and rank in range(6) else None

    def make_move(self, column):
        assert column in range(7)
        assert ' ' in self.board[column]
        exes_turn = self.ply % 2 == 0
        checker = 'X' if exes_turn else 'O'
        rank = self.board[column].index(' ')
        self.board[column][rank] = checker
        self.ply += 1

    def update_game_state(self):
        exes_turn = self.ply % 2 == 0
        current_player = self.playerX if exes_turn else self.playerO
        if current_player.ilk == 'local':
            self.display_board()
        pass # TBD: post game state to clash 

    def winner(self):
        # possible return values are:
        #     'X'
        #     'O'
        #     '='  (tie game)
        #     None (game incomplete)
                
        # check for wins
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dc, dr in directions:
            for c0 in range(7):
                for r0 in range(6):
                    line = [self.get_checker(c0 + i*dc, r0 + i*dr) for i in range(4)]
                    for color in ('X', 'O'):
                        if all(checker == color for checker in line):
                            return color

        # check for tie
        if self.ply == 6*7:
            return '='  # tie game
        
        # otherwise, game is incomplete
        return None

    def display_board(self):
        print()
        print('    +---------------------+')
        for rank in range(5, -1, -1):
            print(f'    |', end = '')
            for column in range(7):
                print(f' {self.get_checker(column, rank)} ', end = '')
            print('|')
        print('    +---------------------+')
        print('      1  2  3  4  5  6  7 ')
        # repr = self.__repr__()
        # print(f'repr = {repr}')
        # parts = repr.split(':')
        # ply = eval(parts[0])
        # board = eval(parts[1])
        # print(f'ply = {ply}')
        # print(f'board = {board}')
        print()

    def __repr__(self):
        col_strs = []
        for column in self.board:
            col_strs.append(f"[{','.join(map(repr, column))}]")
        return f"{self.ply}:[{','.join(col_strs)}]"
        
    def __str__(self):
        pass

#---------------------------------------------------------------
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
            one_thru_seven = input(f'Drop your checker into which column, {self.name}? ')
            column = int(one_thru_seven) - 1
        return column

    def get_remote_move(self):
        # TBD: implement this
        # wait for change in game state, determine move, and return it
        return None
        
#---------------------------------------------------------------
def main():
    # clash = Clash("http://key-value-pairs.appspot.com")
    # lobby = ClashLobby(clash, "lobby")

    # my_name = input("What's your name? ")
    # lobby.exit(my_name)
    # print(f"Lobby contains: {lobby.lobbyists()}")

    # input("press Enter to enter the lobby ")
    # lobby.enter(my_name)
    # print("Your are now in the lobby")
    # print(f"Lobby contains: {lobby.lobbyists()}")

    my_name = input("What's your name? ")
    op_name = input("What is your opponent's name? ")
    op_ilk = input("What is your opponent's ilk (local or remote)? ")
    assert op_ilk in ('local', 'remote')

    if my_name == 'Ken':
        X = C4_player(my_name, 'X', 'local')
        O = C4_player(op_name, 'O', op_ilk)
    else:
        X = C4_player(op_name, 'X', op_ilk)
        O = C4_player(my_name, 'O', 'local')

    game = C4_game(X, O)

    game.display_board()
    winner = None
    while winner == None:
        exes_turn = game.ply % 2 == 0
        current_player = X if exes_turn else O
        move = current_player.get_move()
        game.make_move(move)
        game.update_game_state()
        winner = game.winner()

    winner = game.winner()
    if winner in {'X', 'O'}:
        print(f'{winner} wins the game.')
    elif winner == '!':
        print(f'Tie game!')
    else:
        print(f"something's wrong... game.winner() returned {winner}.")
    print()


#---------------------------------------------------------------
if __name__ == '__main__':
    main()
