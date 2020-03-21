from pydub import  AudioSegment

song = AudioSegment.from_file("Your name is like.m4a", "mp4")

song.export("Your name is like.m4a", "mp4")

