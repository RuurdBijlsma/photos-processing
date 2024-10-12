import mmap


# Get byte slices from exiftool
# Use this file to extract thumbnail image, hdr gain map, and motion picture mp4 from a pixel photo
def extract_slice(input_file, output_file, offset, length):
    with open(input_file, "rb") as f:
        # Memory-map the file, size 0 means whole file
        mmapped_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

        # Extract the slice
        data_slice = mmapped_file[offset : offset + length]

        # Write the slice to the output file
        with open(output_file, "wb") as out_f:
            out_f.write(data_slice)

        # Close the memory-mapped file
        mmapped_file.close()


# Example usage
input_file = "img.jpg"
output_file = "mmap-out.mp4"
# HDR gain map:
# offset = 3809938
# length = 106210
# Motion photo:
offset = 3809938 + 106210
length = 2571996

extract_slice(input_file, output_file, offset, length)
