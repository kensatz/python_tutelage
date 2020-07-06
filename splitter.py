import sys
import time


def main():
    def usage():
        nonlocal prog_name
        print()
        print(f'usage: {prog_name} <filename>.wav')
        print(f'Splits a multi-channel wave file into mono files.')
        sys.exit(-1)

    prog_name = sys.argv[0]
    args = sys.argv[1:]

    if len(args) != 1:
        usage()
    filename = args[0]
    extension = filename[-4:].lower()
    if extension != '.wav':
        usage()

    specs = {'filename':filename}
    print(f'opening {filename}')
    with open(filename, 'rb') as multifile:
        parse_file_header(multifile, specs)
        show_specs(specs)
        split(multifile, specs) 

def parse_file_header(multifile, specs):
    chunk_id = multifile.read(4)
    if chunk_id != b'RIFF':
        print(f"FATAL ERROR: Unknown chunk_id; expected b'RIFF'")
        sys.exit(-2)
    specs['chunk_id'] = chunk_id

    chunk_size = int.from_bytes(multifile.read(4), byteorder = 'little')
    specs['chunk_size'] = chunk_size

    format_id = multifile.read(4)
    if format_id != b'WAVE':
        print(f"FATAL ERROR: Unknown format_id; expected b'WAVE'")
        sys.exit(-3)
    specs['format_id'] = format_id

    fmt_subchunk_id = multifile.read(4)
    expected = b'fmt '
    if fmt_subchunk_id != expected:
        print(f"FATAL ERROR: Unknown fmt_subchunk_id; expected {expected}")
        sys.exit(-4)
    specs['fmt_subchunk_id'] = fmt_subchunk_id

    fmt_subchunk_size = int.from_bytes(multifile.read(4), byteorder = 'little')
    expected = 16
    if fmt_subchunk_size != expected:
        print(f"FATAL ERROR: Unknown fmt_subchunk_size; expected {expected}")
        sys.exit(-4)
    specs['fmt_subchunk_size'] = fmt_subchunk_size

    audio_format = int.from_bytes(multifile.read(2), byteorder = 'little')
    expected = 1  # 1 means data is PCM encoded
    if audio_format != expected:
        print(f"FATAL ERROR: Unknown audio_format; expected {expected}")
        sys.exit(-5)
    specs['audio_format'] = audio_format

    num_channels = int.from_bytes(multifile.read(2), byteorder = 'little')
    expected = 32
    if num_channels > expected:
        print(f"FATAL ERROR: number of channels exceeds {expected}")
        sys.exit(-6)
    if num_channels < 1:
        print(f"FATAL ERROR: less than one channel to process.")
        sys.exit(-7)
    specs['num_channels'] = num_channels
    
    sample_rate = int.from_bytes(multifile.read(4), byteorder = 'little')
    specs['sample_rate'] = sample_rate

    byte_rate = int.from_bytes(multifile.read(4), byteorder = 'little')
    specs['byte_rate'] = byte_rate

    block_align = int.from_bytes(multifile.read(2), byteorder = 'little')
    specs['block_align'] = block_align

    bits_per_sample = int.from_bytes(multifile.read(2), byteorder = 'little')
    specs['bits_per_sample'] = bits_per_sample

    # skip past any unused subchunks
    while True:
        subchunk_id = multifile.read(4)
        subchunk_size = int.from_bytes(multifile.read(4), byteorder = 'little')    
        if subchunk_id == b'data':
            break
        print(f"skipping past subchunk '{subchunk_id}' ({subchunk_size} bytes)")
        multifile.read(subchunk_size)

    data_subchunk_id = subchunk_id
    data_subchunk_size = subchunk_size
    
    specs['data_subchunk_id'] = data_subchunk_id
    specs['data_subchunk_size'] = data_subchunk_size

    num_frames = data_subchunk_size // block_align
    print(f'number of frames (calculated) = {num_frames:10,}')
    specs['num_frames'] = num_frames

    assert num_frames * block_align == data_subchunk_size
    
    dt = num_frames // specs['sample_rate']
    seconds = dt % 60
    dt //= 60
    minutes = dt % 60
    dt //= 60
    hours = dt
    duration = f'{hours:2d}:{minutes:02d}:{seconds:02d}'
    specs['duration'] = duration

