# looping-video-finder
Searches given video file(s) for a looping section (that is, where the start and end frame are same or similar enough) of a given length.

It is intended for automatically scanning a video file in order to find and extract all looping sections, so that they could be, if they are actually interesting enough, converted (via third party tools not part of this repo) to GIFs to be used in chat and social media apps (Telegram, Discord etc.).

Works in three phases:
1. Opens the file, reads each frame, and calculates a hash for them.
2. Compares the calculated hashes in order to find similar frames
3. Extracts a small clip from the video file based on the found matching hashes of the frames.
  
What the script will find, most of the time, is simply dialogue scenes, where the camera cuts from one face to another. This does, technically, count as a looping seqment, but isn't what I was originally after when writing the code. It can and will still occasionally find something good, just keep in mind that most of what it finds is not, and manual output vetting is needed.
