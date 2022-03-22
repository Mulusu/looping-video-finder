# Search parameters ( Change as needed )
save_folder = "loops/"
min_length = 1          # Min length of clip, in seconds
max_length = 20         # Max length of clip, in seconds
threshold = 0           # The max allowed differense in hashes (default : 0)
mid_threshold = 40      # Threshold of difference required in the middle of the clip. Used to filter out still images
hash_size = 32          # results in hash_size^2 * 2 bit hash (that is, hash_size = 8 --> 128-bit hash)
prefer_long = 1         # Set to one to prefer longer loops over shorter ones
output_width = 0        # Width of the output file. Zero or negative for auto
output_height = 360     # Height of the output file. Zero or negative for auto