def show_specs(specs):
    for k, v in specs.items():
        if isinstance(v, int):
            print(f'   {k:20} = {v:,}')
        else:
            print(f'   {k:20} = {v}')
    print()

def split(multifile, specs):
    filename = specs['filename']
    num_channels = specs['num_channels']
    outfiles = [None] * num_channels
    
    for i in range(num_channels):
        outfile_name = f'{filename[:-4]}_{i+1:02d}.wav'
        outfile = open(outfile_name, 'wb') 
        write_header(outfile, specs)
        outfiles[i] = outfile
    
    # hi_peaks = [0] * num_channels
    # lo_peaks = [0] * num_channels
    n_frames = 0
    bytes_per_sample =specs['bits_per_sample'] // 8
    while True:
        for i, outfile in enumerate(outfiles):
            sample = multifile.read(bytes_per_sample)
            if len(sample)!= bytes_per_sample:
                break
            x = int.from_bytes(sample, 'little', signed = True)
            # hi_peaks[i] = max(hi_peaks[i], x)
            # lo_peaks[i] = min(lo_peaks[i], x)
            outfile.write(sample)
        if len(sample) != bytes_per_sample:
            break
        if n_frames % 100000 == 0:
            print(f'n_frames = {n_frames:,}')
        n_frames += 1

    # print(f'{"channel":>16}{"hi peaks":>16}{"lo peaks":>16}')
    # for i in range(num_channels):
    #     print(f'{i+1:16}{hi_peaks[i]:16,}{lo_peaks[i]:16,}')
    # print()

    print(f"number of frames (expected)   = {specs['num_frames']:15,}")
    print(f"number of frames (counted)    = {n_frames:15,}") 

    for outfile in outfiles:
        outfile.close()

def write_header(outfile, specs):
    mono_byte_rate      = specs['byte_rate']//specs['num_channels']
    mono_block_align    = specs['block_align']//specs['num_channels']
    mono_data_size      = specs['num_frames'] * mono_block_align
    mono_chunk_size     = mono_data_size + 36

    chunk_id            = specs['chunk_id']                                 # b'RIFF'
    chunk_size          = mono_chunk_size.to_bytes(4, 'little')
    format_id           = specs['format_id']                                # b'WAVE'
    fmt_subchunk_id     = specs['fmt_subchunk_id']                          # b'fmt '
    fmt_subchunk_size   = specs['fmt_subchunk_size'].to_bytes(4, 'little')  # 16 (as 4 bytes)
    audio_format        = specs['audio_format'].to_bytes(2, 'little')       # 1 (as 2 bytes)
    num_channels        = (1).to_bytes(2, 'little')
    sample_rate         = specs['sample_rate'].to_bytes(4, 'little')        # typically 48,000 or 44,100
    byte_rate           = mono_byte_rate.to_bytes(4, 'little')
    block_align         = mono_block_align.to_bytes(2, 'little')
    bits_per_sample     = specs['bits_per_sample'].to_bytes(2, 'little')
    data_subchunk_id    = specs['data_subchunk_id']        # b'data'        # typically 16, 24, or 32
    data_subchunk_size  = mono_data_size.to_bytes(4, 'little')

    outfile.write(chunk_id)
    outfile.write(chunk_size)
    outfile.write(format_id)
    outfile.write(fmt_subchunk_id)
    outfile.write(fmt_subchunk_size)
    outfile.write(audio_format)
    outfile.write(num_channels)
    outfile.write(sample_rate)
    outfile.write(byte_rate)
    outfile.write(block_align)
    outfile.write(bits_per_sample)
    outfile.write(data_subchunk_id)
    outfile.write(data_subchunk_size)

if __name__ == "__main__":
    main()
