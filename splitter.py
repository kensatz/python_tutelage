import sys

def main():
    def usage(prog_name):
        print()
        print(f'usage: {prog_name} <multi-channel wave file name>')
        print(f'Splits a multi-channel wave file into mono files.')
        sys.exit(-1)

    prog_name = sys.argv[0]
    args = sys.argv[1:]

    if len(args) != 1:
        usage(prog_name)
    filename = args[0]
    assert '.wav' in filename

    print(f'opening {filename}')
    with open(filename, 'rb') as multifile:
        w = 18 # field width

        chunk_id = multifile.read(4)
        print(f'   {"chunk_id":{w}s} = {chunk_id}')
        if chunk_id != b'RIFF':
            print(f"FATAL ERROR: Unknown chunk_id; expected b'RIFF'")
            sys.exit(-2)

        chunk_size = int.from_bytes(multifile.read(4), byteorder = 'little')
        print(f'   {"chunk_size":{w}s} = {chunk_size:,}')

        format_id = multifile.read(4)
        print(f'   {"format_id":{w}s} = {format_id}')
        if format_id != b'WAVE':
            print(f"FATAL ERROR: Unknown format_id; expected b'WAVE'")
            sys.exit(-3)

        subchunk_1_id = multifile.read(4)
        print(f'   {"subchunk_1_id":{w}s} = {subchunk_1_id}')
        expected = b'fmt '
        if subchunk_1_id != expected:
            print(f"FATAL ERROR: Unknown subchunk_1_id; expected {expected}")
            sys.exit(-4)

        subchunk_1_size = int.from_bytes(multifile.read(4), byteorder = 'little')
        print(f'   {"subchunk_1_size":{w}s} = {subchunk_1_size:,}')
        expected = 16
        if subchunk_1_size != expected:
            print(f"FATAL ERROR: Unknown subchunk_1_size; expected {expected}")
            sys.exit(-4)

        audio_format = int.from_bytes(multifile.read(2), byteorder = 'little')
        print(f'   {"audio_format":{w}s} = {audio_format:,}')
        expected = 1
        if audio_format != expected:
            print(f"FATAL ERROR: Unknown audio_format; expected {expected}")
            sys.exit(-5)

        num_channels = int.from_bytes(multifile.read(2), byteorder = 'little')
        print(f'   {"num_channels":{w}s} = {num_channels:,}')
        
        expected = 32
        if num_channels > expected:
            print(f"FATAL ERROR: number of channels exceeds {expected}")
            sys.exit(-6)

        if num_channels < 1:
            print(f"FATAL ERROR: less than one channel to process.")
            sys.exit(-7)

        sample_rate = int.from_bytes(multifile.read(4), byteorder = 'little')
        print(f'   {"sample rate":{w}s} = {sample_rate:,} samples per second')

        byte_rate = int.from_bytes(multifile.read(4), byteorder = 'little')
        print(f'   {"byte rate":{w}s} = {byte_rate:,} bytes per second')

        block_align = int.from_bytes(multifile.read(2), byteorder = 'little')
        print(f'   {"block align":{w}s} = {block_align:,} bytes')

        bits_per_sample = int.from_bytes(multifile.read(2), byteorder = 'little')
        print(f'   {"bits_per_sample":{w}s} = {bits_per_sample:,}')

        while True:
            subchunk_2_id = multifile.read(4)
            if subchunk_2_id == b'data':
                break
        print(f'   {"subchunk_2_id":{w}s} = {subchunk_2_id}')

        subchunk_2_size = int.from_bytes(multifile.read(4), byteorder = 'little')
        print(f'   {"subchunk_2_size":{w}s} = {subchunk_2_size:,}')


        

        

        



        

        

        
        




        sys.exit(0)

      
if __name__ == "__main__":
    main()
