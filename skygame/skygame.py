# 
import requests
import sys
import msvcrt
import time

def process_local():
    return False

def process_remote():
    return False

def get_game_state():
    game_state = requests.get("http://key-value-pairs.appspot.com/?game_state")
    assert game_state.status_code == 200
    return game_state.text

def put_game_state(state):
    game_state = requests.get(f"http://key-value-pairs.appspot.com/?game_state={state}")
    assert game_state.status_code == 200

def main():
    state = get_game_state()
    if state == '':
        greeting = input('Enter a greeting to host a game, or press enter to wait for a game to start.')
        if greeting:
            put_game_state(greeting)

    while True:
        if msvcrt.kbhit():
            done = process_local()
            if done:
                break
        state = get_game_state()
        if state == '':
            break

main()
