__Core P2P and Mp3 audio protocole (standard port 55227)__

*			if path=="/":
outputs the software name and version and an URL for code repository. 

*			if path=="/ping":

Replies "pong"
*			if path=="/listpeers":
Register the requesting machine's IPv6 in the inititial tracker peer table of this peer, then outputs all known peers, one per line

*			if path=="/id":
Outputs the station's human-readable title/id
*			if path=="/random-mp3":
Ouputs on the first line a randomly chosen .mp3 available on this peer, or "No .mp3 found, sorry" if there's no one. Then on the following lines the following metadata, or blank line if none found:

Artist

Album

Title

*			if path=='/mp3':
Parameter: an .mp3 filename

Binary reply. The full .mp3 file requested. Max size 30MiB

*			if path=="/mp3-catalog": 
All .mp3 files filenames served by this peer, one per line			

__Flac audio protocol (standard port 55228)__

*			if path=="/":
outputs the software name and version and an URL for code repository. 

*			if path=="/ping":
Replies "pong"

*			if path=='/flac':
Parameter: a .flac filename
.
Binary reply. The full .flac file requested. Max size 4GiB 				

*			if path=="/flac-size":
Returns the size in bytes of the total flac catalog for this peer			

*			if path=="/flac-catalog": 
All .flac files filenames served by this peer, one per line			





__Vidéo protocol (standard port 55229)__

*			if path=="/":
outputs the software name and version and an URL for code repository. 

*			if path=="/ping":
replies "pong"

*			if path=='/mp4':
Parameter: an .mp4 filename

Binary reply. The full .mp4 file requested. Max size 1.2GiB

*			if path=="/mp4-catalog":
All .mp4 files filenames served by this peer, one per line

*			if path=="/mp4-metadata":
Parameter : .mp4 filename fro which metadata will be outputed

Outputs the following medata, one per line, or a blank line for any metadata not found. 

Title 

Category (Any Artist set forces category to be "Music")

Artist

Description
	
*			if path=="/station-metadata":
first line, station title. Second line, station description
