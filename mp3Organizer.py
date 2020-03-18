import eyed3

def mp3Tagger(filepath, name, album):
 mp3 = eyed3.load(filepath)
 mp3.tag.artist = name
 mp3.tag.album = album
 mp3.tag.save()
 return

