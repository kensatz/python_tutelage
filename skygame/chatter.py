# 
import requests
from pynput import keyboard
import sys
import msvcrt
import time

ESC = 27
def test():
    while True:
        if msvcrt.kbhit():
            c = msvcrt.getche()
            o = ord(c)
            if o == ord('\n') or o == ord('\r'):
                msvcrt.putch(b'\n')
            elif o == ESC:
                break
        time.sleep(0.1)

def main():
    test()
    
if __name__ == "__main__":
    main()


