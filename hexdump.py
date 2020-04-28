import sys
import string

def main():
    def usage(prog_name):
        print(f'usage: {prog_name} <file_name>')
        sys.exit(-1)

    printable_chars = string.ascii_letters + string.digits + string.punctuation
    def char_of(byte):
        s = chr(byte)
        if not s in printable_chars:
            s = '.'
        return s

    prog_name = sys.argv[0]
    args = sys.argv[1:]

    if len(args) != 1:
        usage(prog_name)
    filename = args[0]
    print(f'opening {filename}')

    address = 0
    with open(filename, 'rb') as infile:
        while True:
            byte_line = infile.read(16)
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
