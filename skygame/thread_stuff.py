# 
import requests
import sys
import msvcrt
import time
from time import sleep
from threading import Thread

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

def worker(x):
    print(f"I'm working on {x}")
    sleep(3)
    return x+5

t = FunctionThread(target=worker, args=[7])
t.start()

print("do other stuff in main thread")

ret = t.join()
print(f"done: {ret}")
sys.exit()

def process_local():
    return False

def process_remote():
    return False

def get_game():
    game_state = requests.get("http://key-value-pairs.appspot.com/?game_state")
    assert game_state.status_code == 200
    return game_state.text

def put_game(state):
    game_state = requests.get(f"http://key-value-pairs.appspot.com/?game_state={state}")
    assert game_state.status_code == 200

def main():
    state = get_game()
    if state == '':
        greeting = input('Enter a greeting to host a game, or press enter to wait for a game to start.')
        if greeting:
            put_game(greeting)

    while True:
        if msvcrt.kbhit():
            done = process_local()
            if done:
                break
        state = get_game()
        if state == '':
            break

if __name__ == '__main__':
    main()
