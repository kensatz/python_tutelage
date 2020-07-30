# 
import requests
import sys
import time
from time import sleep
from threading import Thread

#---------------------------------------------------------------
class FunctionThread(Thread):
    def __init__(self, *args, **kwargs):
        self.saved_target = kwargs.get('target')
        self.saved_args = kwargs.get('args')
        self.saved_kwargs = kwargs.get('kwargs')

        super().__init__(*args, **kwargs)
        self._return = None

    def run(self):
        args = self.saved_args or []
        kwargs = self.saved_kwargs or {}
        if self.saved_target:
            self._return = self.saved_target(*args, **kwargs)
    
    def join(self, *args, **kwargs):
        super().join(*args, **kwargs)
        return self._return

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

    def wait_for_change(self, key, old_value=None):
        def waiter():
            while True:
                current_value = self.get(key)
                if current_value != old_value:
                    break
                sleep(0.5)
            return current_value

        if old_value is None:
            old_value = self.get(key)

        wait_thread = FunctionThread(target=waiter)
        wait_thread.start()
        return wait_thread

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
    def __init__(self, clash, my_name, op_name, i_start):
        self.clash, self.my_name, self.op_name = clash, my_name, op_name 

        self.my_phase = 0 if i_start else 1
        self.X_name = my_name if i_start else op_name
        self.O_name = op_name if i_start else my_name
        self.game_name = f'C4_{self.X_name}_{self.O_name}'
        self.board = [[' '] * 6 for _ in range(7)]
        self.ply = 0
        self.highlights = []
        if self.my_turn():
            self.update_game_state()

    def __str__(self):
        return 'TBD'

    def __repr__(self):
        col_strs = [f"[{','.join(map(repr, column))}]" for column in self.board]
        return f"({self.ply},[{','.join(col_strs)}])"

    def my_turn(self):
        return self.ply % 2 == self.my_phase

    def display_board(self):
        indent = ' ' * (4 if self.my_turn() else 34)
        heading = f'{self.X_name} (X) vs {self.O_name} (O)'
        vertical, horizontal, corner = '|', '---', '+'
        print()
        print(indent + f'{heading:^23}')
        print(indent + corner + horizontal * 7 + corner)
        for r in range(6):
            rank = 5 - r
            print(indent + vertical, end = '')
            for column in range(7):
                checker = self.get_checker(column, rank)
                if (column, rank) in self.highlights:
                    print(f'({checker})', end = '')
                else:
                    print(f' {checker} ', end = '')
            print(vertical)
        print(indent + corner + horizontal * 7 + corner)
        print(indent + '  1  2  3  4  5  6  7 ')

    def get_checker(self, column, rank):
        return self.board[column][rank] if column in range(7) and rank in range(6) else None

    def get_local_move(self):
        column = -1
        while column not in range(7):
            one_thru_seven = input(f'Drop your checker into which column, {self.my_name}? ')
            column = int(one_thru_seven) - 1
        return column

    def get_remote_move(self):
        # wait my turn
        while True:
            # wait for a change in the game state
            state = self.clash.wait_for_change(self.game_name).join()
            # make sure its our turn
            new_ply, new_board = eval(state)
            if new_ply % 2 == self.my_phase:
                break

        # see which column changed and return its index
        changed_column_mask = [new_board[col] != self.board[col] for col in range(7)]
        assert sum(changed_column_mask) == 1
        column = changed_column_mask.index(True) 
        return column

    def make_move(self, column):
        assert column in range(7)
        assert ' ' in self.board[column]
        rank = self.board[column].index(' ')
        self.highlights = [(column, rank)]

        exes_turn = self.ply % 2 == 0
        checker = 'X' if exes_turn else 'O'
        was_my_turn = self.my_turn()
        self.board[column][rank] = checker
        self.ply += 1   # changes turn
        if was_my_turn:
            self.update_game_state()

    def update_game_state(self):
        self.clash.put(self.game_name, self.__repr__())

    def winner(self):
        # check for wins
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dc, dr in directions:
            for c0 in range(7):
                for r0 in range(6):
                    places = [(c0 + i*dc, r0 + i*dr) for i in range(4)]
                    quad = [self.get_checker(*place) for place in places]
                    for color in ('X', 'O'):
                        if all(checker == color for checker in quad):
                            self.highlights = places
                            return color 
        # check for tie
        if self.ply == 6*7:
            self.highlights = []
            return '='  # tie game

        # otherwise, game is incomplete
        return None

def main():
    clash = Clash("http://key-value-pairs.appspot.com")\
    
    # w = clash.wait_for_change('some_key').join()
    # print("waiting for a change...")
    # result = w.join()
    # print("done waiting")
    # print(f'result is {repr(result)}')
    # import sys
    # sys.exit()

    my_name = input("What's your name? ")
    op_name = input("What's your opponent's name? ")
    reply = input("Are you the starting player? ")
    i_start = reply[0].lower() == 'y'
    
    game = C4_game(clash, my_name, op_name, i_start)
    
    winner = None
    while winner is None:
        game.display_board()
        if game.my_turn():
            move = game.get_local_move() 
        else:
            move = game.get_remote_move()
        game.make_move(move)
        winner = game.winner()

    game.display_board()
    names = {'X':game.X_name, 'O':game.O_name, '=':'The cat'}
    print(f"{names[winner]} wins!")

    if game.my_turn():
        clash.put(game.game_name, '') # cleanup

#---------------------------------------------------------------
if __name__ == '__main__':
    main()
