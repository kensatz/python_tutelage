import sys, os
import string
from argparse import ArgumentParser

def main():

    printable_chars = string.ascii_letters + string.digits + string.punctuation
    def char_of(byte):
        s = chr(byte)
        if not s in printable_chars:
            s = '.'
        return s

    parser = ArgumentParser()
    parser.add_argument("-n", type=int, help="display n bytes")  # optional
    parser.add_argument("filename", help="file to dump")         # required

    args = parser.parse_args()
    filename = args.filename
    n = args.n or os.stat(filename).st_size

    address = 0
    with open(filename, 'rb') as infile:
        while True:
            byte_line = infile.read(min(n,16))
            n -= len(byte_line)

            if not byte_line:
                break

            address_hi = address // 0x10000
            address_lo = address % 0x10000

            print(f'{address_hi:04X}_{address_lo:04X}:  ', end = '')
            byte_quads = [byte_line[offset:offset+4] for offset in range(0, 16, 4)]
            for byte_quad in byte_quads:
                for byte in byte_quad:
                    print(f'{byte:02X} ', end = '')
                print(f'  ', end = '')
            print(f' ', end = '')

            byte_quads = [byte_line[offset:offset+4] for offset in range(0, 16, 4)]
            for byte_quad in byte_quads:
                for byte in byte_quad:
                    print(f'{char_of(byte):1s}', end = '')
                print(f' ', end = '')
            print(f'    ')

            address += 16
       
if __name__ == "__main__":
    main()

def read_byte_line(file, start_address):
    pass

    