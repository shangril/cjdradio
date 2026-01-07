#!/usr/bin/env python3

from time import sleep 
from datetime import datetime
import random
import sys
import os
from os.path import expanduser
from threading import Thread
import urllib.request
import requests
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import socket
from email.utils import formatdate
import html
import base64
hasmutagen = False
try: 
	from mutagen.id3 import ID3
	hasmutagen = True
except:
	print ("""Mutagen not found (try "pip install mutagen"). Podcast won't be able to expode covers images available in MP3 files ID3 tags.""")

try:
	from tinytag import TinyTag
except:
	print("""Error importing TinyTag ! Try "pip install tinytag" """)
	sys.exit(0)
try:
	if len(sys.argv)==1 or len(sys.argv)==3: 
		import vlc
except:
	print("""Error importing python-vlc ! Try "pip install python-vlc" """)

if len(sys.argv)==1: 
	import gi
	gi.require_version('Gtk', '3.0')
	from gi.repository import Gtk	


def touch(fname, times=None):
	try: 
		with open(fname, 'a'):
			os.utime(fname, times)
	except: 
		print("unable to touch "+fname)

def crawler_daemon(g): 
	while True: 
		sleep(45)
		print ("crawler: crawl started")
		for aPeer in g.peers: 
			try: 		
				crawledPeers = OcsadURLRetriever.retrieveURL(f"http://[{aPeer}]:55227/listpeers", reqtimeout = 55).split("\n")
				newnewpeers = []
				for p in crawledPeers:
					if not p in g.peers: 
						newnewpeers.append(p)
				print (f"crawler: {len(newnewpeers)} newcomers peers discovered with {aPeer}")		
				g.set_peers(g.peers+newnewpeers)
			except: 
				print(f"crawler: {aPeer} didn't reply upon network crawl")
		print(f"crawler: crawl finished. {str(len(g.peers))} peers currently known")
		home = expanduser("~")
		basedir=os.path.join(home, ".cjdradio")
		if os.path.exists(os.path.join(basedir, "settings_crawledpeersList.txt")): 
			with open(os.path.join(basedir,'settings_crawledpeersList.txt'), 'w') as myfile:
				peerFile="\n".join(g.peers)
				myfile.write(f"{peerFile}")
		sleep(300)
def tracker_update_daemon(g): 
	while True: 
		sleep(400)
		g.registered = True
		g.set_processedPeers([])
		bkp = g.get_peers
		g.set_peers([])

		newpeers = []

		g.peers.append(g.get_settings_ip6addr())

		try: 
			newpeers = OcsadURLRetriever.retrieveURL(f"http://[{g.get_Builder().get_object("cb_initial_peers").get_active_text()}]:55227/listpeers").split("\n")
		except: 
			if len(sys.argv)==3: 
				MyPeerList=[]	
			
				home = expanduser("~")
				basedir=os.path.join(home, ".cjdradio")
				if os.path.exists(os.path.join(basedir, "settings_peersList.txt")): 
					with open(os.path.join(basedir,'settings_peersList.txt'), 'r') as myfile:
						MyPeerList=myfile.read().split("\n")
						myfile.close()
				
				dex=0;
				MyPeerList.append("200:abce:8706:ea81:94:fcf4:e379:b988")
				MyPeerList.append("fc71:fa3a:414d:fe82:f465:369b:141a:f8c")
				
				
				if os.path.exists(os.path.join(basedir, "settings_crawledpeersList.txt")): 
					with open(os.path.join(basedir,'settings_crawledpeersList.txt'), 'r') as myfile:
						MyPeerList=MyPeerList+myfile.read().split("\n")
						myfile.close()
				
				
				while dex < len(MyPeerList):
					initialPeer = MyPeerList[dex]
					try: 
						print("trying to reach initial peer "+initialPeer)
						newpeers = OcsadURLRetriever.retrieveURL(f"http://[{initialPeer}]:55227/listpeers", reqtimeout = 30).split("\n")
						dex=len(MyPeerList)
					except: 
						print("This initial peer is currently offline")
						dex=dex+1
				#except: 
				#		print("Unable to reach initial peer")
			else: 
				try: 
					newpeers = OcsadURLRetriever.retrieveURL(f"http://[{sys.argv[2]}]:55227/listpeers").split("\n")
				except: 
					print("Unable to reach initial peer")
					g.set_peers(bkp)
		newnewpeers = []
		for p in newpeers:
			if not p in g.peers: 
				newnewpeers.append(p)

		g.set_peers(g.peers+newnewpeers)


def indexing_daemon(g): 
	while True: 

		basedir=os.path.join(home, ".cjdradio")


		if os.path.isdir(basedir):
			#import threading
			#lock = threading.Lock()
			#lock.acquire()
			#try: 
			shareddir = g.shared_dir
			#finally:
			#	lock.release()
			if os.path.isdir(shareddir):
				datadir = os.path.join(basedir, "MetadataShares")
				if not os.path.isdir(datadir):
					os.makedirs(datadir)
				files = os.scandir(shareddir)
				for mp3 in files: 
					if mp3.name.endswith(".mp3"):
						if not os.path.exists(os.path.join(datadir, mp3.name+".artist.txt")):
							tags = TinyTag.get(os.path.join(shareddir, mp3.name))
						
							with open(os.path.join(datadir,mp3.name+'.artist.txt'), 'w') as myfile:
								myfile.write(f"{tags.artist}")
								
						if not os.path.exists(os.path.join(datadir, mp3.name+".album.txt")):
							tags = TinyTag.get(os.path.join(shareddir, mp3.name))
						
							with open(os.path.join(datadir,mp3.name+'.album.txt'), 'w') as myfile:
								myfile.write(f"{tags.album}")
								
						if not os.path.exists(os.path.join(datadir, mp3.name+".title.txt")):
							tags = TinyTag.get(os.path.join(shareddir, mp3.name))
						
							with open(os.path.join(datadir,mp3.name+'.title.txt'), 'w') as myfile:
								myfile.write(f"{tags.title}")

						if not os.path.exists(os.path.join(datadir, mp3.name+".duration.txt")):
							tags = TinyTag.get(os.path.join(shareddir, mp3.name))
#							print (str(tags.duration))
							with open(os.path.join(datadir,mp3.name+'.duration.txt'), 'w') as myfile:
								myfile.write(f"{str(tags.duration)}")

								
				unshareddir=os.path.join(basedir, "Unshared")
				if not os.path.exists(unshareddir):
					os.makedirs(unshareddir)
				files = os.scandir(unshareddir)
				for mp3 in files: 
					if mp3.name.endswith(".mp3"):
						if not os.path.exists(os.path.join(datadir, mp3.name+".artist.txt")):
							tags = TinyTag.get(os.path.join(unshareddir, mp3.name))
						
							with open(os.path.join(datadir,mp3.name+'.artist.txt'), 'w') as myfile:
								myfile.write(f"{tags.artist}")
								
						if not os.path.exists(os.path.join(datadir, mp3.name+".album.txt")):
							tags = TinyTag.get(os.path.join(unshareddir, mp3.name))
						
							with open(os.path.join(datadir,mp3.name+'.album.txt'), 'w') as myfile:
								myfile.write(f"{tags.album}")
								
						if not os.path.exists(os.path.join(datadir, mp3.name+".title.txt")):
							tags = TinyTag.get(os.path.join(unshareddir, mp3.name))
						
							with open(os.path.join(datadir,mp3.name+'.title.txt'), 'w') as myfile:
								myfile.write(f"{tags.title}")
						if not os.path.exists(os.path.join(datadir, mp3.name+".duration.txt")):
							tags = TinyTag.get(os.path.join(unshareddir, mp3.name))
#							print (str(tags.duration))
							with open(os.path.join(datadir,mp3.name+'.duration.txt'), 'w') as myfile:
								myfile.write(f"{str(tags.duration)}")
								


				dldir = os.path.join(basedir, "Downloads")
				if os.path.isdir(dldir):
					datadir = os.path.join(basedir, "MetadataDownloads")
					if not os.path.isdir(datadir):
						os.makedirs(datadir)
					files = os.scandir(dldir)
					for mp3 in files: 
						if mp3.name.endswith(".mp3"):
							if not os.path.exists(os.path.join(datadir, mp3.name+".artist.txt")):
								tags = TinyTag.get(os.path.join(shareddir, mp3.name))
						
								with open(os.path.join(datadir,mp3.name+'.artist.txt'), 'w') as myfile:
									myfile.write(f"{tags.artist}")
									
							if not os.path.exists(os.path.join(datadir, mp3.name+".album.txt")):
								tags = TinyTag.get(os.path.join(shareddir, mp3.name))
						
								with open(os.path.join(datadir,mp3.name+'.album.txt'), 'w') as myfile:
									myfile.write(f"{tags.album}")
									
							if not os.path.exists(os.path.join(datadir, mp3.name+".title.txt")):
								tags = TinyTag.get(os.path.join(shareddir, mp3.name))
						
								with open(os.path.join(datadir,mp3.name+'.title.txt'), 'w') as myfile:
									myfile.write(f"{tags.title}")
							
						
									
			else:
				print("No <$HOME>/.cjdradio/Shares directory found. Aborting mp3 scanning")
				os.makedirs(shareddir)

		else:
			print("No <$HOME>/.cjdradio directory found. Aborting mp3 scanning")
			os.makedirs(basedir)



		print ("Mp3 scanning finished")



		sleep(300)
def banner_daemon(g): 
	import threading
	while True:
		sleep(150)

		#first off we re-register to the tracker in case it rebooted and forgot us in the meanwhile
		if g.registered: #but only if we registered previously, because we are not traitorware and won't joint the network without prior consent

			#lock = threading.Lock()
			#lock.acquire();
			#try:
			bkp = g.get_peers()
			g.set_peers([])
			#finally: 
			#	lock.release()
			newpeers = []
			
			MyPeerList=[]
			
			#g.peers.append(g.get_settings_ip6addr())
			
			try: 
				if len(sys.argv)==1: 
					newpeers = OcsadURLRetriever.retrieveURL(f"http://[{b.get_object('cb_initial_peers').get_active_text()}]:55227/listpeers", reqtimeout = 30).split("\n")
				elif len(sys.argv)==3:
					
					home = expanduser("~")
					basedir=os.path.join(home, ".cjdradio")
					if os.path.exists(os.path.join(basedir, "settings_peersList.txt")): 
						with open(os.path.join(basedir,'settings_peersList.txt'), 'r') as myfile:
							MyPeerList=myfile.read().split("\n")
							myfile.close()
					
					dex=0;
					MyPeerList.append("200:abce:8706:ea81:94:fcf4:e379:b988")
					MyPeerList.append("fc71:fa3a:414d:fe82:f465:369b:141a:f8c")
					
								
					if os.path.exists(os.path.join(basedir, "settings_crawledpeersList.txt")): 
						with open(os.path.join(basedir,'settings_crawledpeersList.txt'), 'r') as myfile:
							MyPeerList=MyPeerList+myfile.read().split("\n")
							myfile.close()
					
					while dex < len(MyPeerList):
						initialPeer = MyPeerList[dex]
					
						try: 
							print("trying to reach initial peer ", initialPeer)
							newpeers = OcsadURLRetriever.retrieveURL(f"http://[{initialPeer}]:55227/listpeers", reqtimeout = 30).split("\n")
							dex=len(MyPeerList)
						except: 
							print("This initial peer is currently offline")
							dex=dex+1
				newnewpeers = []
				for p in newpeers:
					if not p in g.peers: 
						newnewpeers.append(p)
				#lock = threading.Lock()
				#lock.acquire();
				#try:
				g.set_peers(g.peers+newnewpeers)
				#finally: 
				#	lock.release()
				if len(sys.argv) == 1:
					#GUI mode, update gui
					while g.cbsinglestationlock:
						sleep(0.5)
					g.cbsinglestationlock = True
					try: 
						#lock = threading.Lock()
						#lock.acquire();
						try: 
							
							b.get_object("cbsinglestation").remove_all()
							for i in g.peers: 
								if not i in g.bannedStations:
									b.get_object("cbsinglestation").append_text(i)
							
						finally:
							print("Banner daemon processed") 
							#lock.release()
						#lock = threading.Lock()
						#lock.acquire();
						try: 
							b.get_object("cbsinglestation").set_active(0)
							b.get_object("discover_button").set_label(f"Discover new stations peers ({len(g.peers)})")
						finally: 
							#lock.release()
							print("Banner daemon updated Discover New Station Peers")
					finally: 
						g.cbsinglestationlock = False
			except: 
				print ("Initial peer not responding")
				g.set_peers(bkp)
				raise
				
		#then we can retest each banned peer to see if it pong and if so remove it from banned
		newBanned = []
		for p in g.bannedStations:
			if p!='':
				try: 
					pong = ''
					pong = OcsadURLRetriever.retrieveURL(f"http://[{p}]:55227/ping",  max_length = 120000, reqtimeout = 8)
					if pong!='pong':
						raise ValueError(f"no replying peer {p} on ping request")
				except: 
					newBanned.append(p)
		#lock = threading.Lock()		
		#lock.acquire()
		#try:
		g.bannedStations = newBanned
		#finally: 
		#	lock.release()
		
class Podcaster:
	g = None
	
	description = ""
	
	logo = ""
	coversfile = ""
	coversdir = ""
	
	donation_name = ""
	donation_url = ""
	donation_addy = ""
	
	proxy_url = None
	
	def __init__(self, gateway, description, logo, coversfile, coversdir, donation_name, donation_url, donation_addy, proxy_url=None):
		self.g=gateway
		self.description = description
		self.logo = logo
		self.coversfile = coversfile
		self.coversdir =  coversdir
		self.donation_name = donation_name
		self.donation_url = donation_url
		self.donation_addy = donation_addy
		self.proxy_url = proxy_url
		
		
class Cjdradio:
	g = None;
	h = None;
	def __init__(self):
		builder = None

		
		self.gladefile = "cjdradio.glade"
		
		builder = None
		if len(sys.argv)==1:
			builder = Gtk.Builder()
			builder.add_from_file("cjdradio.glade")
			builder.get_object("cjdradio_main_window").show_all()
		
		global g
		
		g = Gateway();
		g.set_builder(builder);
		g.load_settings_from_disk();

		h = Handler(builder, g)
		
		if len(sys.argv)==1:

			builder.connect_signals(h)
		
		
			builder.get_object("cjdradio_main_window").connect("destroy", Gtk.main_quit)
		
	def getGateway(self):
		return g


class Gateway:
	
	tmplock = '';
	
	httpLock = 0
	
	registered = False
	bannedArtists=[]
	blacklist = []

	podcast = False
	podcaster = None
	
	accessList = []

	dling = False;

	radio = None

	shared_dir = ''

	scan = None
	
	scanThread = None
	
	pingthread = None
	
	ID = 'Another random'
	
	webserver_thread = None
	
	crawler_thread = None
	
	bannerdaemon_thread = None
	bannedStations = []
	settings_ip6addr = "::"
	webserver = None
	
	plussed = {}
	
	processedPeers=[]
	peers = []
	
	h = None
	
	cbsinglestationlock=False;


	def plus(self, ip):
		if not ip in self.plussed:
			self.plussed[ip]=0
		self.plussed[ip]=self.plussed[ip]+1
	def resetplus(self):
		self.plussed = {}
	def set_processedPeers(self, peerList):
		self.processedPeers=peerList
	def get_processedPeers(self):
		return self.processedPeers
	def set_peers(self, peerList):
		self.peers=peerList
	def get_peers(self):
		return self.peers



	def set_webserverThread(self, thread):
		self.webserver_thread=thread
	def get_webserverThread(self):
		return self.webserver_thread

	def set_webserver(self, serv):
		self.webserver=serv
	def get_webserver(self):
		return self.webserver

	
	def get_builder(self):
		return self.builder	
	def set_builder(self, gtkbuilder):
		self.builder = gtkbuilder
	
	def get_settings_ip6addr(self): 
		return self.settings_ip6addr
	def load_settings_from_disk(self):
		home = expanduser("~")
		basedir=os.path.join(home, ".cjdradio")
		
		if not os.path.isdir(basedir):
			os.makedirs(basedir)

		if os.path.exists(os.path.join(basedir, "settings_ip6addr.txt")): 
			#settings_ip6addr	
			with open(os.path.join(basedir,'settings_ip6addr.txt'), 'r') as myfile:
				self.settings_ip6addr=myfile.read().strip("\n\r")
				myfile.close()
				if len(sys.argv)==1:
					self.builder.get_object("settings_ip6addr").set_text(self.settings_ip6addr)
		if os.path.exists(os.path.join(basedir, "settings_blacklist.txt")): 
			#settings_blacklist	
			with open(os.path.join(basedir,'settings_blacklist.txt'), 'r') as myfile:
				self.blacklist=myfile.read().split("\n")
				myfile.close()
				if len(sys.argv)==1:
					self.builder.get_object("clearBlacklist").set_label("Clear blacklist ("+str(len(self.blacklist))+")")
		if os.path.exists(os.path.join(basedir, "settings_access_list.txt")): 
			#settings_access_list	
			with open(os.path.join(basedir,'settings_access_list.txt'), 'r') as myfile:
				self.accessList=myfile.read().split("\n")
				myfile.close()
				if len(sys.argv)==1:
					list_ips = self.accessList
					
					self.builder.get_object("cb_access_list").remove_all()
					
					for ip in list_ips:
						if ip!='':
							self.builder.get_object("cb_access_list").append_text(ip)
							self.builder.get_object("cb_access_list").set_active(0)
		peerList = []
		
		if os.path.exists(os.path.join(basedir, "settings_peersList.txt")): 
			#settings_ip6addr	
			with open(os.path.join(basedir,'settings_peersList.txt'), 'r') as myfile:
				peerList=myfile.read().split("\n")
				myfile.close()

		if len(sys.argv)==1:
			
			home = expanduser("~")
			basedir=os.path.join(home, ".cjdradio")
			
			if not os.path.isdir(basedir):
				os.makedirs(basedir)

			if os.path.exists(os.path.join(basedir, "settings_id.txt")): 
				with open(os.path.join(basedir,'settings_id.txt'), 'r') as myfile:
					self.ID=myfile.read()
					myfile.close()
				self.builder.get_object("station_id").set_text(self.ID)

			
			
			
			
			self.builder.get_object("cb_initial_peers").remove_all()
			for peer in peerList:
				if peer!='': 
					self.builder.get_object("cb_initial_peers").append_text(peer)

			secondPeerList=[]
			
			if os.path.exists(os.path.join(basedir, "settings_crawledpeersList.txt")): 
				with open(os.path.join(basedir,'settings_crawledpeersList.txt'), 'r') as myfile:
					secondPeerList=myfile.read().split("\n")
					myfile.close()
				
			self.builder.get_object("cb_initial_peers").append_text("200:abce:8706:ea81:94:fcf4:e379:b988")
			self.builder.get_object("cb_initial_peers").append_text("fc71:fa3a:414d:fe82:f465:369b:141a:f8c")

			for peer in secondPeerList:
				if peer!='': 
					self.builder.get_object("cb_initial_peers").append_text(peer)



			self.builder.get_object("cb_initial_peers").set_active(0)
			
			
	def shared_dir_scan(self):
		if self.scan == None:
			self.scan = os.scandir (self.shared_dir)
		return self.scan
	def findAFile (self, art, alb, directory):
		
		basedir=os.path.join(home, ".cjdradio")
		
		if not os.path.isdir(basedir):
			os.makedirs(basedir)
		
		
		its = os.scandir(os.path.join(basedir, 'MetadataShares'))
		artcatalog = []
		for it in its:
			if it.name.endswith(".artist.txt"):
				with open(os.path.join(os.path.join(basedir, 'MetadataShares'), it.name)) as myfile: 
					if myfile.read()==art:
						artcatalog.append(it.name.replace(".artist.txt", ''))
		ret = None
		for it in artcatalog:
			with open(os.path.join(os.path.join(basedir, 'MetadataShares'), it+'.album.txt')) as myfile:
				if myfile.read()==alb:
					if os.path.exists(os.path.join(directory, it)):
						ret = it
		if not ret is None:
			return os.path.join(directory, ret)
		else:
			return None
			
class Handler:


	#shared video station descriptions, title and lists
	descs = {}
	titles = {}
	vlist = {}
	
	#currenlty selected video station, metadata for its vids, and selected vid
	v = None
	vip = None
	
	vtitles = {}
	vcategories = {}
	vartists = {}
	vdescriptions = {}
	
	vindexes = []
	
	tv = None
	

	b = None
	g = None

	dling = False
	
	def __init__(self, builder, gateway):
		global g
		global b
		b=builder
		g=gateway
		
	def getBuilder(self):
		return b
		
	def on_cbsinglestation_changed(self, *args):
		return
		#b.get_object("cjdradio_main_window").queue_draw()
		
	def onAddAccess(self, *args): 
		home = expanduser("~")
		basedir=os.path.join(home, ".cjdradio")
		
		
		ip = b.get_object("access_list_ip").get_text()
		peersList=''

		if os.path.exists(os.path.join(basedir, "settings_access_list.txt")): 
			with open(os.path.join(basedir,'settings_access_list.txt'), 'r') as myfile:
				peersList=myfile.read()
				myfile.close()
				
		peersList+=ip+"\n"	
				
		with open(os.path.join(basedir,'settings_access_list.txt'), 'w') as myfile:
			peersList=myfile.write(f"{peersList}")
			
		g.load_settings_from_disk()

	def onDeleteAccess(self, *args): 
		home = expanduser("~")
		basedir=os.path.join(home, ".cjdradio")
		
		
		ip = b.get_object("cb_access_list").get_active_text()
		peersList=''

		if os.path.exists(os.path.join(basedir, "settings_access_list.txt")): 
			with open(os.path.join(basedir,'settings_access_list.txt'), 'r') as myfile:
				peersList=myfile.read()
				myfile.close()
				
		newPeersList=[]
		
		for i in peersList.split("\n"): 
			if i!=ip and i!='':
				newPeersList.append(i)
				
		with open(os.path.join(basedir,'settings_access_list.txt'), 'w') as myfile:
			myfile.write("%s" % "\n".join(newPeersList))
			myfile.close()
		g.load_settings_from_disk()


		
	def onMove(self, args):
		libre = []
		mp3files = []
		
		libre.append(b.get_object("libre1").get_text())
		libre.append(b.get_object("libre2").get_text())
		libre.append(b.get_object("libre3").get_text())
		libre.append(b.get_object("libre4").get_text())
		libre.append(b.get_object("libre5").get_text())
		libre.append(b.get_object("libre6").get_text())
		libre.append(b.get_object("libre7").get_text())
		libre.append(b.get_object("libre8").get_text())
		libre.append(b.get_object("libre9").get_text())
		libre.append(b.get_object("libre10").get_text())
		libre.append(b.get_object("libre11").get_text())
		libre.append(b.get_object("libre12").get_text())
		libre.append(b.get_object("libre13").get_text())
		libre.append(b.get_object("libre14").get_text())
		libre.append(b.get_object("libre15").get_text())
		libre.append(b.get_object("libre16").get_text())
		libre.append(b.get_object("libre17").get_text())
		libre.append(b.get_object("libre18").get_text())
		libre.append(b.get_object("libre19").get_text())
		libre.append(b.get_object("libre20").get_text())
		libre.append(b.get_object("libre21").get_text())
		libre.append(b.get_object("libre22").get_text())
		libre.append(b.get_object("libre23").get_text())
		libre.append(b.get_object("libre24").get_text())
		libre.append(b.get_object("libre25").get_text())
		libre.append(b.get_object("libre26").get_text())
		libre.append(b.get_object("libre27").get_text())
		libre.append(b.get_object("libre28").get_text())
		
		shareddir = g.shared_dir
		
		home = expanduser("~")
		basedir=os.path.join(home, ".cjdradio")
		
		unshareddir = os.path.join(basedir, "Unshared")
		if not os.path.exists(unshareddir):
			os.makedirs(unshareddir)
		files = os.scandir(unshareddir)
		for mp3 in files: 
			if mp3.name.endswith(".mp3"):
				mp3files.append(mp3)
		counter = 0
		for mp3file in mp3files:
			tags = TinyTag.get(os.path.join(unshareddir, mp3file.name))
			
			tobemoved = False
			for l in libre: 
				if not tags.comment is None and l!= '' and l in tags.comment: 
					tobemoved = True
			if tobemoved: 
				counter=counter+1
				os.rename(os.path.join(unshareddir, mp3file.name), os.path.join(shareddir, mp3file.name))
		
		dialog = Gtk.MessageDialog(
					parent=b.get_object("cjdradio_main_window") ,
					modal=True,
					message_type=Gtk.MessageType.INFO,
					buttons=Gtk.ButtonsType.OK,
					text="Process finished.  "
				)
		dialog.format_secondary_text(str(counter)+" files moved as found sharables. They will be indexed upon next indexing. ")
		dialog.run()
		dialog.destroy()	
						
	def onMoveInverted(self, args):
		libre = []
		mp3files = []
		
		libre.append(b.get_object("libre1").get_text())
		libre.append(b.get_object("libre2").get_text())
		libre.append(b.get_object("libre3").get_text())
		libre.append(b.get_object("libre4").get_text())
		libre.append(b.get_object("libre5").get_text())
		libre.append(b.get_object("libre6").get_text())
		libre.append(b.get_object("libre7").get_text())
		libre.append(b.get_object("libre8").get_text())
		libre.append(b.get_object("libre9").get_text())
		libre.append(b.get_object("libre10").get_text())
		libre.append(b.get_object("libre11").get_text())
		libre.append(b.get_object("libre12").get_text())
		libre.append(b.get_object("libre13").get_text())
		libre.append(b.get_object("libre14").get_text())
		libre.append(b.get_object("libre15").get_text())
		libre.append(b.get_object("libre16").get_text())
		libre.append(b.get_object("libre17").get_text())
		libre.append(b.get_object("libre18").get_text())
		libre.append(b.get_object("libre19").get_text())
		libre.append(b.get_object("libre20").get_text())
		libre.append(b.get_object("libre21").get_text())
		libre.append(b.get_object("libre22").get_text())
		libre.append(b.get_object("libre23").get_text())
		libre.append(b.get_object("libre24").get_text())
		libre.append(b.get_object("libre25").get_text())
		libre.append(b.get_object("libre26").get_text())
		libre.append(b.get_object("libre27").get_text())
		libre.append(b.get_object("libre28").get_text())
		
		shareddir = g.shared_dir
		
		home = expanduser("~")
		basedir=os.path.join(home, ".cjdradio")
		
		unshareddir = os.path.join(basedir, "Unshared")
		if not os.path.exists(unshareddir):
			os.makedirs(unshareddir)
		files = os.scandir(shareddir)
		for mp3 in files: 
			if mp3.name.endswith(".mp3"):
				mp3files.append(mp3)
		counter = 0
		for mp3file in mp3files:
			tags = TinyTag.get(os.path.join(shareddir, mp3file.name))
			
			tobemoved = True
			for l in libre: 
				if not tags.comment is None and l!= '' and l in tags.comment: 
					tobemoved = False
			if tobemoved: 
				counter=counter+1
				os.rename(os.path.join(shareddir, mp3file.name), os.path.join(unshareddir, mp3file.name))
		
		dialog = Gtk.MessageDialog(
					parent=b.get_object("cjdradio_main_window") ,
					modal=True,
					message_type=Gtk.MessageType.INFO,
					buttons=Gtk.ButtonsType.OK,
					text="Process finished.  "
				)
		dialog.format_secondary_text(str(counter)+" files moved as found unsharables. They will be indexed upon next indexing. ")
		dialog.run()
		dialog.destroy()
						
	def onFullscreen(self, *args):
		self.tv.player.toggle_fullscreen()

	def onMoveHide(self, *args): 
		b.get_object("move_win").hide()
		return True

	def onMoveShow(self, *args): 
		b.get_object("move_win").show()

	def onAccessList(self, *args): 
		b.get_object("access_list_window").show()

	def onAccessListHide(self, *args): 
		b.get_object("access_list_window").hide()
		return True
	def onBlacklist(self, *args): 
		g.blacklist.append(g.radio.ip)
		g.radio.stop()
		g.radio.play()

		
		
		home = expanduser("~")
		basedir=os.path.join(home, ".cjdradio")
		
				
		with open(os.path.join(basedir,'settings_blacklist.txt'), 'w') as myfile:
			myfile.write("%s" % ("\n".join(g.blacklist)))
			myfile.close()
		g.load_settings_from_disk()
	def onClearBlacklist(self, *args):
		g.blacklist = [] 
		home = expanduser("~")
		basedir=os.path.join(home, ".cjdradio")
		with open(os.path.join(basedir,'settings_blacklist.txt'), 'w') as myfile:
			myfile.write("%s" % ("\n".join(g.blacklist)))
			myfile.close()
		g.load_settings_from_disk()


	def onBanArtist (self, *args): 
		g.blacklist.append(g.radio.artist)
		g.radio.stop()
		g.radio.play()

		
	def onClearBannedArtists (self, *args):
		g.bannedArtists = []
	def onRadio(self, *args): 
		if g.radio is None or (g.radio is not None and not g.radio.player.is_playing()):
			ir = internetRadio(g, b.get_object("nowplaying"), True)
			g.radio = ir
			ir.play()
		else:
			g.radio.stop()
			self.onRadio(args)
	def onRadioShares(self, *args): 
		if g.radio is None or (g.radio is not None and not g.radio.player.is_playing()):
			ir = internetRadio(g, b.get_object("nowplaying"), False, g.peers[0])
			g.radio = ir
			ir.play()
		else:
			g.radio.stop()
			self.onRadioShares(args)
	def onRadioSingle(self, *args): 
		if g.radio is None or (g.radio is not None and not g.radio.player.is_playing()):
			while g.cbsinglestationlock:
				sleep(0.5)
			ir = internetRadio(g, b.get_object("nowplaying"), False, b.get_object("cbsinglestation").get_active_text())
			g.radio = ir
			ir.play()
		else:
			g.radio.stop()
			self.onRadioSingle(args)
	def DL(self, *args): 
		home = expanduser("~")
		basedir=os.path.join(home, ".cjdradio")
		
		datadir=os.path.join(basedir, "Downloads")
		
		
		if not os.path.isdir(datadir):
			os.makedirs(datadir) 
		if not self.dling: 
			self.dling = True
			for p in g.peers: 
				flacsize = ''
				try: 
					flacsize = OcsadURLRetriever.retrieveURL("http://["+p+"]:55228/flac-size", reqtimeout = 8)
				except: 
					pass		
				
				if len(flacsize)>0: 
					catalog = []
					try:
						catalog = OcsadURLRetriever.retrieveURL("http://["+p+"]:55228/flac-catalog", 32000000).split("\n")
					except: 
						pass
					
					catalog.sort()
					for i in catalog: 
						if p!='' and i!='' and i!=p:
							
							finaldir=os.path.join(datadir, p.replace(":", "_"))
							
							
							if not os.path.isdir(finaldir):
								os.makedirs(finaldir)

							
							if self.dling and not os.path.exists(os.path.join(finaldir, i)):
								try: 
									temp = b""
									
									r = requests.get("http://["+p+"]:55228/flac?"+urllib.parse.quote(i, safe=''), timeout = 800, stream = True)
									for char in r.iter_content(1024):
										temp+=char
										if len(temp)>4000000000:
											temp=b""
											valid=False
											print("Flac file greater than 4 GiB received, aborting")
											break
									print ("Finished download")
									
									
									 
									
									if len(temp)>0:
										with open(os.path.join(finaldir, i), 'wb') as myfile:
											myfile.write(temp)
											myfile.close()

								except: 
									pass
		self.dling = False
		b.get_object("dlstatus").set_text("Stopped")
				
			
	def onDL(self, *args):
		if not self.dling:
			b.get_object("dlstatus").set_text("Running")
			t=Thread(target=self.DL)
			t.daemon = True
			t.start()
		else: 
			self.dling = False
			b.get_object("dlstatus").set_text("Stopped")
							
							
	def onComputeSize(self, *args):
		totalsize=0
		for p in g.peers: 
			flacsize = ''
			try: 
				flacsize = OcsadURLRetriever.retrieveURL("http://["+p+"]:55228/flac-size", reqtimeout = 8)
			except: 
				pass		
			
			if len(flacsize)>0: 
				totalsize+=int(flacsize)
		b.get_object("size").set_text(str(totalsize/1000000000)+" GiB")
			
	def onSkip (self, *args):
		print("Skipping")
		if g.radio!=None:
			print("found radio")
			if g.radio.player.is_playing():
				print("radio is playing")
				g.radio.stop()
				g.radio.play()
			else:
				g.radio.stop()
				if not g.radio.threadPlay is None:
					print ("radio is buffering")
					g.radio.bufferingLock = False
					g.radio.threadPlay.join(0)
					g.radio.play()
					
				
	def onStop (self, *args):
		print("Stopping")
		if g.radio!=None:
			print("found radio")
			if g.radio.player.is_playing():
				print("radio is playing")
				g.radio.stop()
				b.get_object("nowplaying").set_text("(nothing currently)")
			else:
				if not g.radio.threadPlay is None:
					print ("radio is buffering")
					g.radio.threadPlay.join(1)
				g.radio.stop()

	def onBanned(self, *args):
		g.bannedStations=[]
		g.get_builder().get_object("banned").set_label("Clear banned stations")

	def onDiscoverPeers(self, *args):
		g.registered = True
		b.get_object("discover_button").set_label("Discovering peers…")

		self.discoverPeers()


		b.get_object("cbsinglestation").remove_all()
		
		for i in g.peers:
			b.get_object("cbsinglestation").append_text(i)
		
		b.get_object("cbsinglestation").set_active(0)
		b.get_object("discover_button").set_label("Discover new stations peers ("+str(len(g.peers))+")")
		
		
	def discoverPeers(self):
		#import threading
		#lock=threading.Lock()
		#lock.acquire()
		
		#try: 
		g.set_processedPeers([])
		g.set_peers([])
		
		newpeers = []
		
		
		
		g.peers.append(g.get_settings_ip6addr())
		
		try: 
			newpeers = OcsadURLRetriever.retrieveURL("http://["+b.get_object("cb_initial_peers").get_active_text()+"]:55227/listpeers").split("\n")
		except: 
			dialog = Gtk.MessageDialog(
				parent=b.get_object("cjdradio_main_window") ,
				modal=True,
				message_type=Gtk.MessageType.INFO,
				buttons=Gtk.ButtonsType.OK,
				text="Sorry!  "
			)
			dialog.format_secondary_text("This initial peer is currently offline")
			dialog.run()
			dialog.destroy()
		
		newnewpeers = []
		for p in newpeers:
			if not p in g.peers: 
				newnewpeers.append(p)
		
		g.set_peers(g.peers+newnewpeers)
		
		dialog = Gtk.MessageDialog(
				parent=b.get_object("cjdradio_main_window") ,
				modal=True,
				message_type=Gtk.MessageType.INFO,
				buttons=Gtk.ButtonsType.OK,
				text="Discover finished.  "
			)
		dialog.format_secondary_text(str(len(g.get_peers()))+" peers discovered")
		dialog.run()
		dialog.destroy()
		#finally: 
		#	lock.release();




	def onDestroy(self, *args):
		g.get_webserver().shutdown()
		g.get_webserverThread().join(5)
		
		g.bannerdaemon_thread.join(1)
		g.scanThread.join(1)
		g.pingthread.join(1)
		g.crawler_thread.join(1)
		
		print("Stopped web server, bannerdaemon, ping and scan threads")
		Gtk.main_quit()
	def onID(self, *args):
		g.ID = b.get_object("station_id").get_text()

		home = expanduser("~")
		basedir=os.path.join(home, ".cjdradio")
		
		if not os.path.isdir(basedir):
			os.makedirs(basedir)


							
		with open(os.path.join(basedir,'settings_id.txt'), 'w') as myfile:
			myfile.write(f"{g.ID}")
			
			
	def onSystemPlayer(self, *args):
		print ("system player")
		home = expanduser("~")
		
		basedir=os.path.join(home, ".cjdradio")

		playlistfile = os.path.join(basedir, "playlist.m3u")
		
		unshare=os.path.join(basedir, "VideoUnshared")
		
		unsharemeta=os.path.join(basedir, "VideoUnsharedMetadata")
		
		filez=os.scandir(unshare)
		
		print("creating m3u playlist")
		output=''
		for file in filez: 
			if file.name.endswith(".mp4"):
				output+=os.path.join(unshare, file.name)+"\n"
		
		with open(playlistfile, 'w') as myfile:
			myfile.write(f"{output}")
			

		
		
		print("m3u playlist created, attempting to launch system player")
		try: 
			import subprocess, platform
			if platform.system() == 'Darwin':
				subprocess.call(('open', playlistfile))
			elif platform.system() == 'Windows':
				os.startfile(playlistfile)
			else:
				subprocess.call(('xdg-open', playlistfile))
		except: 
				dialog = Gtk.MessageDialog(
							parent=b.get_object("cjdradio_main_window") ,
							modal=True,
							message_type=Gtk.MessageType.INFO,
							buttons=Gtk.ButtonsType.OK,
							text="Small problem.  "
						)
				dialog.format_secondary_text("The file "+playlistfile+" was created OK but you will have to locate it and open it manually")
				dialog.run()
				dialog.destroy()

	def notImplemented(self, *args): 
		dialog = Gtk.MessageDialog(
					parent=b.get_object("cjdradio_main_window") ,
					modal=True,
					message_type=Gtk.MessageType.INFO,
					buttons=Gtk.ButtonsType.OK,
					text="Not implemented.  "
				)
		dialog.format_secondary_text("This feature is still to be developped.")
		dialog.run()
		dialog.destroy()



	def onVideoSaveToShares(self, *args):
		home = expanduser("~")
		
		basedir=os.path.join(home, ".cjdradio")

		videosharesdir=os.path.join(basedir, "VideoShares")

		print("Downloading")
		if self.tv!=None:
			print("found tv")
			home = expanduser("~")
			
			shared_dir=videosharesdir
			
			if not os.path.exists(os.path.join(shared_dir, self.tv.mp4)):
				
				os.rename(os.path.join(basedir, "temp.mp4"), os.path.join(shared_dir, self.tv.mp4))
				metadir = os.path.join(basedir, "VideoMetadata")
				
				if not os.path.isdir(metadir):
					os.mkdir(metadir)
				
				# saving metadata
				n=self.v.replace(".mp4", "", 1)
				if self.vartists[self.v]!= '' and not self.vartists[self.v]== None:
					with open(os.path.join(metadir,n+'.artist.txt'), 'w') as myfile:
						myfile.write("%s" % self.vartists[self.v])
						myfile.close()
				if self.vtitles[self.v]!= '' and not self.vtitles[self.v]== None:
					with open(os.path.join(metadir,n+'.title.txt'), 'w') as myfile:
						myfile.write("%s" % self.vtitles[self.v])
						myfile.close()
				if self.vcategories[self.v]!= '' and not self.vcategories[self.v]== None:
					with open(os.path.join(metadir,n+'.category.txt'), 'w') as myfile:
						myfile.write("%s" % self.vcategories[self.v])
						myfile.close()
				if self.vdescriptions[self.v]!= '' and not self.vdescriptions[self.v]== None:
					with open(os.path.join(metadir,n+'.description.txt'), 'w') as myfile:
						myfile.write("%s" % self.vdescriptions[self.v])
						myfile.close()

				
				
				dialog = Gtk.MessageDialog(
							parent=b.get_object("cjdradio_main_window") ,
							modal=True,
							message_type=Gtk.MessageType.INFO,
							buttons=Gtk.ButtonsType.OK,
							text="Success.  "
						)
				dialog.format_secondary_text("Video saved in Shares.")
				dialog.run()
				dialog.destroy()
				
			else: 
				dialog = Gtk.MessageDialog(
							parent=b.get_object("cjdradio_main_window") ,
							modal=True,
							message_type=Gtk.MessageType.INFO,
							buttons=Gtk.ButtonsType.OK,
							text="Failure.  "
						)
				dialog.format_secondary_text("There is already a file of this name in Shares. Maybe you already d/l'ed it? ")
				dialog.run()
				dialog.destroy()




	def onVideoSaveToUnshared(self, *args):
		home = expanduser("~")
		
		
		basedir=os.path.join(home, ".cjdradio")

		videounshareddir=os.path.join(basedir, "VideoUnshared")

		print("Downloading")
		if self.tv!=None:
			print("found tv")
			home = expanduser("~")
			
			shared_dir=videounshareddir
			
			if not os.path.exists(os.path.join(shared_dir, self.tv.mp4)):
				
				os.rename(os.path.join(basedir, "temp.mp4"), os.path.join(shared_dir, self.tv.mp4))
				
				metadir = os.path.join(basedir, "VideoUnsharedMetadata")
				
				if not os.path.isdir(metadir):
					os.mkdir(metadir)
				
				# saving metadata
				n=self.v.replace(".mp4", "", 1)
				if self.vartists[self.v]!= '' and not self.vartists[self.v]== None:
					with open(os.path.join(metadir,n+'.artist.txt'), 'w') as myfile:
						myfile.write("%s" % self.vartists[self.v])
						myfile.close()
				if self.vtitles[self.v]!= '' and not self.vtitles[self.v]== None:
					with open(os.path.join(metadir,n+'.title.txt'), 'w') as myfile:
						myfile.write("%s" % self.vtitles[self.v])
						myfile.close()
				if self.vcategories[self.v]!= '' and not self.vcategories[self.v]== None:
					with open(os.path.join(metadir,n+'.category.txt'), 'w') as myfile:
						myfile.write("%s" % self.vcategories[self.v])
						myfile.close()
				if self.vdescriptions[self.v]!= '' and not self.vdescriptions[self.v]== None:
					with open(os.path.join(metadir,n+'.description.txt'), 'w') as myfile:
						myfile.write("%s" % self.vdescriptions[self.v])
						myfile.close()

				
				
				dialog = Gtk.MessageDialog(
							parent=b.get_object("cjdradio_main_window") ,
							modal=True,
							message_type=Gtk.MessageType.INFO,
							buttons=Gtk.ButtonsType.OK,
							text="Success.  "
						)
				dialog.format_secondary_text("Video saved in Unshared.")
				dialog.run()
				dialog.destroy()
				
			else: 
				dialog = Gtk.MessageDialog(
							parent=b.get_object("cjdradio_main_window") ,
							modal=True,
							message_type=Gtk.MessageType.INFO,
							buttons=Gtk.ButtonsType.OK,
							text="Failure.  "
						)
				dialog.format_secondary_text("There is already a file of this name in Unshared. Maybe you already d/l'ed it? ")
				dialog.run()
				dialog.destroy()


	def onDownload (self, *args): 
		print("Downloading")
		if g.radio!=None:
			print("found radio")
			home = expanduser("~")
			basedir=os.path.join(home, ".cjdradio")
			
			shared_dir=os.path.join(basedir, "Shares")
			
			if not os.path.exists(os.path.join(shared_dir, g.radio.track)):
				g.radio.player.stop()
				
				os.rename(os.path.join(basedir, "temp.mp3"), os.path.join(shared_dir, g.radio.track))
				dialog = Gtk.MessageDialog(
							parent=b.get_object("cjdradio_main_window") ,
							modal=True,
							message_type=Gtk.MessageType.INFO,
							buttons=Gtk.ButtonsType.OK,
							text="Success.  "
						)
				dialog.format_secondary_text("Downloaded to Shares. MP3 will be indexed upon next reindexing. ")
				dialog.run()
				dialog.destroy()
				
				g.radio.play()
			else: 
				dialog = Gtk.MessageDialog(
							parent=b.get_object("cjdradio_main_window") ,
							modal=True,
							message_type=Gtk.MessageType.INFO,
							buttons=Gtk.ButtonsType.OK,
							text="Failure.  "
						)
				dialog.format_secondary_text("There is already a file of this name in Shares. Maybe you already d/l'ed it? ")
				dialog.run()
				dialog.destroy()
	
	def onDownloadUnshared (self, *args): 
		print("Downloading")
		if g.radio!=None:
			print("found radio")
			home = expanduser("~")
			basedir=os.path.join(home, ".cjdradio")
			
			shared_dir=os.path.join(basedir, "Unshared")
			
			if not (os.path.exists(shared_dir)):
				os.makedirs (shared_dir)
			
			if not os.path.exists(os.path.join(shared_dir, g.radio.track)):
				g.radio.player.stop()
				
				os.rename(os.path.join(basedir, "temp.mp3"), os.path.join(shared_dir, g.radio.track))
				dialog = Gtk.MessageDialog(
							parent=b.get_object("cjdradio_main_window") ,
							modal=True,
							message_type=Gtk.MessageType.INFO,
							buttons=Gtk.ButtonsType.OK,
							text="Success.  "
						)
				dialog.format_secondary_text("Downloaded to Unshared. MP3 will be indexed upon next reindexing. ")
				dialog.run()
				dialog.destroy()
				
				g.radio.play()
			else: 
				dialog = Gtk.MessageDialog(
							parent=b.get_object("cjdradio_main_window") ,
							modal=True,
							message_type=Gtk.MessageType.INFO,
							buttons=Gtk.ButtonsType.OK,
							text="Failure.  "
						)
				dialog.format_secondary_text("There is already a file of this name in Unshared. Maybe you already d/l'ed it? ")
				dialog.run()
				dialog.destroy()

			
	def onAddPeerIP(self, *args): 
		newIP=b.get_object("new_peer_ip").get_text()
		home = expanduser("~")
		basedir=os.path.join(home, ".cjdradio")
		
		if not os.path.isdir(basedir):
			os.makedirs(basedir)

		peersList=''

		if os.path.exists(os.path.join(basedir, "settings_peersList.txt")): 
			with open(os.path.join(basedir,'settings_peersList.txt'), 'r') as myfile:
				peersList=myfile.read()
				myfile.close()
				
		peersList+=newIP+"\n"	
				
		with open(os.path.join(basedir,'settings_peersList.txt'), 'w') as myfile:
			peersList=myfile.write(f"{peersList}")
			
		g.load_settings_from_disk()
		
	def onWebserverRestart(self, *args): 
		newIP=b.get_object("settings_ip6addr").get_text()
		
		home = expanduser("~")
		basedir=os.path.join(home, ".cjdradio")
		
			
		with open(os.path.join(basedir,'settings_ip6addr.txt'), 'w') as myfile:
			myfile.write(f"{newIP}")
			
			
		g.load_settings_from_disk();
		
		dialog = Gtk.MessageDialog(
				parent=b.get_object("cjdradio_main_window") ,
				modal=True,
				message_type=Gtk.MessageType.INFO,
				buttons=Gtk.ButtonsType.OK,
				text="Settings saved! "
			)
		dialog.format_secondary_text("Warning ! A restart of the app is required for your changes to take effect")
		dialog.run()
		dialog.destroy()
	def onVideoSkip (self, *args):
		self.tv.skip()
		
	def onVideoStop (self, *args):
		self.tv.stop()
	def onVideoBackward(self, *args):
		self.tv.player.set_time(self.tv.player.get_time()-30000)
	def onVideoForward(self, *args):
		self.tv.player.set_time(self.tv.player.get_time()+150000)


	def onVideoCrawl(self, *args):
		
		videopeers= []
		
		mypeers = g.get_peers()
		for p in mypeers:
			try:
				if OcsadURLRetriever.retrieveURL("http://["+p+"]:55229/ping", 12, 3) == "pong":
					videopeers.append(p)
					print ("crawling: video for "+p)
			except:
				print ("crawling: no video for "+p) 
		b.get_object("cbvideostations").remove_all()
		
		print ("crawling video peers for title and descriptions")
		
		
		for p in videopeers: 
			title = '(titleless)'
			description = '[no description provided]'
		
			try: 
				data=OcsadURLRetriever.retrieveURL("http://["+p+"]:55229/station-metadata", 32000, 3)
			except:
				data=""
			
			datas = data.split("\n")
			
			if datas[0]!='':
				title = datas[0]
			if len(datas)>1:
				description = "\n".join(datas[1:])
		
			self.titles[p] = title
			self.descs[p] = description
			
			
			try: 
				listing = OcsadURLRetriever.retrieveURL("http://["+p+"]:55229/mp4-catalog", 320000000, 6)
			except: 
				listing = ''
			self.vlist[p] = listing
				
		for p in videopeers:
			b.get_object("cbvideostations").append(p, "("+str(len(self.vlist[p].split("\n")))+")["+p+"]: "+self.titles[p]+"\n"+self.descs[p].replace("\n", " ")[:105]+"…")
			
		b.get_object("cbvideostations").set_active_id(videopeers[0])

	def onVideoPlay(self, *args):
		
		self.v=b.get_object("cbvideos").get_active_id()
		
		self.tv=internetTV(g, self)
		
		self.tv.play(self.vip, b.get_object("cbvideos").get_active_id())
		
		
		
	def onVideoConnect(self, *args): 
		station = b.get_object("cbvideostations").get_active_id()
		b.get_object("cbvideos").remove_all()
		self.vip = station
		print ("retrieving video list from"+station)

		print ("which is entitled:"+self.titles[station])

		print ("and describes itself as \""+self.descs[station]+"\"")
		print ("connecting…")

		try: 
			listing = OcsadURLRetriever.retrieveURL("http://["+station+"]:55229/mp4-catalog", 320000000, 6)
		except: 
			listing = ''
		self.vlist[station] = listing

		print (str(len(self.vlist[station].split("\n")))+" videos found, fetching their metadata")
		
		self.vtitles={}
		self.vcategories={}
		self.vartists={}
		self.vdescriptions={}
		self.vindexes=[]

		for v in self.vlist[station].split("\n"):
			if v!='' and v.endswith(".mp4"): 
				
				self.vindexes.append(v)
				
				data="\n\n\n\n"
				try: 
					data = OcsadURLRetriever.retrieveURL("http://["+station+"]:55229/mp4-metadata?"+urllib.parse.quote(v, safe=''), 3200000, 6).strip()
				except: 
					data = "Network error\nerror\nerror\nerror\n"
				
				datas=data.split("\n")
				
				if len(datas)==0: 
					datas.insert(0,"unavail")
				
					datas.insert(1,"unavail")
				
					datas.insert(2,"unavail")
				
					datas.insert(3,"unavail")

				if len(datas)==1: 
					datas.insert(1,"unavail")
				
					datas.insert(2,"unavail")
				
					datas.insert(3,"unavail")

				if len(datas)==2: 
				
					datas.insert(2,"unavail")
				
					datas.insert(3,"unavail")

				if len(datas)==3: 
				
					datas.insert(3,"unavail")
				
				self.vtitles[v]=datas[0]
				self.vcategories[v]=datas[1]
				self.vartists[v]=datas[2]
				self.vdescriptions[v]=datas[3]	

				vtext=""

				vtext +=v+"\n["+datas[1]+"]"+datas[0]
				
				if datas[2]!="unavail" and datas[2]!='':
					vtext+"\n"+datas[2]
				
				
				
				b.get_object("cbvideos").append(v, vtext)
				
			b.get_object("cbvideos").set_active(0)

			








					
class HTTPServerV6(ThreadingHTTPServer):
	address_family = socket.AF_INET6

class internetTV():
	
	g=None
	h=None
	ip=None
	mp4=None
	index = 0
	player=None;
	
	bufferingLock = False
	
	def __init__ (self, gateway, handler):
		self.g=gateway
		self.h=handler
		self.player = vlc.MediaPlayer()
		
	def play(self, myip, mymp4):
		self.g.get_builder().get_object("video_nowplaying").set_text("Buffering… Bytes received: estimation ongoing")
		 
		self.ip=myip
		self.mp4=mymp4
		
		self.index=self.h.vindexes.index(mymp4)
		
		
		self.threadPlay = Thread(target = self.playThread)
		self.threadPlay.start()
		
	def stop(self):
		self.player.stop()
		
	def playThread(self):
		print (self.mp4)
		
		home = expanduser("~")
		datadir=os.path.join(home, ".cjdradio")

		
		self.bufferingLock = True
		char_array=b""
		try:
			char_array = OcsadURLRetriever.retrieveURL("http://["+self.ip+"]:55229/mp4?"+urllib.parse.quote(self.mp4, safe=''), 1200000000, 30, False, 1024*1024, self.g.get_builder().get_object("video_nowplaying"))

			print ("Finished download")
		except:
			print (sys.exception().__traceback__)
			char_array=b""
	
	
		if len(char_array)>0 and self.bufferingLock: 
			home = expanduser("~")
			datadir=os.path.join(home, ".cjdradio")


			with open(os.path.join(datadir,'temp.mp4'), 'wb') as myfile:
				myfile.write(char_array)
				myfile.close()

			

			self.bufferingLock=False
			
			if self.player != None and self.player.is_playing():
				self.player.stop()
				
				
			
			media = self.player.get_instance().media_new(os.path.join(datadir,'temp.mp4'), "rb")
			
			self.player.set_media(media)
			
			
			self.g.get_builder().get_object("fsw").set_keep_above(True)
			self.g.get_builder().get_object("fsw").show()
			
			em=self.player.event_manager()
			em.event_attach(vlc.EventType.MediaPlayerEndReached, self.onEnded, self.player)
			caption = ''
			if not self.h.vartists[self.mp4]==None and not self.h.vartists[self.mp4]=='':
				caption+="["+self.h.vartists[self.mp4]+"] "
			caption+=self.h.vtitles[self.mp4]
			if not self.h.vdescriptions[self.mp4]==None and not self.h.vdescriptions[self.mp4]=='':
				caption+="\n"+self.h.vdescriptions[self.mp4]
			self.g.get_builder().get_object("video_nowplaying").set_text(caption)


			self.player.play()
			if not self.player.get_fullscreen():
				self.player.toggle_fullscreen()
			
	def onEnded(self, event, player):
		
		self.g.get_builder().get_object("fsw").hide()
		self.index=self.index+1
		
		if self.index<len(self.h.vindexes	):
			self.play (self.ip, self.h.vindexes[self.index])
	def skip(self):
		self.player.stop()
		

		
		self.g.get_builder().get_object("fsw").hide()
		self.index=self.index+1
		
		if self.index<len(self.h.vindexes):
			self.play (self.ip, self.h.vindexes[self.index])

class internetRadio(): 

	isMultiPeers = True
	g = None
	ips = []
	ip=''
	track = ''
	player=None
	
	threadPlay = None
	
	bufferingLock = True
	
	artist = ''
	
	def __init__ (self, gateway, display_text_setter, isMultiPeers = True, ip = '', ):
		self.ip=ip
		self.g=gateway
		self.isMultiPeers = isMultiPeers
		self.display = display_text_setter
		self.player = vlc.MediaPlayer()
		
	def play(self):
		self.threadPlay = Thread(target = self.playThread)
		self.threadPlay.start()
		
	def playThread(self):
		running = True
		
		import threading



		#lock = threading.Lock()
		#lock.acquire()
		#try: 
		self.display.set_text("Selecting a station and buffering…")
		#finally: 
		#	lock.release()			

	
	
		if self.isMultiPeers: 
			self.ip = ''
			while self.ip == '':
				peer = ''
				while peer=='' or peer in self.g.bannedStations or peer in self.g.blacklist:
					while len(self.g.get_peers())==0:
						sleep(6)
					
					localPeers = self.g.get_peers().copy()
					
					for p in self.g.get_peers():
						if p in g.plussed:
							dex=0;
							while dex<g.plussed[p]:
								localPeers.append(p)
								dex=dex+1
					
										
					tmpPeer = random.choice (localPeers)
					try: 
						pong = ''
						pong = OcsadURLRetriever.retrieveURL("http://["+tmpPeer+"]:55227/ping",  max_length = 120000, reqtimeout = 8)
						if pong!='pong':
							raise ValueError("no replying peer on song request")
						else:
							peer = tmpPeer
							self.ip = tmpPeer
					except: 
						while g.cbsinglestationlock:
							sleep (0.5)

						g.cbsinglestationlock = True
						try: 
							self.g.bannedStations.append(tmpPeer)
						finally: 
							g.cbsinglestationlock = False

						while g.cbsinglestationlock:
							sleep (0.5)
						
						if len(sys.argv) == 1:
							self.g.get_builder().get_object("cbsinglestation").remove_all()
						
						
						
						for i in self.g.peers: 
							if i not in self.g.bannedStations:
								while g.cbsinglestationlock:
									sleep (0.5)
								
								g.cbsinglestationlock = True
								try: 
									if len(sys.argv)==1:
										self.g.get_builder().get_object("cbsinglestation").append_text(i)
										self.g.get_builder().get_object("cbsinglestation").set_active(0)
								finally: 
									g.cbsinglestationlock = False	
		else: 
			try: 
				pong = ''
				pong = OcsadURLRetriever.retrieveURL("http://["+self.ip+"]:55227/ping", reqtimeout = 8)
				#print (pong)
				if pong!='pong':
					raise ValueError("no replying peer on song request")
			except: 
				#lock = threading.Lock()
				#lock.acquire()
		
				try: 
					while g.cbsinglestationlock:
						sleep (0.5)
					self.g.bannedStations.append(self.ip)
					self.g.get_builder().get_object("cbsinglestation").remove_all()
					for i in self.g.peers: 
						if i not in self.g.bannedStations:
							while g.cbsinglestationlock:
								sleep (0.5)
							
							self.g.get_builder().get_object("cbsinglestation").append_text(i)

					while g.cbsinglestationlock:
						sleep (0.5)
					self.g.get_builder().get_object("cbsinglestation").set_active(0)
					#lock.release()
					return
				finally:
					print("Play detected a station to ban: "+self.ip) 
					#lock.release()
			
			

		
		char_array=b""
		running = True

		while len(char_array)==0 and running:

			song = ''

			try: 
				song = OcsadURLRetriever.retrieveURL("http://["+self.ip+"]:55227/random-mp3");
				if len(song.split('\n'))<4:
					song = ''
					running = False
			except: 
				print("Could not contact IP "+self.ip)
				
				
			
			if song!='':
				self.track=song.strip().split('\n')[0]
				print (self.track)
				self.artist = song.strip().split("\n")[1]
				
				if self.artist in g.bannedArtists: 
					self.play()
					return
				#add metadata
				valid=True
			
				r = requests.get("http://["+self.ip+"]:55227/mp3?"+urllib.parse.quote(self.track, safe=''), timeout = 18, stream = True)
				self.bufferingLock = True
				try:
					for char in r.iter_content(1024):
						#lock = threading.Lock()
				
						#lock.acquire()
						#try: 
						if self.bufferingLock:
							char_array+=char
						else:
							raise ValueError("Skip")
						#finally: 
							#lock.release()
						if len(char_array)>32000000:
							char_array=b""
							valid=False
							print("MP3 file greater than 32000 kilibytes, or Skip signal, received, aborting")
							break
					print ("Finished download")
				except:
					char_array=b""
			
			
				if len(char_array)>0 and self.bufferingLock: 
					home = expanduser("~")
					datadir=os.path.join(home, ".cjdradio")


					with open(os.path.join(datadir,'temp.mp3'), 'wb') as myfile:
						myfile.write(char_array)
						myfile.close()
					if not self.player is None and self.player.is_playing():
						self.player.stop() 
					
					self.player = vlc.MediaPlayer(os.path.join(datadir,'temp.mp3'), 'rb')
					em = self.player.event_manager()
					em.event_attach(vlc.EventType.MediaPlayerEndReached, self.onEnded, self.player)

					

					
					self.display.set_text(song.split("\n")[1]+" - "+song.split("\n")[3]+" ["+song.split("\n")[2]+"]\n"+self.track)
					
					myid = "Another random"
					
					try: 
						myid = OcsadURLRetriever.retrieveURL("http://["+self.ip+"]:55227/id")
						
					except: 
						myid = "<unknown>"
					if len(myid)>60:
						myid = myid[0-60]	
					#lock = threading.Lock()
					#lock.acquire()
					
					#try: 
					if len(sys.argv)==1: 
						self.g.get_builder().get_object("lasttuned").set_text(self.ip+"\n"+myid)
					print ("current station: "+self.ip+"\n"+myid)
					#finally: 
					#	lock.release()
				try: 
					self.player.play()
				except: 
					self.playThread()
		if not running: 
			self.playThread()
	def stop(self):
		self.player.stop()
	
	def onEnded(self, event, player): 
		#import threading
		#lock = threading.Lock()
		#lock.acquire()
		
		#try: 
		self.play();
		#finally: 
		#	lock.release()

class OcsadURLRetriever:
	def retrieveURL(url, max_length = 32000, reqtimeout = 800, decode=True, iteration=1024, text_setter=None):
		try: 
			r = requests.get(url, timeout=reqtimeout, stream=True)
			char_array=b"";
			for char in r.iter_content(iteration):
				char_array+=char
				if not text_setter == None:
					text_setter.set_text("Buffering… Received "+str(len(char_array))+" bytes")
				if len(char_array)>max_length:
					raise ValueError("Invalid Ocsad URL")
			if decode:			
				return char_array.decode("utf-8")
			else:
				return char_array
		except(TimeoutError):
			raise ValueError("Invalid Ocsad URL")
		except: 
			raise


class WebRequestHandlerVideo(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			self.gateway.httpLock=self.gateway.httpLock+1
			
			if self.gateway.httpLock>125:
				return
			touch (g.tmplock)

			home = expanduser("~")
			basedir=os.path.join(home, ".cjdradio")

			path = urllib.parse.urlparse(self.path).path
			query = urllib.parse.urlparse(self.path).query

			
			self.send_response(200)
		

			if (path!="/mp4"):
				self.send_header("Content-Type", "text/plain")
			else:
				self.send_header("Content-Type", "video/mp4")

			self.end_headers()

			if path=="/":
				self.wfile.write("Cjdradio\n0.3\nhttps://github.com/shangril/cjdradio".encode("utf-8"))
			if path=="/ping":
				self.wfile.write("pong".encode("utf-8"))




			
			if path=='/mp4':
				print (query)
				basename = os.path.basename(urllib.parse.unquote(query))
				filepath = os.path.join(os.path.join(basedir, "VideoShares"), basename)
				if basename.endswith(".mp4") and os.path.exists(filepath):
					with open(filepath, 'rb') as myfile:
						while True:
							chunk = myfile.read(4096)
							if not chunk:
								break
							self.wfile.write(chunk)

			if path=="/mp4-catalog": 
				reply = ''
				completed = False
				while not completed:
						mp4files=[]
						files = sorted(os.listdir(os.path.join(basedir, "VideoShares")))
						for mp4 in files: 
							if mp4.endswith(".mp4"):
								mp4files.append(mp4)
								
						if len(mp4files)>0:
							size = 0		
							for mp4 in mp4files:
								reply+=mp4+"\n"
								
							completed = True
						else:
							reply=""
							completed = True
				self.wfile.write(reply.encode("utf-8"))
			if path=="/mp4-metadata":
				basename = os.path.basename(urllib.parse.unquote(query))
				filepath = os.path.join(os.path.join(basedir, "VideoShares"), basename)
				metadatapath = os.path.join(basedir, "VideoMetadata")
				reply=''

				if basename.endswith(".mp4") and os.path.exists(filepath) and os.path.exists(metadatapath):
					
					title = ''
					artist = ''
					category = ''
					description = ''
					
					titlefilepath = os.path.join(metadatapath, basename.replace(".mp4", ".title.txt"))
					artistfilepath = os.path.join(metadatapath, basename.replace(".mp4", ".artist.txt"))
					categoryfilepath = os.path.join(metadatapath, basename.replace(".mp4", ".category.txt"))
					descriptionfilepath = os.path.join(metadatapath, basename.replace(".mp4", ".description.txt"))


					if os.path.exists(titlefilepath):
						with open(titlefilepath, 'r') as myfile:
									title = myfile.read().replace("\n", "")
									myfile.close()
					if os.path.exists(categoryfilepath):
						with open(categoryfilepath, 'r') as myfile:
									category = myfile.read().replace("\n", "")
									myfile.close()
					if os.path.exists(artistfilepath):
						with open(artistfilepath, 'r') as myfile:
									artist = myfile.read().replace("\n", "")
									#artist found! override category to "Music"
									category = "Music"
									myfile.close()
					if os.path.exists(descriptionfilepath):
						with open(descriptionfilepath, 'r') as myfile:
									description = myfile.read().replace("\n", "")
									myfile.close()
					
					reply = title+"\n"+category+"\n"+artist+"\n"+description+"\n"
					
					

				self.wfile.write(reply.encode("utf-8"))
				
				
			if path=="/station-metadata":
				metadatapath = os.path.join(basedir, "VideoMetadata")
				reply=''
				stationtitlefilepath = os.path.join(metadatapath, "station_title.txt")
				stationdescriptionfilepath = os.path.join(metadatapath, "station_description.txt")

				title = ''
				description = ''

				if os.path.exists(stationtitlefilepath):
					with open(stationtitlefilepath, 'r') as myfile:
								title = myfile.read().strip()
								myfile.close()

				if os.path.exists(stationdescriptionfilepath):
					with open(stationdescriptionfilepath, 'r') as myfile:
								description = myfile.read().strip()
								myfile.close()
				reply = title+"\n"+description+"\n"

				self.wfile.write(reply.encode("utf-8"))


		finally:
			touch (g.tmplock)
			try:
				os.unlink(g.tmplock)
			except: 
				print ("unable to unlink "+g.tmplock)
			self.gateway.httpLock=self.gateway.httpLock-1


class WebRequestHandlerFlac(BaseHTTPRequestHandler):
	gateway = None
		
	def do_GET(self):
		try:
			self.gateway.httpLock=self.gateway.httpLock+1
			
			if self.gateway.httpLock>125:
				return
			
			touch (g.tmplock)
	
			home = expanduser("~")
			basedir=os.path.join(home, ".cjdradio")

			path = urllib.parse.urlparse(self.path).path
			query = urllib.parse.urlparse(self.path).query

			
			self.send_response(200)
		

			if (path!="/mp3" and path!="/flac"):
				self.send_header("Content-Type", "text/plain")
			else:
				if path=="/mp3": 
					self.send_header("Content-Type", "audio/mpeg")
				if path=="/flac":
					self.send_header("Content-Type", "audio/flac")
			
			self.end_headers()

			if path=="/":
				self.wfile.write("Cjdradio\n0.3\nhttps://github.com/shangril/cjdradio".encode("utf-8"))
			if path=="/ping":
				self.wfile.write("pong".encode("utf-8"))

			if path=='/flac':
				print (query)
				basename = os.path.basename(urllib.parse.unquote(query))
				filepath = os.path.join(g.shared_dir, basename)
				if basename.endswith(".flac") and os.path.exists(filepath):
					with open(filepath, 'rb') as myfile:
						while True:
							chunk = myfile.read(4096)
							if not chunk:
								break
							self.wfile.write(chunk)
				
			if path=="/flac-size": 
				reply = ''
				completed = False
				while not completed:
						flacfiles=[]
						files = os.scandir(g.shared_dir)
						for flac in files: 
							if flac.name.endswith(".flac"):
								flacfiles.append(flac.name)
								
						if len(flacfiles)>0:
							size = 0		
							for flac in flacfiles:
								filepath = os.path.join(g.shared_dir, flac)
								flacsize = os.path.getsize(filepath)
								
								size += flacsize
							reply = str(size)
							completed = True
						else:
							reply="0"
							completed = True
				self.wfile.write(reply.encode("utf-8"))
			if path=="/flac-catalog": 
				reply = ''
				completed = False
				while not completed:
						flacfiles=[]
						files = os.scandir(g.shared_dir)
						for flac in files: 
							if flac.name.endswith(".flac"):
								flacfiles.append(flac.name)
								
						if len(flacfiles)>0:
							size = 0		
							for flac in flacfiles:
								reply+=flac+"\n"
								
							completed = True
						else:
							reply=""
							completed = True
				self.wfile.write(reply.encode("utf-8"))
		finally:
			touch (g.tmplock)
			try:
				os.unlink(g.tmplock)
			except: 
				print ("unable to unlink "+g.tmplock)
			self.gateway.httpLock=self.gateway.httpLock-1

class TUIDisplay: 
	def set_text(self, text):
		print(text)
		print ("Press Enter to skip current song, enter \"help\" to list available commands, or [Ctrl+C] to quit\n")
	
class WebRequestHandler(BaseHTTPRequestHandler):
	gateway = None
		
	def do_GET(self):

		try:

			self.gateway.httpLock=self.gateway.httpLock+1
			
			if self.gateway.httpLock>125:
				return

			touch (g.tmplock)
		

			home = expanduser("~")
			basedir=os.path.join(home, ".cjdradio")

			path = urllib.parse.urlparse(self.path).path
			query = urllib.parse.urlparse(self.path).query
		
			self.send_response(200)
			self.send_header("Server", "Cjdradio")
			if (path!="/mp3" and path!="flac" and path!="/albimg"):
				self.send_header("Content-Type", "text/plain")
			else:
				if path=="/mp3": 
					self.send_header("Content-Type", "audio/mpeg")
				if path=="/flac":
					self.send_header("Content-Type", "audio/flac")
				if path=="/podcast":
					self.send_header("Content-Type", "application/rss+xml; charset=utf-8")
			self.end_headers()
			reply="Cjdradio\n"
			reply=reply+"Version: 0.3\n"
			

			
			if path=="/":
				self.wfile.write("Cjdradio\n0.3\nhttps://github.com/shangril/cjdradio".encode("utf-8"))
			if path=="/ping":
				self.wfile.write("pong".encode("utf-8"))

			if path=="/listpeers":
				try: 
					if not self.client_address[0] in self.gateway.peers and self.client_address!="::":
						self.gateway.get_peers().append(self.client_address[0])
				except: 
					pass
				self.wfile.write("\n".join(self.gateway.get_peers()).encode("utf-8"))
			if path=="/id":
				import threading
				lock = threading.Lock()
				lock.acquire()
				try: 
					self.wfile.write(self.gateway.ID.encode("utf-8"))
				finally: 
					lock.release()
			if path=="/random-mp3":
				if not self.client_address[0] in self.gateway.peers:
					try:
						if not self.client_address[0] in self.gateway.peers and self.client_address!="::":
							self.gateway.get_peers().append(self.client_address[0])
					except:
						pass
				reply = ''
				completed = False
				while not completed:
						mp3files=[]
						files = os.scandir(g.shared_dir)
						for mp3 in files: 
							if mp3.name.endswith(".mp3"):
								mp3files.append(mp3)
						if self.client_address[0]==g.settings_ip6addr or self.client_address[0] in g.accessList: #localmachine or allowed one
							unshareddir=os.path.join(basedir, "Unshared")
							if not os.path.exists(unshareddir):
								os.makedirs(unshareddir)
							files = os.scandir(unshareddir)
							for mp3 in files: 
								if mp3.name.endswith(".mp3"):
									mp3files.append(mp3)
									
									

						if len(mp3files)>0:		
							mp3=random.choice(mp3files)
							artist=''
							album=''
							title=''
							datadir = os.path.join(basedir, "MetadataShares")
							if os.path.exists(os.path.join(datadir, mp3.name+".artist.txt")) and os.path.exists(os.path.join(datadir, mp3.name+".album.txt")) and os.path.exists(os.path.join(datadir, mp3.name+".title.txt")):
								with open(os.path.join(datadir,mp3.name+'.artist.txt'), 'r') as myfile:
									artist = myfile.read()
									myfile.close()
								with open(os.path.join(datadir,mp3.name+'.album.txt'), 'r') as myfile:
									album = myfile.read()
									myfile.close()
								with open(os.path.join(datadir,mp3.name+'.title.txt'), 'r') as myfile:
									title = myfile.read()
									myfile.close()
								if artist != '' and album != '' and title != '':
									reply = mp3.name+"\n"+artist+"\n"+album+"\n"+title
									completed = True
						else:

							reply+="No mp3 found, sorry!"
							completed = True
				self.wfile.write(reply.encode("utf-8"))
			if path=='/wall':
				print("WALL "+self.client_address[0]+": "+os.path.basename(urllib.parse.unquote(query))[0:197])
			if path=='/mp3':
				print (query)
				basename = os.path.basename(urllib.parse.unquote(query))
				filepath = os.path.join(g.shared_dir, basename)
				if basename.endswith(".mp3") and os.path.exists(filepath):
					with open(filepath, 'rb') as myfile:
						while True:
							chunk = myfile.read(4096)
							if not chunk:
								break
							self.wfile.write(chunk)
				else: 
					if self.client_address[0]==g.settings_ip6addr or self.client_address[0] in g.accessList: 
					#local machine or allowed one
						unshareddir=os.path.join(basedir, "Unshared")
						if not os.path.exists(unshareddir):
							os.makedirs(unshareddir)

						filepath = os.path.join(unshareddir, basename)
						if basename.endswith(".mp3") and os.path.exists(filepath):

							with open(filepath, 'rb') as myfile:
								while True:
									chunk = myfile.read(4096)
									if not chunk:
										break
									self.wfile.write(chunk)
			if path=="/mp3-catalog": 
				reply = ''
				completed = False
				while not completed:
						flacfiles=[]
						files = os.scandir(g.shared_dir)
						for flac in files: 
							if flac.name.endswith(".mp3"):
								flacfiles.append(flac.name)
								
						if len(flacfiles)>0:
							size = 0		
							for flac in flacfiles:
								reply+=flac+"\n"
								
							completed = True
						else:
							reply=""
							completed = True
				self.wfile.write(reply.encode("utf-8"))
			if path=="/haspodcast":
				if g.podcast:
					reply="1"
					self.wfile.write(reply.encode("utf-8"))
			if path=="/podcast":
				#reply = OcsadURLRetriever.retrieveURL(g.podcaster.proxy_url+"?"+query, 128000000, 8000)
				#self.wfile.write(reply.encode("utf-8"))
				querystring = ""
				if query != "":
					querystring="?"+query
		
				link = """http://["""+g.get_settings_ip6addr()+"""]:55227/podcast"""+querystring
				
				shareddir = g.shared_dir 
				datadir = os.path.join(basedir, "MetadataShares")
				unshareddatadir = os.path.join(basedir, "MetadataUnhared")

				files = os.scandir(shareddir)
				title = None
				album = None
				artist = None
				file = None
				duration = None
				albindex={}
				artindex={}
				i=1
				files = os.scandir(shareddir)
				if self.client_address[0]==g.settings_ip6addr or self.client_address[0] in g.accessList: 
					#local machine or allowed one
						unshareddir=os.path.join(basedir, "Unshared")
						files = list(files) + list(os.scandir(unshareddir))
				for mp3 in files: 
					if mp3.name.endswith(".mp3"):
						album = None
						while album is None:
							if os.path.exists(os.path.join(datadir, mp3.name+".album.txt")):
								with open(os.path.join(datadir,mp3.name+'.album.txt'), 'r') as myfile:
									album=myfile.read()	
							#tag scanner hasn't still processed this file, sleeping
							else:
								sleep(5)
						if not album in albindex:
							albindex[album]=i
							i=i+1
						
				whitelist = None
				if os.path.exists(os.path.join(basedir, "podcast-artists-whitelist.txt")):
								with open(os.path.join(basedir,'podcast-artists-whitelist.txt'), 'r') as myfile:
									whitelist=myfile.read().strip("\n").split("\n")		
				else:
					print ("No podcast-artist-whitelist.txt defined in "+basedir)		
				files = os.scandir(shareddir)
				if self.client_address[0]==g.settings_ip6addr or self.client_address[0] in g.accessList: 
					#local machine or allowed one
						unshareddir=os.path.join(basedir, "Unshared")
						files = list(files) + list(os.scandir(unshareddir))

				
				for mp3 in files: 
					if mp3.name.endswith(".mp3"):
						artist = None
						while artist is None:
							if os.path.exists(os.path.join(datadir, mp3.name+".artist.txt")):
								with open(os.path.join(datadir,mp3.name+'.artist.txt'), 'r') as myfile:
									artist=myfile.read()		
							elif os.path.exists(os.path.join(unshareddatadir, mp3.name+".artist.txt")):
								with open(os.path.join(unshareddatadir,mp3.name+'.artist.txt'), 'r') as myfile:
									artist=myfile.read()
							#tag scanner hasn't still processed this file, sleeping
							else:
								sleep(5)
						if not artist is None:
							artindex[artist]=artist
				files = os.scandir(shareddir)
				if self.client_address[0]==g.settings_ip6addr or self.client_address[0] in g.accessList: 
					#local machine or allowed one
						unshareddir=os.path.join(basedir, "Unshared")
						files = list(files) + list(os.scandir(unshareddir))
				chantitle=g.ID
				if query!='':
					chantitle=urllib.parse.unquote_plus(query.replace('artist=', ''))
				pod="""<?xml version="1.0" encoding="UTF-8"?>
				<rss xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:podcast="https://podcastindex.org/namespace/1.0" version="2.0">
				<channel>
					<title><![CDATA["""+chantitle+"""]]></title>
					<itunes:category text="Music"/>
					<description><![CDATA["""+g.ID+"""]]></description>
					<itunes:author><![CDATA["""+g.ID+"""]]></itunes:author>
					<link>"""+link+"""</link>
				"""
				if query=='' and len(artindex)>0:
					pod=pod+"<podcast:podroll>"
					for art in artindex:
						if whitelist is None or (whitelist is not None and art in whitelist):
							pod=pod+"""
							<podcast:remoteItem feedUrl=\""""+link+'?artist='+urllib.parse.quote(art)+"""\"/>
							"""
					pod=pod+"</podcast:podroll>"
				
				albcovers = {}
				if not g.podcaster.coversfile is None and os.path.exists(g.podcaster.coversfile):
					with open(g.podcaster.coversfile, 'r') as myfile:
						albz = myfile.read().strip("\n").split("\n")
						i=0
						while i<len(albz):
							albcovers[albz[i]]=albz[i+1]
							i=i+2
					
				
				for mp3 in files: 
					if mp3.name.endswith(".mp3"):
						title = None
						album = None
						artist = None
						file = None
						duration = None
						while title is None or album is None or artist is None or file is None or duration is None:
			
							if os.path.exists(os.path.join(datadir, mp3.name+".artist.txt")):
								with open(os.path.join(datadir,mp3.name+'.artist.txt'), 'r') as myfile:
									artist=myfile.read()
							elif os.path.exists(os.path.join(unshareddatadir, mp3.name+".artist.txt")):
								with open(os.path.join(unshareddatadir,mp3.name+'.artist.txt'), 'r') as myfile:
									artist=myfile.read()
							if os.path.exists(os.path.join(datadir, mp3.name+".album.txt")):
								with open(os.path.join(datadir,mp3.name+'.album.txt'), 'r') as myfile:
									album=myfile.read()
							elif os.path.exists(os.path.join(unshareddatadir, mp3.name+".album.txt")):
								with open(os.path.join(unshareddatadir,mp3.name+'.album.txt'), 'r') as myfile:
									album=myfile.read()		
							if os.path.exists(os.path.join(datadir, mp3.name+".title.txt")):
								with open(os.path.join(datadir,mp3.name+'.title.txt'), 'r') as myfile:
									title=myfile.read()
							elif os.path.exists(os.path.join(unshareddatadir, mp3.name+".title.txt")):
								with open(os.path.join(unshareddatadir,mp3.name+'.title.txt'), 'r') as myfile:
									title=myfile.read()
							if os.path.exists(os.path.join(datadir, mp3.name+".duration.txt")):
								with open(os.path.join(datadir,mp3.name+'.duration.txt'), 'r') as myfile:
									duration=myfile.read()
							elif os.path.exists(os.path.join(unshareddatadir, mp3.name+".duration.txt")):
								with open(os.path.join(unshareddatadir,mp3.name+'.duration.txt'), 'r') as myfile:
									duration=myfile.read()
							
							file = mp3.name
					
							#tag scanner hasn't still processed this file, sleeping
							if title is None or album is None or artist is None or file is None or duration is None:
								sleep(5)
						if query=='' or (artist==urllib.parse.unquote_plus(query.replace('artist=', ''))):
							pod = pod + """<item>
							<title><![CDATA["""+title+"""]]></title>
							<podcast:season name=\""""+html.escape(album[0:127])+"""\">"""+str(albindex[album])+"""</podcast:season>
							<enclosure url="http://["""+g.settings_ip6addr+"""]:55227/mp3?"""+urllib.parse.quote(file)+"""\""""
							if os.path.exists(os.path.join(shareddir, file)):
								pod=pod+""" length=\""""+str(os.path.getsize(os.path.join(shareddir, file)))+"""\""""
							else:
								pod=pod+""" length=\""""+str(os.path.getsize(os.path.join(unshareddir, file)))+"""\""""
							 
							pod=pod+""" type="audio/mpeg"/>
							 <guid>"""+urllib.parse.quote(artist)+'_'+urllib.parse.quote(album)+'_'+urllib.parse.quote(title)+'_'+"""</guid>
							 <link><![CDATA[http://["""+g.settings_ip6addr+"""]:55227/mp3?"""+urllib.parse.quote(file)+"""]]></link>"""
							if os.path.exists(os.path.join(shareddir, file)):
								pod=pod+"""<pubDate>"""+formatdate(os.path.getmtime(os.path.join(shareddir, file)))+"""</pubDate>"""
							else:
								pod=pod+"""<pubDate>"""+formatdate(os.path.getmtime(os.path.join(unshareddir, file)))+"""</pubDate>"""
							pdo=pod+"""<itunes:duration>"""+duration+"""</itunes:duration>"""
							if album in albcovers.keys():
								pod=pod+f"""<itunes:image href=\"http://["""+g.settings_ip6addr+"""]:55227/albimg?"""+urllib.parse.quote(album)+"""\"/>"""
							else:
								pod=pod+f"""<itunes:image href=\"http://["""+g.settings_ip6addr+"""]:55227/albimg?"""+urllib.parse.quote(album)+f"""&amp;{urllib.parse.quote(artist)}\"/>"""
							pod = pod+"""</item>
							"""
				
				pod = pod+"</channel></rss>"
				self.wfile.write(pod.encode("utf-8"))
			
			if (path=="/albimg"):
				albcovers = {}
				if not g.podcaster.coversfile is None and os.path.exists(g.podcaster.coversfile):
					with open(g.podcaster.coversfile, 'r') as myfile:
						albz = myfile.read().strip("\n").split("\n")
						i=0
						while i<len(albz):
							albcovers[albz[i]]=albz[i+1]
							i=i+2
				ran = False		
				if not '&' in query and urllib.parse.unquote(query) in albcovers.keys():
					with open(g.podcaster.coversdir+os.path.basename(albcovers[urllib.parse.unquote(query)]), 'rb') as myfile:
						if os.path.basename(urllib.parse.unquote(query)).endswith(".jpg") or os.path.basename(urllib.parse.unquote(query)).endswith(".jpeg"):
							self.send_header("Content-Type", "image/jpeg")
						elif os.path.basename(urllib.parse.unquote(query)).endswith(".png"):
							self.send_header("Content-Type", "image/png")
						elif os.path.basename(urllib.parse.unquote(query)).endswith(".gif"): 
							self.send_header("Content-Type", "image/gif")
						self.wfile.write(myfile.read())
						ran = True
				elif hasmutagen and len("".join(query).split('&'))>=2:
					tart = urllib.parse.unquote("".join(query).split('&')[1])
					talb = urllib.parse.unquote("".join(query).split('&')[0])
					directory = g.shared_dir
					file = g.findAFile(tart, talb, directory)
					if file is None:
						directory = os.path.join(basedir, "Unshared")
					file = g.findAFile(tart, talb, directory)
					if not file is None:
						tags = ID3(file)

						for tag in tags.values():
							if tag.FrameID == "APIC":
									self.send_header("Content-type", tag.mime)
									self.wfile.write(tag.data)
									ran=True

					
				if not ran:		
					base64data="""R0lGODdhuAu4C+cAAAIFARIDBBgEBx4EAiIFBSYFCCsFBC8EBzUDBA8QBDcEBjEGCjkGCUAFCEcEBjsIBEEGCU8DBUIHChMXBkkGCVAEB0oHClEFCBYYAFoEB1MHC2IDDlwGCmMED2wCDlUKDRwdAmUGCm0ED14JDW4FEGcIDHcDD4ABDm8HC28HEWgKDXgFEHAIDIEDDyEiAnkHEXIKDYIFEIsCFXoJEnMMDoMHEYwEFZYBFCInASYmAXsLE4QJEo4GEY0GFn0MDpcEFSUqBoYLEo8JEZgGFocNE6IFFpALEpkIF6wCGpENEyovBJoLGKQIF60FG5IPFLgDG5sNGCwxB64HHKULF8MCG50PE7AKF7kHHKYOGMQFHDA1BLENGLoKHc8EITM3B8UJHKkSGrIQGdoDIbwNHTY6AuUBJ9AIIrMSGccMHTg7BL0QHtsHItILHb4SGecFIb4SH8gPHtEMI/IDJzw/CN0LI8kSH9MPHugJIsoUID9CA94OJNQSHvMIKOkNI9UUH0JEBt8SJEFIAPUNKeAUJesRJPYQJOIXJkRLA+wUJfYRKklLBPcUJO0XJkZOBvcUK0hQCPkXJUtRAE1TAk5UA1FXB1NZCVVaAFZcAlheBF1iCl9kAWJnBF9pBWFrCGdrC2VvAGdwAmhyBGx1Cm53AHB4AHF6AnN7BHV9CHd/C3iADXqBAHuDAXyEA36FBn+HCYGIC4OKDoWLAIeOA4mPBouRCoeTCoiUDYmVD4qWAIyXAI2ZAY+bBZCcCJKeDZSgEJahAJijAJumB56pD6CqEqKsAKStAaavBqixC6mzD6q0Eay1AK63AKu6AbG5BbK6CLO7DK69CrHAEbPBALXDALbEALfFA7jGB7nHCrvIDbzKEcDNAL7MFcHOAMLPAcPQBMXSCcfTD8jVFMvXAMzYAM3ZAM7aAc/bBdDcCdLdDdPeENTfE9XgFtfiANPlANnkANXmANvmBdboA9jpCtnrENvsE9ztFt7vAN3uGODwAOHyAOLzBOP0CeX1Deb2Eef3FOj4FywAAAAAuAu4C0AI/gAXCRxIsKDBgwgTKlzIsKHDhxAjSpxIsaLFixgzatzIsaPHjyBDihxJsqTJkyhTqlzJsqXLlzBjypxJsyZFR3wY9ekzaNAaP3bM1PlCpQ2XK1ukYJlSBMoQJ0Jk7Ijh4wUNFB5KbOCQQUMECxIaMECwwEABAgMEBAgAoC2AtQIGEChgYAECBg0kWIigIQOHDSU8oKDxwkeMHTKEOBkCpcgULFK2XOHShsqXOmbs+FnTcycjPo5sih5NurTp06hTq17NurXr17Bjy55Nu7bt27hz697Nu7fv38CDCx9OvLjxjI76rDHzRsqSGiEWuJ1Ovbr169iza9/Ovbv37+DD/osfT768+fPcF4SosUTKGzNr+oQ+Tr++/fv48+vfz7+///8ABijggAQWaOCBCCao4III8TFIHWEcYUID6FVo4YUYZqjhhhx26OGHIHrYgAlHhFHHIHwwqOKKLLbo4oswxijjjDTWaOONOOao444BJvJgE0REEOKQRBZp5JFIJqnkkkw22V0ERDRxYiI8VmnllVhmqeWWXHbp5ZdghinmmAsiwkYYPQjp5Jpstunmm3DGKeecdG4XQQ9hsIEImXz26eefgAYq6KCEFmrooYgy6MgaXCRRQZ2QRirppJRWaumlmHpYQRJcrDFfoqCGKuqopJZq6qmopqrqqh4l4kcY/jFkKuustNZq66245qorADGE4QeVrAYr7LDEFmvsscgmq+ywfXwxhAO7RivttNRWa+212DbpwBBf9LHst+CGK+645JZr7rnoGrRGGC9k6+678MYr77z01nveC2Gske6+/Pbr778AByzwwCs1y4O9CCes8MIMN+ywwjx0S/DEFFds8cUYZ6wxgm5w0cLDIIcs8sgkl2xytS1w4cbGLLfs8sswxywzxX1QscPJOOes88489+yzpTtQ4e3MRBdt9NFIJ620f4nUkcTPUEct9dRUV201k0nUAezSXHft9ddgh+21H1UUcPXZaKet9tpst31eAVX4IfbcdNdt9914kylG/hEGuO3334AHLvjghBtQhBh5J6744ow37vhqcThB+OSUV2755Ziz7UQcj3fu+eegh/51H1eEkPnpqKeu+uqsQx3CFUOLLvvstNduO6J8fNFu67z37vvvwAcv8gtfpHj78cgnr/zy9pGegfDQRy/99NRXP28GsDOv/fbcd+/9RnXEav345Jdv/vno6xpDHd+37/778M/NxxsipG///fjnr//+korwhvHxC6AAB0hAY7FBBvxLoAIXyMAGOnBJMmBDASdIwQpaEEdfIMEDN8jBDnrwgyC8EAm+cMESmvCEKMSNGU4Qwha68IUwjKEMsXMCM6TwhjjMoQ4t0gcpmG2G/kAMohCHSMQQFkAKsduhEpfIROa5YQpFjKIUp0jFKnJwCitroha3yEWk8eEKFLCiGMdIxjKacX8UuAIAu8jGNroxWWv4wRnnSMc62vGO5/uBvt7Ixz76EUx+IAIeB0nIQhrykNEjgtz+yMhGOjJAgzgCIidJyUpa8pKsO8IgHsnJTnqyNVx4FCZHScpSmvKUhKsAFz7Jyla6MiN9wAIqZ0nLWtrylmzDQhJfycteurEPUMSlMIdJzGIaE2pT2KUvl8lM9yXiCgg4pjSnSc1qWnNkCLjC1prJzW4uzg83u6Y4x0nOcpqzXjtYpDfXyU6XUUED54ynPOdJz3pSSwNU/minPvcpLi4owJ4ADahAB0rQTClglfxMqEILRYULFPShEI2oRCcapwvkc6EYzeiN/CA+inr0oyANqUiLFAN1avSkKM0PH8Iw0pa69KUwjSmGwrDGlNr0pq4ZxBBkytOe+vSnQOXOEDaJ06IaNSVrEGRQl8rUpjp1qUTY41GnStWF6OFgT82qVrfK1Z7yQA9VDStG+8CErpr1rGhNK0yZoEyxurWRXxClWudK17ra1aMVIOFb97rDPkDhroANrGAHK1EotJWviN2eHXZH2MY69rGQBegL7JDYyoauDiOIrGY3y9nOynME7LOsaL2GWc+a9rSoTa04QTva1mbMDiZQ/q1sZ0vb2h7TBJR1rW7H5Yad2va3wA2ucG05hCzu9rim4kI0h8vc5jr3uaNEAEKRS10yDeJp0M2udrfLXUQmgajVDe+NzKCC7pr3vOhNrx1VYEPxuvdAb3iAeudL3/raV4wPeMN790ufKwzgvgAOsIAHPMQBXIG/CKYNFw5A4AY7+MEQduEBppvgCsukDs+LsIY3zOEOOzADobWwiD+ih3B6+MQoTrGK8bcDsI74xQxxxBZWTOMa2/jG5dvCp2DMXzHQAMdADrKQhxw8GiCOx63lApGXzOQmO1l1FEYyThlRhSdb+cpYzjLhqsAIKfOzDErVspjHTOYyo40IZfDy/isH4QMzu/nNcI4z1HwAXjW3cRAfk7Oe98znPpOsBXW2Mwr7YAQ/G/rQiE60woxwWEG3DwyKjrSkJ01pd4HB0dqrAwEqzelOe/rTuCJAiDHduT6EGdSoTrWqVy0pIjSa1F17A6tnTeta2xpO+oX10fiA3Vv7+tfADnaRklBTXVdMDBkWtrKXzexmXygDRzZ2v77g7Gpb+9rYFo9epf2tK2T72+AOt7irc2Bus2rG4063utf97S2YG1ToZre8503varv73XxScr33ze9+MzvK+OaRGfxN8IIbXNjtDbiM3MCCgzv84RC3NQuMq3AEBTPiGM+4xlU9hYr/hw0C2LjI/kdO8k8LQIIeN84SSs7ylru80ktI+W7WQKGX2/zmOEd0A6Qqc9Z4O+dAD7rQ+1zunoum10NPutKX7uYkGL0lfagf06dO9aqPWQSvfvpF9CABq3v962C/sgRcrHWKiOG/YU+72tdO5AFEu+wIWcOm2U73utv9xgTgudEHEca7+/3vgE8xBQLNbUY0PPCIT7ziN8yCLpPat4uPvOQnT+AhIFnflM+85jdvX4BXdxA157zoR0968zaA8KKtculXz/rWZ7cKiRWD62dP+9oz9+1FLYLtd8/73tO2CCjtgwV8T/ziG9+zFsi6L6l9/OY7//mP3bYvdQ/96lv/+ncFPivb/oz97nv/+2f1ASMR8QHwm//86H/qB/bERTdIJ/3wj7/8e7oAit9wECGfv/73z/+RCgD1BdQH79d/BFiABhhRC6B83MMHyXaADviAEGhPGVBs29NREXiBGJiB5RQD2nNxGviBIBiC09RxtVMHIniCKJiCxDRqjoMI0KKCMBiDMmhKDsB+iUN9M5iDOriDk6R9c7MGPBiEQjiEg6R3SQN5RJiESriEVmR5RjMITBiFUjiFUQSAGBNvVJiFWriFLXRvGKNBXBiGYjiGD0QCE6MHZJiGariG/EN2+8J8bBiHcjiH5CN94yJLdJiHeriHwoMF4YJ0fBiIgjiIp+N0x1ID/oSYiN4RBaAwC8LwDNygDvbwD5RYiZZ4iZiYiZq4iZzYiZ74iaAYiqBoD+rADc8gDLMAClGgiGpYA8LCQqyohJiQC9AwDvggiriYi7q4i7zYi774i8AIjPgwDtCQC5gQiw94AqhiYshIgJsQDNwwicE4jdRYjdZ4jdiYjdoIjPbADcGwCc1ofDsgKnIUjs7XCcVgDtu4juzYju74jvAYj/FoDsXQCeYoeT9gKE1wj6MXC9hwi/IYkAI5kARZkAZ5kLyID9gQC/zodU0AKHDYkGx3CtMAkAh5kRiZkRq5kRyZkfgwDacgkS1nh14ChSKZdKEQDRbZkSzZki75kjAZ/pPviA/REAonSXBWWCUocJMjlwvjIJNAGZRCOZREWZTUOA65wJPghgJZgoVKWW/B0A5GOZVUWZVWeZVYuYntEAxPCWxeiCNl0JXhhgPFQA9ZeZZomZZquZZTSQ/FgANi+WlpViOAGJe3dgnRwJZ6uZd82Zd+KZPRcAl2aWiG+CJAOJiqZgvo8JeM2ZiO+ZiQiZHoYAuIaWZGmCDlWJmKVgrcEJme+ZmgGZqiCY/cUAqa2WT5mCB9cJp7FgvqOJqwGZuyOZu0GYzmwJCsWWMKiB+Yl5tY9gjSUJvCOZzEWZzG+YnS8Ai+uWGepx/ct5xDlgnYcJzUWZ3WeZ3ViQ2Z/gCdASZ++4EI3GljxLCS2Fme5nme6Cmb+EAM4ZleNkgfbNCeHDYHeZme9nmf+JmfsBkNcyCfz4VyxdGb/glgxrAP+nmgCJqgCgqZ+2AMA/pbzbkbHvig5yUK4LCgGJqhGrqhfQkOokChp0WCvZGZIApdqvCTHJqiKrqiLJqV46AKJQpZqZkbWBWjwWUJ29CiOrqjPNqjRbkNlmCjgMUDt1FoQjpbvXAPPrqkTNqkTtqS99ALR5pWRjAbKzelnmUMT7qlXNqlXoqQDoqlWRVzriEFYgpZweAPX7qmbNqmbtqO/sCVZwpUUrAaETmndUUK6/CmfNqnfvqn07gOpICn/jFFkjZhkoSaVsQAqIzaqI76qKLInokaUjn5EqE3qVn1DJC6qZzaqZ5aic+AqRLVADaBhKIKVMvwqaq6qqz6qMtwqgPlhDAxcLDaU7mgpq2aq7q6q33qD0lZq/OUcCxxqcAqUp3Jq8iarMraptxQrOVEqivhlM4qUaFglst6rdiarVxKDzY5rdT0lSTBCN4qUa3AD9p6ruiarkzKD60wrsbkeCNhpu4qUKIgjep6r/iaryxqDx86r7ZUpyHhCHPnr/MkDvp6sAibsBwqDgSLSgSwYxtxpw0rTr+gsBZ7sRiroL8wsaNkqBZxahxLTReasSRbsiabnuAQspREBBrB/gcqO015AA8nO7M0W7PWCQ958LKFRIEQEZ86O0yPYK02O7REW7S0SQ/K+bN1BKASIa1Ke0rqYLRSO7VUK5rq8LRnBK4OYaRYa0rBWbVgG7Zi25jS0LViVKUQsZNmi0mmMLZu+7Zwq5emsLZSxJQOIVd0i0j1Gbd827d+S5XRkLdDVAENwQCCe0hR+7eKu7iMK5NXe7gyxAALYbiQe0dRoKSNm7mau7kaeQ+rWLktpBAOBbpzhAFCy7mom7qqK4/0gAGk60EJcXivS0avubq2e7u4q43mMLsPhBB1ybtRlAy5O7zEW7zBmAzAq0AHwVLJK0WSYLzQG73SK4qS0Lz5/mMQfmC9RYQM09u93vu9logM2ps+BeGy4xtE5wC+6ru+0nsO51s+BYFA7xtD9sq+9nu/uGsP81s9BGGC+9tCQGCg+DvABLy6+wAE/ws9BIF2CexBp1vAEBzBjUsPDQw8AyGvFbxBIyvBHNzBipuyGdw6AmG+IdxAveDBKJzCfSulJZw6AoHBLZxA86DCNFzDYjsPMXw6ApF/Oaw/tmDDQBzEU0uZPVw5i+C/RYw/1iDETNzENWsNSTw5iwCyUWw+6evEjNsO4BANw5ALquAJkpAGOZAACZADaSAJnqAKuTAM0QAOUonFi+u+VRw4JDzH5vPGcFyz0gCOdbIJX5vH/jTbDnb8N3YwyOZTu4CMsMzgAtPiAsyQyAq7u4bMNsw7ydUzDZCsru0wt/ZiCnicydo6DZasNkIwytTzCqCMrc06Mseaysr6CqZ8Nh4Qy9Ijs668q/bgBTrjBfV7y6wKD7RsNS8YzMDzw77cqtAANdBwzK1KxMQcNQz8zL3Tyszsqa4gNa5Qzaq6ytL8M2zRzb0zw9rsqTkbNXkwzp6Kw+DsM8u1zqyDq+i8qfobNb0cz43qD+7cMxyQz6zTD/bcqerMM+L8z5DaD/y8M4h40KkjDwT9qZxMMm3b0J0qDwqdMxNa0ZYznRKtquKQBgyTBga70Z+KDRh9MhJb0pOT/s0inav8UAzvUgzmutKtes0oTTKrWdOXkw4yfa3c8NCXYgrUvNO8mg44TTKLUF5FTTmkINQIew/TMAtEMgvTgLlMna+DmtQhswiVjNWDw71V/dVgXZ7iy9Ugswg3TdaDow1hvdZsPZzagNZlvQg2ANeDs8Ftfdd4HZkgTNcNIxCHydeAo9F5PdiEvZckDdh9LRDMiNhtUwyF/diQjZUuzdgMMxCIStltwwmRvdmcHZScgNmVPRBlBdpuY9edfdqofZB7TdoJUxA/xNprAwqpPdu0LY+gANsLUxCFjNts49W1/dvATY1jzdutXRB4SNxqE9TBvdzM7YncjNwIcxA//gbdaoOizX3d2E2J40DduW0QjsDda6Pc2T3eqP3c4G0vCOEG5602qUre7s3Zr7reCpMQsiffaBPR753feO3T9o3eCREH/Z024aDfBF7V4RDgoZ0QtIrgVyMKBf7gEt2vDD7fC+GzE341iwrhGn7MknrhCsO0CfHXHm41f7zhJo7FZTviC3OZCHHWKk7iJx7jNpziL64wu0kQA1jjVePYMt7jEDzZOp4wC1ARFhjkVFMKPp7k6muaRq4wHGgRTtvkUmPaSl7lq7vaUo4wWjsRIp7lVbPUVh7mmnvVXq4wLE4RDVjmVRMMYt7mcCunaq4wGfARWx3nViO8bp7nRIu8/nbOMGEQEuDZ52mT4Xpe6Bbb4YK+MO8JEjiY6GeDyoYe6egKy47eMD5IEi5e6WgT0pLe6azKsJr+MDe+EfsY6mszC56e6o4K1ab+MA/ZEl3X6mxzDKpe6156DLIeMhIQExae62zT3rYe7Csa374eMiD+EqNd7G4jDMLe7AcqDMpOMkwwGiUQ7YBDCg/s7NounPRA5tYuMiVgGoH+7YED7Nt+7p5J7OReMotOGvW97oITBVSO7vSeleDwufB+MriHGkic74MTCPNe7wL/kuAQCP6+MyzIGm1w8JeDyQP/8BcpygzfM21QGwI68ZRjC1QN8RyPjffgzBjfMxEKGxcf/vKWowwdn/K6qAwmPzUjPxsn3fKYY+4q3/HqLvNS47G5kb04zzvBQJ41r+r4AOc9bzUmFRyZXvStowniHfRJzg2aoPRrM+q6sc9SLzyrYN1Or9/jsApX7zYcsB9/9fXTAwpNv/WczQ23TfaAAwX/0e9sXz3CUM9oX9X2AO1xPzkJ3x98kON5Xz7I4M91j879MNx/XzkLwLMActGHjz698MmDH8TtwMKNjzoiqiCXXfn7AwLLAM+Rz77+sAwgoPm9U6kHMvak/0DCsPGfj7r3gPepHzxuPyNJH/scZAkO3/phOw1BavvVQ/ULUue+/0LGAPS6f6/4EKbDfz5/biVg/rj8RNQIz+D5x9+p/vAMjQD9+2OGW5L52l9FsqD11d+k4yAL379Bpl8lVHD+eLQJuT/+9zkNfMz+IXRRfNLo9H9IaWAM2Q7/jUkPAGEsDQCCBQ0eRJhQ4UKGDR0+hBhR4kSKFS1exJhR40aOHT1+BBlS5EiSJU2eRJlS5UqWLV2+hBmTYZFFNW3exJlT506ePX3+BBpU6FCiO3fIRJpU6VKmTZ0+hRpV6lSqVa1exZpV68dc4/59BRtW7FiyZc2eRZtW7Vq2bd2+hRtX7ly6de3exZtX716+Ycfl2hpY8GDChQ0fRpxY8WLGjR1z3FFU8mTKlS1fnizi8WbOnT1//gYdWvRo0qVNl8S0jF5f1q1dv4YdW/Zs2rVtt6W3DNNp3r19/wYeXPhw4sWZisCcXPly5s13cjAeXfp06tWtX8eefXQkYutufwcfXvx48uXJryMWSft69u3dv4cfX35oDs7t38efP+iI+f39/wcwQAEHJLCpP34RxzwFF2SwQQcfFEucX/4osEILL8QwQw03/GwE/T4EMcT8UuCwRBNPRDFFFVckbBNivIIwRhlnpDG2cYjZhEUdd+SxRx9/vDAFEYckskjMiAAySSWXZLJJJzVcRZlx/KmxSiuvvMufcZRZ5UkvvwQzTDHHvIoII89EM02hpiCzTTffhDNOOQsL/uWXadDhB0s991SLH3Sm+SWUOQcltFBDDyV0CjUXZbRRnL5ANFJJJ6W0Uks7IgOUWH5ZBhtx2sGHz+/waUccbJb5JRZQyLi0VVdfhTXWFL9wtFZbGR1EVl135bVXX38FNlhhhyW2WAIHuTVZZdWMwVhnn4U2WmmnpbZaa6/FdtAYluW2WzTfyDZcccclt1xzz0U3XXXXBekNb9+Ft0hGLGC3XnvvxTdfffflt19/47OAkXgHJnjIMP5FOGGFF2a4YYcfhtjhMAqmuOIQ+dAgYo035rhjjz8GOWSRTdSAD4tPRvlDSEdmuWWXX4Y5ZplnphklWlPGOef8kqi5Z59//gY6aKGHJlraJHRGOmn8EKGgaKefhjpqqaemuur+KEBEaa23ts8Pq78GO2yxxya7bLNV8oNrtdd2Dtyz34Y7brnnprtuj91lO2+9mdvCbr//BjxwwQcnvNIt9kY8ceawKLxxxx+HPHLJJ18PC8Uvx3w5xinnvHPPPwc9dNFfsjxz009Pru/RV2e9dddfhz3ww1GnvXbMqIg9d91357133zmmwnbhh8fM69+PRz555Zdnnte0iYc+essQga5566/HPnvtt9+Qg6ylBz98y6Dgvnzzz0c/ffU7g0J899+/zIz156e/fvvvx/8jM+Dnv3/LCnlB/gQ4QAIW0IDKe0Eh/vy3QAZaZmUHhGAEJThBCsrtZg3EYAYrc5QKdtCDHwRhCD8WGQ2W0ISWEYMIVbhCFrbQhdUSwwllOMPLXOGFN8RhDnW4wzZdgYY/BCJmfsBDIhbRiEdEYn9+EEQmNhEzfDBBEqU4RSpW0YqNMYHJnLhFLl6mD/y5YhjFOEYylpEkI+hDF9W4xuSU4QNmhGMc5TjHK36gDGzEYx6V04cN0NGPfwRkICG4gTTq0ZCHVA4jAihIRjbSkY/03QsEhkhKVpI5Q4BkJjW5SU4CbgiWBGUo7WPDTpbSlKdEpc98KEpWttI+YkBAKmU5S1rWcl8IiKErdblL/AzRlr8EZjCF/hmsJfLSmMfUDx6GuUxmNtOZZMIDMqU5zRBh8pnXxGY2tUmgT1LTm98U0RoqsE1yltOc5+xNBdYATna2s0huQ2c85TlPelIFb+7EZz6NtLl69tOf/wSoRkqnT4IWFE2FsGZAFbpQhsZzCAo0aEQluig+CKGhF8VoRlMpBC1O1KMfbRQffKlRkpbUpGH8QUdBulKW2ooJJ4VpTGUaQia01KY39RYpZ7pTnva0fKvEaVCF+i470MunR0VqUkdnATsM1alPLRgjeKZUqlbVqnJLwiShulWuVuyBVwVrWMXaswt21axnRRkfEjpWtrbVrQgbgkrROle65swPYHxrXvW6/ldqjeB5dQVsYLkGT74W1rCHpdQ9BbtYxuZNdYiFbGQlq6TZNdayl71cEya7Wc52VkBNwGxoRVs7KXjWtKdFbXCkMFrWthZ6XEhtbGU7W8JwwbW3xa34zFA92vbWt79FCQf2l1viFpd/fZgqcJW7XOYqJAmFNG50pdvANgygudfF7mYH0Ibpdte7M+zDSLM7XvIm9QfQ/W561QtEM3igvO+Fr0I9MNz11te+aqRCA+K7X/4uswHBu2+ABYxILli3vwdGsCAHYNsBN9jBrOTCARI8YQof8QAMfnCGNWzML2Sgwh8GsQQzUNYNl9jE1FxDDUK8YhZrrwbrPHGMZUxQ/j6UtsU3xvHopCDXGffYxxL1wwxyPGQi020Gf/1xkpUc1DY8oMhPhrLQHsDdJVfZymetcZS1vGWN7fjKXwYzY/mgWS6X2czmagKPw7xmNl82EQc7c5zl3KswJKLNd8bzdL/wxjn32c9t+gCJ8zxoQqt3EEb4c6IVjSIjIKvQj4Z0iakQgUVX2tLriQCAI71pTid5zJcGdahFk+ZOl9rUd+5DEUS9alZXpQjoPXWsZQ1pRvCz1bfGNUiwoNVZ99rXv+YCA3I9bGIThAEY/nWylb1snoiBg8WGNpd3kEtmV9va1xbKG4wabW7v1wKKxXa4xT3uovDhsd1Gt2m3oGZy/rfb3e+eDB/gnG56XzUM7IZ3vvW97+R8gbf1BjhAOSBofhfc4AfPzyCOEHCGL/MIjkZ4xCU+cTSZIYoNx/gfTUBfinfc4x+vVR1IkHGS65AEdQB5ylW+8nj54dklh7n9doBkltfc5jenGCPOHXOe724LvMZ50IU+dKQNYq09R3rghgBxojfd6U/fm8KTPvWoPRzqV8d61oXHiDDEkupfjxgCwgB0rZfd7GcH3xrEC3a2Z+sHMEZ73OU+9xKKIbltx/ulkkBtuvfd7393Yh+kUIC8F35JBZACrAG/eMY3/pBqN3zk//N2x1fe8pen5iCqIHnOm6YKTMd86EU/eoI6/uILMOh86qUCgy84gvSvh33sn1qIL9BA9bfPCA2+AFHZ9973v2fsGlSNe7YXAe7AR37ylR9d4ROf1cZffvSlP/0S074Fzv9wC3ZPfe533/ttjsPdsR/ZJMTh++dHf/p/7Yg62GD8JrVBHVyvfvrX3/4F78MVNPP+WorgCoq/vwAUwAEMOjM4Ov4roiHgOAJkwAZ0wMobhC1QAQRUHxXYAtB7wAzUwA30Pj6oA/GjwMJJgjrANw40wRNEwRRchEG4Ah0IQZrRgSvAQBWkwRq0wRtcjkHggpd7QWvZAS6YQRwUwiEkwiK0FT/YAtvrQTChgS2gOSOEwiiUwinMG0So/oMi6IAlnI4OKII6+B4qBMMwFMMxNCFEMIMmWAEtjIkVaAIz+EIyhMM4lMM5nCY+8IMrEIJxwrsKEIIr8IMSpMNAFMRBJETAGoQ6aIIdcIAEc4AdaII6CMJClMRJpMRKXDM+WIMvaAIe6CN52gAeaIIvWANAtMRSNMVTREWo44NBYAMqaIIfWIFt0x4LWIEfaAIqYINBIMVU5MVe9MVflMNCQIQyEAMz+IIraAIosIEX2AD9qpYG2IAXsAEoaIIr+AIzEIMyQATeA8Zu9MZvBMcUTAQ38IMv2IIhiEUCosUh2IIv8AM3sLNwlMd5pMd6VDJGyMQmIAIPa6gMIIJQ/lwDsrPHgSTIgjTIH3KEQfgCLDiBBbixBTgBLPiCQZi/g7TIi8TIjEwON6iDKVBC1aOBKagDN9DIkjTJk6RBM8SCj1RDpaABLHBDlJTJmaTJoLPDLViklrSOF3DCXazJnwTKoGywPviCI1hEnQwTBziCLwBAoXTKp4RKg1qDJETKbGnC44vKrNTKrXwfFszJqnSZF5BBriTLsjRLRkkEM1gChwRLwVmAJTCDeDzLuaRLp+yDN2iWttSeGHiDpqzLvwRMMoxAvNJLFxqBCwzMxFTM9IuDAyxMRxoC81vMyaTMq+uDM8jCx6ynDjgDv6zMzwRNU+ODN7g4zRQrE3gD/p8MzdVkTe9CBC4IAdNsrhDggjdszdvEza3yg7WTzSL7gSfMzeAUTlASg4XrzW47Ar4bzuVkzvBJBCpAgePsPBSgArlszuvETor5gtKUTs00AYLLzvAUz8sYBDbpzvPkiCmIxPFkT9YchOFDz/hUiiJYz/a0z5nkAy7gM/nkz8P4AC5QzfsUUEp0A1vrzwP1DSwgyQFlUCrsAzJD0AiVjybwzAa10O+rAxaQ0A1VERZAuQsFUdHjgytwMg41UTF5gCsI0BBlUYobUQg40RhtFQhQ0Ra10XczgzSU0R2FlhVYwBsFUjwztwDg0SJllwBYtyBVUg3rg5cy0ieNGCao/tAlpdLAYgQIhdIsnZkmEMgq9VKQ+oJO1NIxrZoNAM8vRdNW6gPzJNM2/ZspmNI0ldMSWgOLctM7BR0hwMo55VPi0QM7xdNA/R0h0IM+NVSuaVJBVVT1kdJDdVRl6bBFldQIGrFHtVT7SNRJ1dQbatRL9dScWIMe2NRRvaIe2NNPvdE1QBJSZdVAIoJTRdXmNLpWpVVZWrpY/cw3q9VdxaY6w9Ws9IOv5NVhlacXAM5fHcgrIABiZdaSIgCgQtZURAQ2bdZqTaopsM1oFcM+2Dxr9da9qoI41dYHnNZvNdfTwtZxHUCdOtd2VS5oVVfkiwMNddd65S8WkMx4dbxa/rPXfsWxXdNXrfODE/DXgjWzEzjWgJ24L8gYg3XYStOAM1XYcOMCwnvYix22AkC2iZ21AsPYj2W4BeNYQqMCCQDZk506CdC0kZ0xO4hOlIVZyUOBpmLZ++qDJYjZnEXAJRDXml2sLyhRnRXalnwAifXZrUIEnB3apT3OJcjWo10pP9g/pqXaAxWBhIVab/oCCavaruXRAzDarK0kdvXasm1TeBXbNSJbs2XbSUXbtC0hwmrbuR1WcIPb8DEDk6XbvXVXCfjRu72cQXBBviVcjNWB+gTclMHSwmXcnAWtxK0YP9jPxqVcr/0ArIVcNFncyuVcvn3czBWRMhDWziXd/s59gTsCXeUwA64t3dZ13YQ4gL9N3Z2Arde13dt9iI3N3J3D3d71XYeorKPl3d8l3uKFiODV1rU13uVl3ol42z79quaV3unFiLBl0TWgNOrV3u3liAiAVQHlA1Hl3vEl34/ogRVtzdot3/Vl35DQ3dbsg5dt3/mlX5FAgZ4tS/Wt3/3lX5J4363kAxno3wEmYJSQAfS9yDUQtgJm4AZGCQb4XouMXgem4Ao+Cev1xuG14A3mYJNAXmB00g4W4RFmiZpCRfgk4RRWYZagCUKk1hWG4RhmCUUZw3mT4RvGYZeYmCKsgxz24R+WiQ9FwUGAUSA24iOGCQhAXPUDVCR2/uInfgkhsL8JhuIqtuKWwODYYwT3uuIu9uKY8IAuJT25/eIyNmOXsNvKcwQfOOM2dmOZ8IGK/DvjeeM6tuOYwNyns+E75uM+1mGsa2I/FuRBbgkpxjk+4GJCVuRFdgkPQOB26wO9ZeRJpuSWkAD8xbZBMLBK5uROZokBWOJlK4Nl9eRSNmWWIADUtbY+OMpTduVXVgkHwORBK4SRg+VbxmWVIAFu3DQnyOVfBmaVcIJHU95gNuZjFonnXbI1QOZmdmaUiOATY+NnpuZqJgkfmDEytuZt5maPSOP74oN/6+ZxJueO4IBHZi1tLud1ZueM+Gbi4s52lud5zggTKK4U/qLnfNbnjVDOy9LgfQbogI6IDwYsFRPog0boiqiBuuKDIk7oh4boiIAAdC6oXInoi8boiAhlg6LjjJ6lP7gEUEiFWMiFXxAGY1iGaJgGbOAGcBAHc0gHdmgHeaCHe7AHfMCHfeCHfvCHnv6KnvaHfuCHfcBpe7gHepCHdmCHdDAHcQAHbsCGaYiGZTAGYfiFXIiFVACFS6AQjzajPM4n+fFqCqKEWCgGbEiHfRCVtbaNfUgHbCiGWKCEsc4e2XUnsaZr5MmEXrAGdmDrvwZs2mAHa+iFTMjryLHraerow3YcILCFaZCHwJbsyabss5CHabAFIGBssAFrVrLozSYb/hDIBW1Q68o27dNGbdrYB23IBRAAbZnZ6EPig6Z57aDJBXBI7dzW7d3eE3AAjNpuGAqg6CbiQeDmmFjQBt5W7uVmbubWhlgwbnYhoUra4+jml1sIh+bW7u3m7u5Wi3C4Beuulh3OI2YW73Q5BWzw7vVm7/Z277jAhlM471+JZhpiyfmGljRAhnt47/727/8GcLq4B2QYCPyeFBpwInU2cFnJBXQI8AeH8AiX8LtAh99e8Dd55wYqhFa+8Eppheye8BAX8REn8bsIh1bocCdxAF5mIP1NcTmZhXMo8Rmn8Rq38bs4h1l48R35X/chzB33Ei9ghn648SI38iNHcrro/gdm8AIg1xAPgR82cPIlKYZQSfIrx/Is13K4wIdimHIBYYPw6dYvTxFNUO8tR/M0V/M1bwts0AQyd48qgJ4LgPMMCYRoYPM81/M95/O0iIZAqHPquIDa+exA/49XkPE+V/RFZ/RGD4tzeAVDF47YThoqlvTsiAUHd/RN5/RO33R0gO5LJ40szpl/FnXikIRp8PRVZ/VW9/RpkIRT5wyCVhrykXXiUAUYcfVd5/Ve5/RxUIVbT4z22RpEE3beIAUQ9/VlZ/Zm5/RwIIVjDwwjSBoekHbRWAZn1/Zt53ZPX4ZrrwoewBneBPfE4ATc7vZ0V/d133Rw4IRyb4piopgX/ob3wQAFXWf3fNf3fV/0cQCFeo8JGo6XYgZ4qlCCM+f3hFf4hVd0bFCCglcJZa6VOIB4q8gFK2f4jNf4jddzfLDwig+JfL0VRAB5qMh2jkf5lFf5PP/2ku+Ip1WT+3b5l3iGlbf5m8d5NX+Gmb8IBG+U6uZ5lCCGnCf6ojd6LSeGoI8I8j4TN1B6lAAFeDj6qaf6qj9yePj3p1eIBS2S4tZ6jhh6qxf7sSf7Gk/6ryeI6Q4RKUd7jlD1sof7uJd7EZ+Grw9zEInntp+It5/7vvf7vw/wuud5e86Pxdb7hzAGwFf8xWf8/jYGl+9syQDBw08IUijtxsf8zNd87d6H/mgv+KNhDkagfIbA8803/dNHfd6OBoAX46Kw9MPX9NSX/dmnfcpGh3IndZ4gd7SPhNWo/d8H/uBfa3pQD2GX98nIXr1Pg3YQ/uZ3/ue3knYocFGPgMnog8NHd+jX/u3n/gYBh1PHZMPn+WDo/vI3//Mnj2CQ9Mjv4adnfvSH//iXf9loh0AX4p5QcIB/hfnn//73/74AiFcABhIsaPAgwoQKFzJs6PAhxIgSJ1KsaPEixowaN3Ls6PEjyJAiR5IsafIkypQqV7KU+GYRzJgyF3FpafMmzpw6d/Ls6fMn0KBChxItarTlsH9KlzJt6vQp1KhSp1KtavUq1qxat3Lt/ur1K9iwYseSLWv2LNq0ateybev2Ldy4cufSrftv2NG8evfy7ev3L+DAggcTLjxw5sw3hhczbuz4MeTIkidTrqzwmN3Mmjdz7uz5M+jQokeTLm36NOrUp49Zbu36NezYsmfTri0Sccw6tnfz7u37N/Dgwvv+Um38OPLkypczb+78OfTo0k//Gm79Ovbs2rdzD4x7kZju4seTL2/+PHqSoqazb+/+Pfz48ufTr2/fs6j0+vfz7+//P2C4IQIggQUaeCCCCfJkzn0NOvgghBFKOCGFFVpYlTkKarghhx16uB1uF3w4IoklmniicLNcuCKLLbr4IowxyjhjVLOgeCOO/jnquONJiA3BI5BBCjkkkSJtQyOSSSq5JJNNOvlkWtsUOSWVVVoJ4Ey6Xbkll116maA8UIo5JpllmnkmmvHJ8yWbbbr5JmMy8QEnnXXaeedkOOyTJp99+vknoIEKCtY+OOB5KKKJKqqRTEks+iikkUo6Ej6DWnoppplquimM+Ez6KaihdhmTH6Kaeiqqj67DKautuvoqrLGitk6qtdp6K4IxwYArr736quMzsgo7LLHFGntsVs/8uiyzzfYGUxzOSjstteZ1giy22Wq7LbeCdlItuOGK2xdMJ4x7LrrpVoZNt+26+y688V6Ijbr12nvvSIsMgi+//foL1J7yCjww/sEFG3zcPv8qvDDDACzSRMMRSzyxRaYcfDHGGWu88VqmUPwxyMwukkHIJZss8S0cq9wtOL0A0RIQvYCzMs3Z3nIyzjlLWobOPfs8ri01C63pPshMQNgEyAQ8NNOC2vIz1FF/+YXUVVtd63pNa20ma7FhtjXYYuZ3Ndll41iE2WmrfWilYbs94z6uCOfK0m/b3aKna+u9t4E+8P034FROczfhFkrZ3ZGFKx7hNIE7/nh3JEM+OeUfSrI45vc1ft7gmXsunySViz46bQuQfjrq/CnzOevtjcPfOK3LHp0yqdt+O+656/5oOrP73lwO/OXwO/HJpbM78skXRYDyzTvv/lrbxUuPWi/89TI99qbl/Tz33adkgffhiy9Y9uWTdo5+55i/Pmjju/9+RijAPz/9P0XPPv6bVTdecfn7n9n26ifAARLECQQ8IAJLwqD/MTAzucBOLhooQbpkKIEWdN8VLqjBDVqkGBP8YF3AUQnbVGJmIDwhXIrBwRU2LzwsfCEMDaIFFNKwLtMI3WMk0bka8vAtWoghEFO3iCAScYXL6CESM2MPZURiKJFQhj2SKMW5LKOIVqTcIhx1xS0SEB5T/CIYwzgoeHCxjH9bhBnMqMb3PUKMbnwjHKH0iDXSsWwwkUAd8/g8UsSxj37844pIocdBQg0mGSQkInOXNUAy/rKRjnzP2BIpyZLBxBGTvOTpAvHITXKyk8cJBCZDObGYHFKUpnTcqjypylWysi60OiUs/yWTCsSylnojRitzqctdkoUYtvylvWRiB2ASk2z34yUyk6lMpgSwmM6s1kyg8Mxp+iyCy7wmNlv5QGpy01mIgUA3w1myHWaznObs4+bEqU5eIWZf63xnxMJxznnSU4rhgCc+a4UbquWzn/2SZz0DKlAG3tOfBgXVd7Bw0IWqyxoDfShEpWcNhlIUUt9ZhBAqqlFw9S+iHv1o4fa30ZHe6aKLeAFJU8osIBwTpC59Kcfw8TKV0vRNJl1ECmqqU1wZA6Y+/WnBjLHToX7p/qaLkB9Rk2qq3gG1qU5F1vGUKtUqocCoi/DbVLMaqUbU7ale/Sqm9tEIrZJVSD6wKky0WNa1HmoTYH0rXPu0CbbSNUdJQGtMIFbXvdJJEl2NK2ADG6N94JCvhh1RE/AqEy0dtrFfUp9gIyvZCaHPsZblUB0UOxM3XLazW+rpZEMr2vcI1bOmPZAbNIubEZy2tUSKQphGK9vZGkceUXAtbv0zAtVeVK+5/a2Ogkbb4RKXM08DLnLRk1jeXlQPyX3ujUBb3OlSFy2lhS52xaMH5hrVBNn97oiQUd3xkjcryAAverVjAu6ilbHpfW+Crlfe+c63evC9r3Ayy168dgC//v41UCbqQd8Bj7YemfgvgnvTgf2qNo0JfrB/mEHgCYOVGRC+cG3MwGDm7gDDHk5PFCBL4RFD9By3/TCKXbODDbO3Dyl+cXk4MQ8S0xib8+AEjHNcmT6wmME10TGQt6OJdtS4yJ5shyaCrGTIcKHHPSbCkqOMHW4Yucpv5IaUs8wYIji5y4tAgJbDHJyOWrnMHxSpmNMMGAR4uc3uVDOcecMuM9MZe/SKM57/Mog28xmNef5zbQIB0DoTunDhACWgE60XDfe50fxUNKRfowQqF7rSNOOGEiKtaaN8odGejsmPNy1qy0jX0qZ+13VHrWqgNPnTroZJqFct68hkYtCn/r41rMJx4Fnz2ietfjWwF0GFXhM7MqwgMq6T/ad2sKLYzuYJFYIt7Zg4+NnWZowpFqjsbSfJHB67Nrhxwuhpk3sRzg03ug2Dg2hwu90Tioah0i3vlmy33PaGCR8EMO99E8YU4nA3wKUjjm/zu+ApEQAf7q1wmbTA4A4XTCr+HfCJi0YcqXg4xlPSgoVzfCZhyDjIAfMHaVC85G2Rxh9CrvKThKHjLp/Jm1cuc75E3OQ2v4rFZ65zk+z55T6fiQ52LvS+kMKEN3c3OAQ59KWPRAc/f/o+mS71vhSjpUcfMT5UOPWtj6TTUP/6arku9r1gQBn9uPpw+6EMDIy97SLZ/i3Y4/6dR7u97nmZBTrQ3lR02MjufheJ1+Uu+O+g9O+G30su1KF3bKpjm4d/fEheMPjJ33QNkL98XxoBjcX/ERpjxTzoR7IGypPeqB8PPer9Uox7cP5/99B66mNPkpaXvvZWNZfsc/8XLyAjiq2/mz2Q4QXdE/8kJ7A98vHKiAIUv/mD4QQ5fw+vaeDY+dZPSQEYkfztK9by1//+YlpBaelfihutAD/6bzJ67rNfs3hIP/wjMwujk79F4Oh7/POvEzy0v//MHbb+BaBliEI0+F79JYc9REMkCSAD/kS0+R8EcpdiNCAF0gYoMAOyHWBZtAMzgEIFfuBevEQEjuB+/tEdCJ7gbyjCL9BfyYHDLygCCsZgYQQeCdbgflWbDOYgeaTCMuTdbKHDMlycDg6hZYybDR7hhnkfES6hgmACL0xDKjnSOkwDL2ACE17hcKwfEm6hk/EBOGEhGFoJJ9jCMWyDOlidvOCDOmzDMdhC9YUhHBYIBCQcF9Yhn0FZHOahHu5hnHGZHf6hp8UaHw4iIRbig/0aICaip8WcITaiIz4ibvWcIk4isKkVJF4iJmbiVN0VJXYiuQ2TJoaiKI7iQdmBJ56iwvUAKa4iK7ZiLfUAKsZixymhK9aiLd7iFWmhLO5ix0kBLv4iMAajAEkBLxbj19GAMCajMi6j7dCA/jE+o9wxIjNOIzVWY9VIIjRmo9y5lzV2ozd+o8LolzaOI+mVEjieIzqmI7NcATm24/b5ljrGozzOo6IslzveI/spFD3uIz/2I5VgAT4G5AjCoz8WpEEeZILYo0AuJAmaI0I+JERGpHawI0NWJBdyo0RmpEZuZGWIo0V+pB0OwgBwJEmWpEnyxQBgI0iupCLGwEm+JEzG5ErEAEvW5C46pEzmpE7upENQpE3+ZDEOgunwJFEWJUwugEoCpVI+IxMYpVM+pUEywVJOZUAOAphBJVZmJTUiQFJSpVfi4+lppViOJSnS3lee5UoWgkuSJVu2pR7GQCGgpVwupR4MpVve/iVeVuAC1Ntc9uVXYmReBqZg5p5H+qVhzqUgDqZiLmbbIeJhPiZkbgFjTiZlytwWQCZmZuZ3SGZldqZnWttlaqZojuZ3JOZnniZqwpljkiZrtmaWpCZsxqaOFaZr1qZtIsYaOIBs7iZvopcD6OJtBqdwfgcf4GFvHidyOhYR0OFwNqdzGpVpJqd0TqdKreZzXid2mtQg9Bd1dqd34lMHdGV2jid53lRYfid6pucpmWV5tqd7alYfFJ56zid9ctEL8Nh75qd+chcO1qd//icBGeF+DiiBctd5AiiCJujusGeBNqiDMlgVKKiETqjjVMGDXiiGehkfWCKFdqiHnkwS/jBnho4oiXYZHxjBh6aoivKLEYhoib4ojLZZISzBitaojf7KEsRljO4oj76aL94okAapohBjjxapkU6bCQqpki4pkdDgkT4plE7bICAjk1aplXYIDYhnlG4pl04bQV4pmIapeChkl5apmc6iCoipmq6pbagAcJ4pnMapz+Ekm9apnQaGT8qpnu5p3DHCj9wpoAaqTwyB9vGpoR4q6Q1C0AkqozbqR+iAliKqpE7q4IlBmjoqpmYqQqiAGFCqp36q//nBpWoqqYqpCvgBqKaqqtbgGshnqb6qh77Am64qrdYqCfYBh8KqrlJnEuCnrf4qsALige4qsVYmgwYrsibr/iSywagWq7NqpQqwgbJOK7UWIx986bNmK0c2gYtWq7d+qzGuwVpqK7nSYwzMKrimq7qOYx1oQLm+qzJqAG2uK73W60JygQHAq75iogFYp73+K8CuJBeM5L4W7BIOgL8GrMIurFK+wRcaLMSmHwSIIMNWrMUephnkVMRu7OWlgIBeLMiGbGa6wRFwrMkO3RGklsiuLMsKJxVQwMnGbLhRwAO2rM3ebHb2AdrILM8mWhH4Ks4GrdDm5xrUQM8eLYzVALoOLdM2LYHGwa4grdRiFwzEgdNeLdYWqR1419R27V6ZgClmrdiObZfqgQ14LdqSlA3wJdm2rdvq6bWmrdxS/hO3vq3d3q2qQu3c7q0eVS3e/i3gKqsj0CnfFi4BXYEjBK7iLi69IsIUGC7kNs8UIALjVq7lXmwfNGXkbi7fMAHQXi7ohq7N8gFncq7pgswWdKvori7rYm0dhMDpxm64hMC8tq7t3u7fZq7s7i6oeC7u/i7wAq8YGCfvFm+VEEGnBq/yLi/zfocd4J7xRu+GnEDYNq/1Xi/2WtUa8ID0dm938MDSZq/4ji/5GhUj/Kj3pm9lSEGhlq/7vi/8spgfdJj61m9R7ACqxq/+7i//elodkID9BrBIkEDt9q8BHzACf5oZcK0ANzBBmMDHJrAETzAF39sglKwDQ+4RRGoF/newB3+wy31Bs2bwu6qAk4IwCqewCpOeI3CBu5LwnWoAFyTuCtewDd/wCNaBxsLwhKZAAeMwEAexENvgIOwsD8dmEXDwEC8xEzdxIopBRh0xVgpB8jqxFV8xFrvjIEiTFBskFChxFoexGI9xQFLBCHdxK6pAzZIxG7exG8slH3ABB6AxGHIAF6juG+exHu+xZpoB/dJx8e1ABPMxIReyIT8nH7yBBwCy0HnAG+DxIUeyJE9ygfoxI6+aIFOyJm8yJ5dpIovAJXuYCDxyJ5eyKZ9yqpqBDISyY8nAIKMyLMeyLCtrIXyB0bJyPtXAF+joLPeyL/8yyw5CE0QALq9R/gQ0ARgDszIvMzNfbR9wAZUWs/PQABd8bjNfMzZnM/AiQhvMgDRHzQy0AeVqMzmXszlX8DMz8Df/iglU8zm/MzzHMxkPwhVE8zpPCQ1cQTLLMz/3sz9PchlcgTff83jMwBWUwT8ntEIvNEPLBCPUwRDYJUHrxQIMQR20b0NntEZvNEezWB9QgRAwz0Q7BAEIARVYc0entEqvNEu/nBiEAVZxrg+EQRW3tE3fNE7ndB3yARtIgauq6QtIARtAsk4XtVEfNVIz5CB8QRWcMV6qQBV8wT4nNVVXtVVf9W26AR40QQ0wwC8yQA00AR6oLFaXtVmfNVqrah/4ARdAAQ3o/pvbCQANQAEX+AFKpzVe57Ve7zXgIsIafMEW/AAMXCVyIQAM/MAWfMEajDNfN7ZjPzZkbzIflIEf1AEXgMEQtMAGSLTuLMAGtMAQgAEX1IEflAFRRzZqp7ZqrzZr4wYfMIIb6IEfmMEXcEEYNEEVOAERvIAKaIBX8wgDaIAKvAAROEEVNEEYcMEXmIEf6IEbMMJpt7Z0Tzd1Vzde84EbrIEZvMEWVIEN0IAGwDXfCIAG0IANVMEWvIEZrIEbRLd1vzd8x7d8fzB2+8EXhAEU1MAIiPckCcAI1AAUhMEX+EF7z7eBHziCJ7jF9sFfb8EQmAAeOZYEmMAQJPYa3LWC/me4hm84hzsnHwxCHYTBELAA86lZAbDAEIRBHQyCe3e4i784jMc4CRbCIODBFhgBdwpdBxjBFuDBIPCyjAe5kA85kTNXH5hBGAjBHAsgBwhBGJgBhhe5lE85lZ81iGOBD5R4KBaAD2DBilc5mIe5mGezG9QBFvw0P76Al5P1mLe5m7/5DR95E0AvWZ5AE0A5nOe5nu+56DICG2xBw31nC2wBG2A0nx86oid6ujKCGYCBPS8pDYCBGRi6ole6pV/6jpYBFfwA+GSrBfwAFSA0po86qZe6aCJCHRTBks8tBxRBHTC2qce6rM/6LvbBF/zAA5DwA/zAF0Q5rf86sAd7/sfxgRkwwaqPdEFwABOYQYsLu7M/O7THhK3/AGEju0cgAK/7erRvO7eLObFXQadbO1BYQBUwe7efO7oneBlwwbiKe2PEABeIerrPO71jNT2jubvvxgvoc733u7/7MyJ8wSrne3/IwBfA+r8nvMJP8ho0wQYQPIpsQBOE78JXvMWnsB8wAcxCfJdQABPk78WHvMiT7xqAwQtzfKRoABhQ/Mi3vMuL7TPjO8r3ygu488vfPM5b7BpMgW7OvL84wBSwfM4PPdEbKhtgsM/7zBFIa9E3vdNrLY0mveMsQfU+vdVf/XPqARhsvNTrDgWAAdtivdiPPVXyARUsatfXjw5Q/kGzk73bv/0kCnPPpz0QOQAywz3e530N+kHU030iLQHI673gD77L2cEP+P00/UDVEz7jN/5+iQEXI/5BQUFNO77lM34ZNMHcS/5O2b28Xz7oD30tDzTnH9YM7HLop36/DwIWaHnpA1cBYMFUqz7t67kZnO3rP5gNvHLt936RO8IXqHPuA5kJfAEN+z7yZ/gnD7+ijXLbJz/0n3UhUAFSMT+xoQAVAHn0bz9V10GgW7/BtcAPcz/5J/Qa/Cn4L90QCH35t78vI0IYhHv6+50FhAHCuz/+czIbEO/85x4RMD1ALBI4kGBBgwcRJlS4kGFDhw8hRpQ4kWJFixcxZtS4/pFjR48fQYYUOZJkSZMnUaZUuZJlS5cvYcaUOZNmTZs3MfK5UgFAT58/gQYVOpRoUaNHkSZVupRpU6dPoUaVOpVqVatXsWbVupVrV69fwYYVO5ZsWbNn0aZVu5ZtW7dv4QKtcIUPTrt38ebVu5dvX79/AQcWPJhwYcOHESdWvFjhoCpxIUeWPJlyZcuXMWfWvJlzZ8+fQYcWPZo01yqDGKdWvZp1a9evYceWPZt2bdu3cd+1I6N0b9+/gQcXPpx4cePHkSdXvpx5WBl2ckeXPp16devXsWfXvp1799h1XjQXP558efPn0adXv559e/fHX9TxPp9+ffv38efXv59//n//i+qg4b0BCSzQwAMRTFDBBRls0EGqaJDvvwkprNDCCzHMUMMNOXytjhUeDFHEEUks0cQTUUxRxRV7WkHCDmGMUcYZaazRxhtxvI2NHVjs0ccfgQxSyCGJLNJIpXZgI8clmWzSySehjFJKGPU44sgrscxSyy257NLLLy07Qo8pySzTzDPRTFPNNVFiZIsCwIxTzjnprNPOO/H8sYAtGGHTzz8BDVTQQQnFrw4Y8kxU0UUZbdTRRyHtDIYXC63U0ksxzVTTTUkqo4hIQQ1V1FFJLdXUUwEoogxOWW3V1VdhjbXJLzxA1dZbcc1V1115fdCDL2QNVthhiS3WWNf6/sCi12WZbdbZZ6GN9jMs+jjW2muxzVbbbS/ygwhpwQ1X3HHJLdfcpojwg9t12W3X3XcF/SKEc+mt19578c231BCAhdfffwEOWOD8dFJA34MRTljhhRkmUgG6Bo5Y4okprlgwRJpoWOONOe7Y44/bawIRi0ku2eSTUa6ojylAbtnll2GOWebOpqg25ZtxzlnndVee2eefgQ5a6KG1qnnno5FOWuk/kyXa6aehjlpqoqld2uqrsc7aQj62mNrrr8EOW2yFt6hL67PRTlvt2d6wYOy34Y5b7rmXteCNtfHOW++9bzJDQLoBD1zwwQlXlAYz+E5c8cUZl2iQHwqPXPLJ/imvvMgfUGtc8805z5qPMCwPXfTRSS+dwTDM7lz11VkP2AwTTI9d9tlpr305ExBvXffdeYe1Z9uBD1744YnfzOjekU9eeTPNIKH456GPXvrpySIh9+Wxz177CxnJmPrvwQ9f/PGXaqLP7dFPX33r/KiB/Pfhj19+8GtQd/378c8/sTcomN///wEYwNpR4G76M+ABERgTRChLgA104AMhODksjCyBFbTgBS2iBx5EkIMd9OAH38aDMWGQhCW8YBz+BkIVrpCFLQQaDeJgQhnOEHtf4IALcZhDHe6wYxzoFw2BGMTEvQECPDTiEZGYRHtBoIBCdOITkXYFAyiRilW0/uIVnWWAK0CRi12U2BUGgEUxjpGMZSzVALboRTWu0VpcmKIZ4RhHOc4RTwbgAhvxmMdMtaGIdPTjHwEZyCxBoA16NOQhzfSFDAiSkY105CNZlIEfIpKSlewQCiGZSU1ukpMMgqElQRlK/azBBp005SlRmUr12GANonTlK6fTByaokpa1tOUtj8MEm8GSl71kDBcOgEthDpOYxfzMAe7oS2Uucy+YNOYzoRlNacblk8y05jVX0gcoTJOb3fTmN8cChV1ik5zlvEgbHgBOda6Tne2UygMKaU55zvMga/iWO/GZT33uUyhEaCU9AbpMR5yBnwU16EHzeQZHBJShlRSD/vsQGlGJTtSbNRBDQzHaxSsIgKId9ehHnymANGaUpBcchBBAmlKVrhSXQshcSWGavi9ogKU1telNT6mBScaUp6xjBANxGlShDvWRWDhfT5GauDXwiKhNdepT/7iDfyaVqllTJFSxmlWtmlGSVfVqzgoBuq2OlaxltWIYCvFVtUqsD48x61vhGlceVmGca7WrtuwpV73ula8s9OddAUssNqSwr4U17GEdSAMlBZaxmqrDDREbWclO1n8coFRjMbsmKvSPsp317GfFRwEqZJa0U+LCAkCbWtWuNnoLSGZpYUsjLhCAtbW17W2BR4DXxpa3FQIjboEbXOGWDo29NW5+/rgAp+Eul7nNlVwBdntc6VbnDQxw7nWxm13AMaCJ0/XubL7AE+2Ol7zlDVsFdvpd9SbGDPMy73vhG9+nheB667XvX8QwA/nul7/9/dkMLnpfAeOkDCj174ERnGCQCWFVA3YwS/jAMgVPmMIVZtgUUvdgDX+ECxb28IdBnK/obpjEEjEDZEOcYhWvOFwcqG+JYXyQQdyTxTW28Y2ZRYSXxpjEhfAejoEcZCHfqglp5bGA6+CAIS+ZyU0WlQMue2TeztjJVbbylRmlYymXtmtY9vKXwUynLWz5rnYoQZjRnGY1b6kE0CFzT/kwyzXPmc51HhITMvxmgJohAnb2858B/q2iCLxYz9bkwzYDnWhFLzpEUMhzoV9pBrcxmtKVtrSBLEBoSB+SD5+69KdBHer1FOHRm/aiHzYgalWvmtXi2YD9TA3FLrea1rW2NXHGHOsZlgGit/b1r4E9mho0WNcJrMMbg51sZS87MwaIcrHRB1RmT5va1YYMFqCtvUGcwNrd9va313KCHWebdXgwGLjRnW51g0UBeCB358S6bnnPm95XCcO7E8eHIdSb3/3291OGUGp8W20QhP33wRGe8KDQYNwDP1ocJKBwiU+c4hKIocNz9gaKb5zjE+8uxis2646PnOT/zjXIB+bpkq+c5f0uAsrhxYcktJzmNed3EgQO/nNi9YGpNvf5z9e9g7rqXFZuABHQkZ70dK/ADUSH1SCcp3SpT/3bJGi40ws1CPdSnetdr3YIro51NumhA143+9mp3YERil1NWkf72+G+bLCzvUyDEEHc8Z73YIsg7HSvkRtgp3fBD/7WJmi632uEiF4TnvGNZ3UNKIj4DfHBCI63/OVZbYScS34/bsX850EP6ipw3j8iD/3pUU/pk5OePhpP/ethT+mPs/46cQhA7HGf+0QH4OK0n84gyq574Q/fzx3ou+9dwwfeEJ/5zaezDDaP/MX82PnVtz6amyD91Xzh+t33PprTq33BDIKm3zf/+a+sgeOL/y6FMDD64R///iYLwcjsz8sV5J9//TN5pPaviRhQa/8EcABxbAECzP9eIhGWjwAZsAFZTAYSAQFXosMcsAItUMVGTAI/YhAu4AI98AM/7ALWTwMpwvNA8ARRUMFGjwQxwgxS8AVhUME0jQUXIhFoLAZxMAfliwgikAYXgvt0MAiFML7CjwYZ4eiGMAmVcLxW4KhYsA2WMAqlULviCQEZIfCmMAu1cLlMwAmRjwq2MAzFcLhGi/b4IAbGMA3V8LZiIPpQDg/WMA7lkLXcTez2bQ7xMA89awh0bg2QTQ8BMRAPywCm6t3iTRARMRH76t6gjQ+wUBEhMRLjygTcEMZcUBIxMRPhagZh/kzaNPETQTGrsI3H+AAFQvEUURGrUKASp8sOUvEVYdGp3EzATC8WbfEWWWr1vOsGcbEXfRGkiGC6yqCPfrEYjbGjIIDYSqsOjrEZnZGinu2uavEZqbEa80kX16ryrHEbuTGfjGCtGOHMunEcyXGdSsALY0oPynEd2RGc1q6kLrEd5XEeo4kT5YkC6TEf9ZGYMrCcqG8fATIgaSn75MlKBPIgETKVjoCcei4hHfIhNWkHlqkQDA4iLfIiBYkG6k+UGCHVMPIjQTKQNgAdD6kP+iwkUTIl5ygChg6P3MC6VDImZbKMGODw8KgMlGsmdXInragAlJGLBoGjeHIoiTKJ/gRgBEkoKItyKZmSh45SiNzgD5tyKqlShQzAJkuoD9KpKrmyKz/oAVrygBBBvLyyLM3ygSog8g6ID7buLN3yLf8nBFhxeZAQLu3yLuFnBfJnAfGyL/0yfGRAfRDtLwmzMKcHCrRnGg1zMRkTeLBRd8CwMSVzMoOnDHXHFSkzMzVzdmaxc8pgM0EzNEvnJxenENpSNFEzNQsnBDYycbRRNWEzNgXnGxNHMWXzNnEzbB7zbOIxN33zN8PGHpWmD4QSOI3zOKNGAMIyaXwAOZ3zOZ3GB7DmH6GzOq0zZggSaXrzOrmzO1tGOC2GEZTMO8mzPDvGAUiSZCDHPNmzPRnm/gdQBgjdcz7pU1+KUGD6gLbqcz/5k14IYDn9xQn6c0AJlFycIGKYsUAVdEGjJRrXhQ8mjUEldEJ5xQLmslgkjEI1dENvZQraZQ04NERF9FQKEVsWb0RRNEUdpQayRT5V9EVhVFHuE1YcAcVi9EZxlE44YKGGBf9y9EeBNE7671UYAQGCVLvIYBNaYReIARqwIRzWoR764R+otEqt9EqxNEu1dEu5tEu99EurtB/qYR3CARuggRh2oRU2gQyO9LAQID0zRQra1LAyIRaIYRrGgR7AdE/5tE/99E8BNVAFlUrpYRymgRhiIRPmtKakoFX6YFGHCgNI4Rem4Rz2YVAx/jVTNXVTObVTOXUfzmEafoEUMABS2wlABYU6TVWfGmEWmGEcLtVTZXVWabVWbfVW+XQfxoEZZqERVhWXsrNSEEE/f3Wa/sAWomEdcHVZmbVZnfVZoZVK1yEabOEPitWRCEAtBeUQrzWVMiEYuAEfonVcybVczfVcZRUfuCEYFLVbyYgRAwVC3fWRMEEYwMEf0DVf9XVf+bVfA9UfwEEYMGFeechCASUyCdaM6nUc/LVhHfZhITZiu3QcBDZhPcgy1QRRLDaJQEEZ2kFiQTZkRXZkQ7YdlAEUNtZ/YEBNMDNlWSgXuIFkZXZmabZmI5YbcsFlwaczp+QOddaBZiFm/m12aIm2aI22X7lhFn5WePhwSh51aePnEYrhY4+2aq32arHWXNuhGB4BaksHVWsEH702evKAGNgha9E2bdV2bZ+VHYghD8Y2cvrRRuoybmvnFYSWbfV2b/m2b2mVG17BbuVGL5dEHQXXdHKBYf12cRm3cR03U8chZw/Xa96RRmxzcgFnFsDhcTm3cz33c/sUHJQWc4VmNzkkBUgXcC7BGcQVdF33dWE3dq8UH5zhElIXZlJgRgbhdsdmFfJWdoE3eIUXdrlhFXi3Y5DSP3z0eJ/mFTZ3eKE3eqUXdsEhcJkXYYb0QtDwen9GFLBhesE3fMX3dbFBFLi3XmIgQxDh/nxfBgSK4R7GN37ld3499x6KAQTYV1y01T+2M38XhhS0gX4FeIAJmHO1gRT811nAsz48MYHxZRbMoYAleIIpmHHNYXQdGFdGsT8qMoPJ5RbSoYJFeIRJmG/T4RY82FRogD+eNoXF5RUUt4RleIZpOG3HwXpdGFLANjvYIIehJROsoYaFeIiJOGutoV19OFEWqz4IKol5JRjmoYileIqp2GjnIRic2E7OoD5mLotRRRO+t4rFeIzJuGaxQRO8+EuSYD5OM40hJRYiuIzleI7pWGTNIRbcOEtCgDsYIY8hpReoto4FeZAJ2WHboRf8uEjgNDdANJET5RfkoZAleZIp/plf5eEXHPlHSlQ6EjST54QX3KGSRXmUSdlc3YEXPDlFHLQ2mjiVu8QV4riUZXmWablZzcEVXHlEtlg6VC6XjwQTwriWhXmYiblWsWFgfXlBXi43+DKZg0QY7KGYpXmaqZlT7UEYnPlAAvM2WCCbfwQUfreaxXmcydlPuQFlvbk9WMA2yi+dUQSSyzme5XmewfSS3Tk9NGA2+IBY7zlEosAZ6DmgBXqgtdQZoqCfx4MALpQw1hehHWQTApigJXqiJ1obNsGhl2N/GaOFMfpATCEcKDqkRXqiw8EUOto4dngwdvekCWQVYnikYTqmBXocjJelgSN5AcNwbXo9TuGl/mX6p4GansfhFHa6NCr3MBq5qM3DE543qJ36qQMaHDxBqUFjkwkjqamaOfJgGqC6q71aoKcBbrNaM6w6MLB6rI+DGKb0q9m6reW5H4gBrS+jrP1Cp+V6OFzhbN16r/k6ntkBl+86Mo7aL1Y6sH9DCbi6rxV7sct5GpTAsN8Cp22CoyFbNG5BTxk7szVbnOkBhStbLVK6Jhr6sz8jARJ7s1E7tal5GhKAtM1Co++CD27PtTcjFfRatXE7t4uZHVKBtsMiABb6JSLUtytDGHT7uJFbmrGZuLnCAvji7ph7Mk47uam7uml5GqI7K0RALxoyu9siEprausV7vEsZHCLB/rupQiLvYjDRWy1AQR3IO77lu5TVAZ3b2ykQEycu976/4hTgYb4BPMBFGR6Imr+XwnRdwkUNPCxUIZIF/MEhXJLlQRUWHClmdCXEoMLDwhQCOcI9/MPruB1MWsOH4gBhYrRJXCs2QVlBvMVdnI7X4aJT/CdgWyXIcsarIg1A+sV5vMfLOBzSAMcrICZ4EcejYrp9PMmVfIqxO8WD0SVU1ciZwriXvMqtfIqXu8KDNSU6WcqbwhTg98rFfMyF+B5G3MBXOSTcwMudIpzJ/M3hfIS5YcGx0iQ6kM2T4hfifM/5vIQxub0vICUEFM+NIhBCuM8RPdEnOB0CAb0P1CRc/o/Qh2IYFL3SLb2Ah8G7Z28DJV0oouAcLj3URX1+z+GgmVuyKaKdOx0AcmHUXf3Vx1dyaTufRcIEJT2IYT3XdT16rcG3V/Aj+tfLJaHDd73YjR1220ESXHuBJYIPOn0Wjj3apT12MRiyg5shmtnIjWHaub3bP9cYKnubN0LBcTyYvf3c0X1xsQGyLxwi+tjLfTrd5X3e13YcDHuRIaKUcFwJiJ3e/f3fsbYdHhutbSAjulzDFcHBAX7hGd5q5UER0DrNGcIRirPCIwGzGz7jNZ5o6eG8qVoAeJQietnADyGKN/7kUZ5m5+EQqHqZJ+Ks79sFbjvlab7mQZYdXECp/ul6ITTWwOPd5oE+6PvV3nd6ZSWC3L17G4R+6ZneX7dhp9vdIPjZu5Wh6a3+6vNVGViaACJCTtvbFrA+7MWeXG3hpBvVISibuSWhdce+7d0eV/FB2TE6pZcAvcP77fE+7z0VHDB6CRqisJmbyvV+8Al/U7P8nkfwNX2bEmK18B3/8QF1Hyihn2kzIQCfts0d8jV/87903e95Id7PtVWB80m/9L2UwtO5MYj77k2/9V2f771ZIdaTtFnB9W3/9quUFbI5IdLesCMa94G/9bXBmRMiQyE7E4I/+W0fiVMZIZz9s49B+aW/9Y8hlxFCbAP70Kd/+zk/HVwZIT4AskGB/vvJv/TtO5EPoocNm9LLv/03P9Md+SA2KLDd3P3tf/DnHP0LAsXRut/v//8B4p/AgQQLGjyIMKHChQwbOnwIMaLEiRQrWryIMaPBdgA6evwIMqTIkSRLmjyJMqXKlSxbunwJM6bMmTRr2ryJM6fOnTx7+vwJNKjQoUSLGgWwKKnSK0ebOn0KNarUqVSrWr2KNavWrVy78qSkMazYsWTLmj2LNq3atWzbun0LN67cuXTr2r2LN6/eh5S8+v0LOLDgwYQLGz6MOHFXpUpVKH4MObLkyZQrW76MObPJVXs7e/4MOrTo0aRLmz6NOrXq1azPrtIMO7bs2bRr276NGyfj/kWDcvv+DTy48OHEiw/m1Tq58uXMmzt/Dj269OnUq//jZTy79u3cu3v/Lnh3E/Dky5s/jz69+p/DrLt/Dz++/Pn069u/j3/Y+v38+/v/D2B4jGUQYIEGHohgggpOdQx+Dj4IYYQSTkhhhRZOd8yCGm7IYYcecseYHh+OSGKJJp6onTIXrshiiy6+CGOMMj6oDIo23ohjjjoCxdgWO/4IZJBCDukTMjMeiWSSSi7JZJNOSoQMkVJOSWWVATImgpVabslllxsS82SYYo5JZplmntkaMV6uyWabbkamVB9vzklnnXbC9guaeu7JZ59+/gkoQr/cSWihhh5qk1JfIMpo/qOOPgrUK4FOSmmlll6KaX2vQMppp556qZQTn45KaqmPapJpqqquymqrrs6liamyzkqrhko1UGuuuu4aJD6v/gpssMIOCyw+vB6LbLLFJdWbss4+Cy1/4xBLbbXWXottk+NEy2233h6W1BvfjktuubQtk2266q7LbrvwLWNuvPLOK1RSQ9CLb776biWpu/7+C3DAAuu16b4GH4wwSElxkHDDDj9s0z4DT0xxxRZfHNE+EG/MMbeLMNJxyCKLvA3GJp+McsrubjNyyy6TuogfL89Ms7yzqIxzzjrvrOosNf8MNJ2LcBF00UbzWg/PSi/NdNNP1nN01FIPucgSU1+N/nWjKjrNdddefx1hjVmPTTaHi9BQdtpqc/kH2G6Hac82v2CyEya/bGPP23oz+cfafv+t3iIHAE544TdOs3fiK9KjTF9VUaIMPYpPTuE0hl+O+XCIZM555wc2Qnno9dWjJmHEJC166vA14nnrrl+2xuuyzw7eM6rfHh04pExGCji4/97cM7QPT3xgdRSPfPK48QN886nhU4xsxfjqfPWk8aN89tpDRfT23n//WJ7Wj++ZNUrgpoQ15K+v16Dgvw//TWDET3/9W5nDfv5zwTscuvr/7xZz2G+ABDTJvQqIwAQKxRIAbGBa0JEG7aQBHQ6sYFksocAM2m8HGuygB2nS/h4LihAj2AAPNkaIworo54MszB7aWgjDGJIkHCms4UO2ZZ5p2XCHCgmHDH8ouw0AcYgxZB4Pj1iQWKQnFkhsokCwR8QoXi4CUqyiAk3hxCYGYj2ByCISTWHFMKqNAWIsI/2C4UUeZoI/mUjjDoNhxjhOrQByrKP2EOfGFGaoPw3KIwotZ8dA1iwAgiwk7cThRxRWwj+VSOQIxWHISEpykpSsUzscKcIE+CcBmLQgRyoJyoMJIJSkXFveOulAUPgHFKh0oD1KCct5GSCWtLyaEVv5P2v4R324/B8UawlMbuEqmMT8mT96CcBc8CcXyPyfP4oJzWRpIJrUHNkxm6k//mWqh5nYzN8zqwnOWZUgnOR0mMS6mT9AngeP6FyfxsoJz069IJ70zBfq2sk+V5THFfjMH9TqCdBDySCgBCUXO/qpv9d0hzMIZR87CgpROkEhohR9lu8amj+xGWdrGF0fOCoK0i5JIaQk1ZXtOqo/7AQHOSjNn/BKClMiiSumNB1VL1oKQGbghhk4/V8vagpUHZkhqER1VCd62sB9GAM2xjgnUvXXiaJKtUTNmqpV7XTKpzZwHdp8TC7WoVVXXnWsG+IDWc/aJm2EFYXg0CdgXHHRtVpQG2ita4EWQQG76rVKLJWrDfERDVFIRRTRoJ5fa6jSvSo2PYtowWIfCyQl/hzWj+3ARjBKcT6YKKEUwcDGJSfrxsxCdrTeWQQTSItaG3EDtKxt7Q65kdrYZmcRVJCtbT0kC9fqdrcOlMVtf/ubRcQOuMRFkDx4i9zkVk8exW0ubRZhVudKtz8hVK51r0u5FU53u5VJSgq4C97zGBa75C0v14wV3vQ+JimnVa97t1MM88p3vjyL3nvvO5ikHA+//BXOPegL4ABf7B79LbBXkiInAyvYNjcVsIMf7K+fLnjCVVEKwyiM4czoEMIc7jC1cJjhEDdFKUUQsYklswkPq3jFr9rEiV9cr6QMFcY0NoyRWIzjHFMqSjXusU6UEl0fC9kv6dCxkY+MpnQM/nnJNGFMDJgMZaxIAslUrrKTJBHlLLOEMd3Tspefwk0ri3nMLurql88sEsYkGM1sHko0yAznOEsoGm2us0d280I763knG5azn//8HhDvGc276fKgD10TyQF60Yx+Dj0QzebdrBnSlH5J2xqN6Uyvpm+V9vJuFlGDTouaJUfVtKlPDZqojjrLn17Uql9tklOgeta0rsspYB3lTzsC17wWSStqDexgq6UVvWbypxdR4mIrm5/CbrazMeJWZQv52FWVNq9V8exsa9shqrD2kI+9iHl6m9eh2La5zz2QUIx72sfe77phPWV0y9vZWH53j8G9CAfYG9f/nbe/UU3gfd8b/txMEfir8ffvhDdagAavMb6D3HBRs1PhFIezOiP+YnwvYjwYF7X4Kg7yKruv4xnHN8hI3ukUh3zlOnYxykuObyy8vNNFZrnNOazkmcMc3CfXOaQ5evOgz1ejPhexxpMyv6IjmpVCbzp5Val0EYPh6NCNOqRp6PSs79aHVhcxH6i+iDB0/dBh1rrZ/WrmsU84DGBPygLUPmiwnn3uSF0H3DO8gLYnxdV3t3OD6Q74hkq47xP+gt6TkiXC2/kcgW98N8+heAqL4PBJEUPk7dwvx2u+kwW7vILFQHl7eb7OJ9y86dNYwtEreAihT0rPVX/mP2T19LSvoT04DfsCM6L1/kkxdO69XPbaC9+Baf/9fbnAe6WQwPhonvjwn0++izP/viRIvlKqPX0tUxD63G8eOrJf4EFYXykcB7+WMTHe7qtfcfigm/nx24TxM+YD7/cys9eP/7dFu/7u/YD8GTNc/Jdlf5d/Bcg0gyeA7rUG/8cY5ZeAUAYmBiiBOVM6D+he8ceAjBECFphlNzaBH2gxPMaB6hUCGbgb2DeCQ5YMIMiCAZMMKfhe4meCXAaDUWYMLYiD6rJUNaheyDeDuzFQPMhkaJSDRTgscCSE6SUDP/hphTBKSbhkt2CEU9gqtwCF6SUAhcCEn2Z5V7hkpHBLVCiGgMIPu+OF4QV6W/hp/gV3hkKWBgc1hnGoJ+wQQW0IXleghuAWhHYoZKUnh3/4JKnHh9y1hHkIbhIwiENGhIDIiEeChIm4XRJgiPhWBpA4ZKDQb42oiRdyD1BnidtVBpOIb+72iT3mh5uIig4iiKU4XXUgihrnI6zoY1KYirU4H1Yoi9u1Ba94dDyQi0IWV7YojNDxUb+4XTzAi1QnRMbYY8E3jM+4GsXHjMS1AclIdRA3jTRWMtDIjaXBMtm4XV9njUeHguB4YqaQid2ojnhxD2BkjtMlg+N4dGzwjj4WgeuIj3FRgfXoXGwgj21XW/zYY9uYjwV5Ft8okNJFBf+od7GYkDSGCepgkBOZ/hHq4H4P6Vy7yJB6l2wYSWOskI4UKZILcQ+s4JHTVQQbSXlCcJLN2A8jCZMF0Q/S2JK/JQQqGXqOVZM19nExOZEjt5PN1QI42XrfFZQ86ZP4CJRHWVwpQJS8NwJM2WO9cE1JmYr+gIBSWVwj8JTJdwFa2WO2kH5WOYb4YAtgOV0X0JXWp29oWWOm8FlkaYTt4I5u6VwOsJbj9wB22WOREIxyKYHgEAl8OV0PkJfyt5eE2WM8BZj4p1OKWZiH+X8QAJmzGJKNuXn3gIuVKV0QIJkMaAGc6WORsFqY2XjcMJiiOV0W8JkZSCCq6WO/4FSmKXT7sJSw2VwZ0Jom6Bi4/uljkqBWtLly2lBvvjldKrCbMyhuxuljthCXwolu7XCWzMldL5CcP7iH1OljHgidziaC2rldhXidM2g14Dlkj3CK3Wlq2PAI5hleSzCeW+iA7uljofCX6iln4KBu9BleGBifTOh7/OljqdBn+Ell45AKAtqD/5mHpKigQ6YKBWqgHjYO3fag6uWKDJqHAXihTNY7E/pgutOh77WAGmqIkzaiTIYJ6QmiyoUNF5mi6tUHJvqK0xSjWqYMVdmioOUPRHej6qUBNJqMHPSjwPecO9pT7UCTRQpeOyCk1ihzTPpll8CiSIpO2HAJUtpfWPCk48h3Wvplu+AOVtpL7rAL/mBqYIbXpePIoWj6ZVrgP2SaRsugBW6qYCW6puPIBwpgp3UGCqUppynEDZ7YpwWmAOKYp/9IpIVaZ6sgoYE6PuOgUIy6YE6aqCrpkJRqZ67wqJAaOuOwf5q6YBp5qSppB6KKaKmAdZ6qN+GQoKgaYnZQqk/JBwQAq5CWCVXKqjmDDWt0qyJGAIg6q0SZnb+KaNOzqyYDPcYKY+I5rF0ZoMyaqveZrOoCDq8qrTDmg8+al+WYrZQWDPNQrdQyD4/4rTUWj9x6mCxwrrg2B8zwkuOaKf3ADHPQrkPGAuqanJl6r7AWCW8mr30SDanZr0tGqvramm1asLyWBsswmwGb/iT7sAx1uLBRhqcIm5x5VrHW9gtwCLErwg63ubFQRgMYy6BsOLLrBgq6+rHwgQ2EmrJfhocmy6BuELMRlwuM17LRcQ5LerNe5gY0S6Ms+bMd9wtyt7OmsQ4iW7RtdpNCK6Qz1rQvlwudmrRwMQ4+O7V1ZgZQu6ZRubVFBwrToKNXOxb+MA0wG7aUxpVem6cou7ZRZwuIZLYRIQ7TGbe4NrNum6ebk7eEV7V1+w9Z+7fehgh8O6tTULijlwrYULY76g/YgK2LO25TgLjP6q2Ue3m9YLUxOQ5Zqbn7lq6XO6vlGbrglwvUOozgoLWna2/wSbr6KiKu+4CdsAxHOpfL/qBqtKt0ehC7JntAvAuDm4AMHgt97IAMLie8cMd6v0uzmbu8NegK03BPQlcP0xCq0Rt5o+u8GNuR2guJm1AMCJdt5lAMygu+zJeS3eu2KJq+v/gIvcANY0ll+MANvdCe72uBM8q+iMuv+suPIBAL0GC85MUO0BALIADAV3iw/cu3fBCaCwyWltAL01DA/cQO09ALGCTBn2gBwurAl/ulHSyaGJAKxMANx5VC8sANxJAKGEDC/KimIdy9TxbDIwoKvfAM4VC9TFMP4fAMvaC2NxyUMUDDIaywRMyoaSAKuWAM2DAO4roq8zAO2GAMuSAKFKvE2nmxR9y/SbfFhXsI/pygCrbwC8YADdbADePADvKAD487Gv6AD/LADuPADdYADcbwC7agCpxwCGFsrFPnxV6cCK8JyIeMyIecAYkwyI28CFKbyJEsyQDctY5syd87yZmsyZq7vpbsyXxgo5ssyqPctBoAwp5syfRIyqvMygXrj6gMyw3YyrNMy7Dqn7GMy0mhsbXMy718oyWby8F8fb5MzMWsoNwrzLk8wsbMzM0MmTOczNGcFJjszNVszTvZydKszbp8zd3szQIJzNsszgj2hN9szuf8iQLAv+PMzosQB+gMz/HshXHQzvWsFNEqz/msz9m3rfbsz9S8zwEt0IqXzf5s0KA20Amt0F1X/gMH7dCMwQdgu9ATTdEGNwKn/NAH7Qa2WtEd7dG9RgBBm9EjDYAfbdInTWldTNIrDcko7dIvHWWVvNIzvRvLDNM3jdMhBs00zdP3nNM/DdQG1s89TdRKIXZBjdRJPV1sV9RN/WkjpdRRLdWoJQVObdXHBsZTrdVbfVWCfNVfvRtRytVjTdYlxaVgjdafJtZlzdZtHU9nndZxLR5uTdd1XUy3LNd5rRRQbdd97deSVNV6LdifdtR/bdiHHUZMPdiLXWiI7diPDUNDzdiTvXeQbdmXPUA7TdmbLWOY7dmfrTwyzdmjXdKgbdqnzTkqTdqrvQh90JaoDduxnTUOsM6s/m3bEI0Csq3bu/0zKIDRtw3ci0C0vE3cxe0wTxvcyY3Vxs3czT0vXq3c0f1pAenc1W3dyrKQ0q3d4CYz1+3d320qfrDd441viCDR4I3e6U0oI3C45O3e+GYE6i3f870mRvDe9310hU3f+83fP6LY+A3g4Haq/U3gBU4ishrgCa5xiDBOBu7gDx4gJdDeCk7hGlcFEI7hGW4eVVDhHQ52Nq3hIS7iuaHZHm7ix9YHhjziK87imZEBtX3iMW7hLU7jNf4YHC7jOd52DmrjPe7jWpGhOi7kYMcI7PrjR47kT8ECuzfkTd6QSQ7lUe4TDezkVU51eoAAUq7lW/4SCOC7/lYO5pQ3UVxO5mUeElAQ5mneeqps5m0u5a+s5nEeesPt5nVO48gt53keei1t530O4aKt54Eeej3g54VO4D0g6Ik+fnxu6I1u3YCu6JHeej/g6JXO3D8g6Zn+f91t6Z2O2uKt6aH+f2vt6aWO2HAt6qkuf2Vw3qbu6m09AqGo6rOegW3w6rc+1m1A67s+g47gi7gO7EDNA47A68X+g2KQ5cGu7CaNAGlo7M/+g3C77NMe0HsL7df+g4lgA9TO7fFsA4yM7eGuhmuQV91u7s5MAaot7us+g9R97u9Oy9nN7vM+iQAN7/eeyAVN7/ueh4jgA/gO8IDsAxPO7wUvimvw/toBr/Dv6wDqbvAPn4cgvvATT7klDvEXL4r6TfEbv7b/jfEfP44XzvEjf7M4DvInz5B8UKwkz/LSKgO/jfIxn4x9sMstb/OMSgMwLvM7z5B6cGE3D/RaygFfzvNF/5R+gIhBr/QdKgGgbvRPv5ZmwNFLT/XUSQCQDvVZ/5R4UPVdr5p4oPVhv5s87vVlH5RBLvZp35pkb/ZtX49or/ZxP/ZuT/fgCPdyj/fJaQblXPd9z4cCgPV5L/jJyQaJ6feHz4MPAOeDz/gaKgb0h/iRL4Af4OyNb/k0OghGKfmbn3spgMyXD/oa2gehxvml33c1oPOhr/pCygfBa/qvP3ND/gDzq0/7QjqfsI/774bXtc/7pWrruQ/8yqbrvU/8+hoH5R78yQ9pFEDPxe/8GDsIM6D8099mM/D5z4/9z5oIIk/93T9kVQDu2S/+UIvP3m/+CybZ46/+QusHrX7+7+9eI+D060//iMsIogL/+b9dTsDk9e//vwsQXAAMJFjQ4EGECRUuZNjQ4UOIESVOpFjR4kWMGTVu5NjR40eQIUWOJFnS5EmUKVWuZNnS5UuYMWXOpFnT5k2cOXXu5NnT50+gQYUOJfqRyyKkSZUuZdrU6VOoUaVOpVrV6lWsWbVu5drV61ewYcWOJVvW7Fm0adWGFaOi6Fu4ceXOpVvX7l28/nn17uXb1+9fwIEFDyZc2PBhxIknqhCz1vFjyJElT6Zc2fJlzJk1b37Mp4hi0KFFjyZd2vRp1KlVr2bd2vVr2LFlzy5ahA9n3Ll17+bd2/dv4MGFW63zgPZx5MmVL2fe3Plz6NGlT6de3fp1jg/qDOfe3ft38OHFjycvtk8S7OnVr2ff3v17+PHlz6df3/79JH3K7+ff3/9/AAMUECsq7jPwQAQTVHBBBht08EEII5SwLyoGtPBCDDPUcEMO0+qDhwlDFHFEEks08UQUU1RxRRZz4kG/DmOUcUYaa7Rxvy8IaHFHHnv08UcggxRySCKLLIqAL25Uckkmm3TySbT6/hjCSCqrtPJKLLPUcksuuzxuCBihFHNMMss0k0k8KvByTTbbdPNNOOOUc84uK8DjTDzz1HNPPstLBAs6AxV0UEILNfRQRBM9DItE+nT0UUgjlbSyNV5Q9FJMM9V0U0479ZTQF9aYdFRSSzX11Kuo0PFTVlt19VVYY5V11uYIqBBVXHPVdddI+WCCVmCDFXZYYos19tiTmLiNV2abdfZZJ9doAVlqq7X2Wmyz1dbNFkSF9ltwwxUXwzoi2PZcdNNVd112260ugu3GlXdeeusFLwx389V3X3779fffn8Kwd2CCCzaYM0Q+A3hhhht2+GGI+S0CkYMrtvhijNEaRIaI/jv2+GOQQxY5UBkGyfhklFNW+So/TBj5ZZhjlnlmmhM0wY+Vc9Z5Z57xGKFmoIMWemiiiwZthDt5VnpppjP+wgKjo5Z6aqqrtjolC5Jsemuuuyb4DQSuFntssss2W2gE3vB6bbbbHpeLVc+We26667a7WgKOcntvvvtm9ooB7hZ8cMILNzzOAa7we3HGGz8V7sMjl3xyyiuXMG/HM9d8c0jfUMBy0EMXfXTSkVNAbc5TV331M78wt3TYY5d9dtrpikBr1nPXffcm6+igduCDF3544kHqIF7ek1d++Rn9sLR46KOXfnrZX8CZeeyz1z7DQUCk/nvwwxf/ah5M3v58/vTT/w+RX8d3/33442eYCYrVt/9+/Me7IgD5+/f/fwACKwCKy18BDXhA7uAhBAFkYAMd+EA4hSBpCKRgBS24m0EIAYIb5GAHPZgiIZjvgiMkYQkxw4ctfFCFK2RhC9uzhWWZUIYzpGFkzFACF+ZQhzvkIWpKYIYaBlGIQ1RLH5bQQyQmUYlLlMsSwkREKEZRimChggOYeEUsZlGLJnHArab4RTCGUSuDMMIWzXhGNKaxIEYQoRjd+EY4SuUNEFBjHe14xw5CAHVx5GMf/cgUN0wJj4MkZCGlNwQ3/FGRi2TkIurwM0NGUpKTjNwIkNdITGayj3xoAiU9+UlQTq0J/jHUZClN2cc1ECGUq2RlKx9GBG+dUpaz/GMdOOBKXOZSl9biwCVp+Utg9rEQ+NplMY15zE2FoRDBZGYzF9kHhSFTmtOkJpeK8ERnZlObftSD96r5TXCGE0U80MM2zXnORvrBB+JkZzvdWR8fXA+d86QnI82AgnfmU5/7XA4KgFhPgAYUk3XAIT8NelCEJqYEvhRoQx26yDosMKETpWhF3xIChj5UoxtdpBk8YFGQhlSkLfHAPzl6UpRqMg4uG2lLXfpSiZggDimlaU1PKYYdwFSnOxXpDhpjU6AG9ZSDECRPjXpUcA6hjUJlalNLyYhOIlWqUw1lExjhVKxm9Zdv/ngdVb36VS1GYI9aJWtZaemHGIBVrWtdYQzkaVa4xvWXfZgCW+16V/hNAZty5Wtff/kFSOJVsION3Qhw51fEJraZgzgCYR37WMIdYamKpWxlm/mFDEBWs5uNWgYOa1nQhlab0ORsaU37sWuKVrWrpacZVnBa2MZ2XSswKWtte9t5OoILDJBtb30LLAZwwRG4JW5xBdqH9v1WuctFFBP2alzoRreea9Agc617XS4JIZbS5W53H8qGdWJXvONtkQ/Y4F30pjeleGABed37XgaxYILqpW99U1oHEcBXv/tNjwgyal8ABxildWgvfw184Niw4L8CZnCDaRqH8CJYwhM2/owPZupgDGc4q9SlcIc9PBftaljEIzYrXT98YhTXRK8kZnGL5VoILkAtxTOmcUcswIVluljHO/arHWpQYyAHOSE1sAOPjXzkyvYhqkJm8oSb8FwkR1nKiTXDDJp8ZevOoLZT5nKXRcuILRgAy2N2rAG2cFUvp1nNxF3DD8j8ZqT+YLtrpnOdjWuG58FZzwd9wZbt/GdAc/cNgd1zoY85grEGWtGLVi8fuKAmQ0d6khXgAikZfWlMA5gPV+iqpD19xQhcwdKZJnWpG5wILtzy06v+IAe40ChTx1rWLv4CDVh9a/jR4LOz5nWvd+yH6uJa2LQTwlt9fWxkS1nJBRh2/rMNV4AnJ1va07ZzHXTgbGxbTQcLpna3vb1mJR8g2+Me2QGi/W10p7vUfkAPud29ryQYW93zpres62Dld+f7WDPgdr39/e9ZJ4IKJNB3wTtFAirAGuALZ3i6+fAGghtc4nAiwRtG3XCMZ7zeX8D3xD0upBnsWuMjJ3nG7dDuj6c8REkocsld/nKYL8UNW7Ciym0eHwdsIZEx53nPfc4UM6jy5kNvDhH8/HOkJ13pSEHEFX5HdKiXpgNXqN/SrX51rDdlEE2gY9S9rhcINGGyWSd72c2+lEFg4XNfZ/tOFICFsZ9d7nOnO1PKIAVIt13vJKmAFMpQd8AHXvBVYUQb/my9d8Q/hAZtQPPgHf94yFvFD1BI/NehIO/IZ17zm68KH6hwgsqP+wRUuDjnTX961F+lD1eIeOixTIIrQDn1s6d97bXSBy4U2PUGZgEXZG974Adf+F3hwxeEvnvYEuELpR9+853//LGsAQsXQL5XL4CFOUNf+9vn/loKYYaiVv+gQzBDjrt/fvSnvzJ8qIMTxG9MJ9SB+eqnf/3tXxk/MEHG70+jBZiA+fsLQAEcwNzogzfIKf5boR14g98jQAd8QAjsjUG4gtdKQPBZgSuIuwjcQA7swO8wwOOzQMohAgb0QBM8QRS0EEfwAyzYABGsmg3AAj8YrhSsQRu8wRjh/oM4mAJVe0GH4YApiIP5w0EiLEIjnJE1uALQ88FqOYEryL4jjEIpnMIyKQQ/kILDY8JEoQEp8APzo0IwDEMxHJVB4IIeEDctNJID6AEu0MAxfEM4jENdWQMukAExS8MGMQAZ4AIolEM//ENArBdEMAMsgAE8jA4YwAIzqLpAbERHfMSd4QM/OAMiWIBDPIwFIIIz8IMhhERP/ERQ9Bo+EAMuSALqu0SduIAk4AIx6MRQfEVYjEXV4YM1eIMjkChUpIgQOII3WANXlEVgDEZhvB9HGIQvmIIZiBvEI4AZmIIvGAQaHEZpnEZq5CNE8AMugALdizQWgAIu8ANGrEZx/hxHctwmWvyCJpCBzFquDJCBJvgCXyxHeZxHeoyrPrCDN5iCHdCAidKAHZiCN7CDBqxHgixIg5QuRtADM7iCItiBHmQiDtiBIrgCM9CDxjtIjMxIjcw0RFDIN2iCIdCBdaScDNCBIWiCN6jIcNxIlmxJlyQ7RnADMTADKgiDKXCCGFCBmisWB1CBGHCCKQgDKjADMXCDi3xJpExKpYRDPkCEPhiENbADM/iCN7iCLQCDIjgCIyACHWCBENAACWA21igACdCAEGABHSACIziCIgCDLbiCN/gCM7CDNRiEPkCEX1xKvdxLvhzDQojJqKyDNwgDLIACHvABD9CAOywS/gPQAA/wAR6AAiwIgzeoA7o0yi/sS83cTM7MvJicyZq8yZzcSWLpyZ8MyqEsyqPsTNZsTdfkNT4oAz+oAy4AgyFogQ2wRJlZgA1ogSEAAy6oAz8og7x8TeM8TuS8rY40g48MyZGcnJI8yZTUg5VMTuu8Tux0KD4YBDaggib4gRXYP/ixgBX4gSagAjYYhOLMTvZsT/csoYRcyIZ8yCWKyImsyNV8T/3cT/7kHERYgy/Ygh+AgbBxJQSAgR/YAniszv5sUAd90Hq5x3zcx378x4AcSAjNUA3dUCY5xybgARdcqw3ggXeMRw49URRNUfHwUHVkrnYs0fVUURmdURq1/oo+wEYooAEBODEBoAFv9AMMrVEhHdIGvcZs3EZD68ZvZFAibVIn7ctBqIMm2AHS1DcH2IEmqAM3fFIu7dJhLMZjTMbQY0ZnhEYvPVM09UM3wIMmqAHeQkUGqIEmwIOdS1M7vVMIpEVbxMVclIhd7MUYxVNBHVTBk8QrEIK869ORqAAhuAJOJFRIjdSyG8VSPEVFrQlVZMVAlVRO7VRfM8YqcItLhQsVqIJn9FRUTdVSk0RK1M1R9YtM3MRNVVVarVX6GsQmqMBXJY0VaIJFtFVgDdbuGsRC3NXjSMRfFVZlXVa54gM2kII8M9bpeAEpYINZZVZszdZfokM7lNb5/tBDPtRWcR1XWUKEOiiCp/NWB+mAIqgDJiVXeI3XGSrDM1RXFVnDNpRXfd3X/BGDMIgwex0SHwiDn+JXgz1YzbFCLAxYNuFCL0RYiI1YpfGDLchChhUUGtgCAJRYju1YaEnCJbxYTnHCPvRYkz1ZPukDKhACZRTZWCEAIaCCIEVZmq3ZDNFBHnRZbAFCIbRZn/3Z/yhDBNRZd9mBfAVapE3a3VjBFiTah4nBGVRaqZ3atGCEOhgCV3VakVmAIaiD/KRasA3bpgBBrY0aEpxZsU1bjp3AayvbstGBDFRbuZXYCdRVtxUcDNzSud1bVS2DK+i4u7WcGbiCv+Nbw5VU/gMc2sClnQVE28N9XA1lP5Rb3OlJAvmDXMzd0PwTT8p9H//b2MwNXdecQIvtXAeigbgVXdXlS/ZzP9PVofi71tWd3VgchC0Q1ddlIhXYAr2lXd/9xO8Lv9xNI/LLzN893j/EPZYaXkkyAd9DXugFQ+mzVOZlpesr2ejN3gcEv+qtJvLTXvC9v+ILwe5lJ+WT3fBN38BDhDYA3PI9qBlog3dVX/oFPNxD0vcNqd5z3Prt35hbvfzKX6kSgdjzXwP2udVrPQFeK9jj3wN+YGTDvdJdYMKigeeFYAyeNs8LWQqOrdFD3wwOYSNzhDqwgQ4eLxuog2gUYRb2ssk74QO7/rwWnuEd27pOg+EJiwCxo2EeFrDCm2AcTrHF+9oeLmLWioPJDeIxS4ILM2Inrqy7S1QlNrS+K9wnvmKtKoQv+LEpdrYa+ALjxWIx1qi0W7sufre3690xXmNg0uJpOWOVawEwZmM6Bqat6zo4jrqwU+M67uMvMgOOyePQk4Gj82NDHqKmS1dBFr+pm99DfmQDWoNoWmQtLALshWRM1p6go+RRNbpM/mTmebgA5mRvFQGLA2VU3pyZq1JSZticq9NUjmWvkeRW7lxLlmVc3pmTq+XuZblc/uWKMQPF5eX83YFCBmZkZhaOI+YuDrlkfmZc0WIgZuYu1rUwhmZsNpOH/lNgaq7ligPhbA5nAHm4j+pmcy4IDzhlcV7nGBE4bj5neC4IhFM4dq5n/3CELzDEeN7nhoCBL1hhew7o7rg3fi5oieA3gU5o3xBmg25oizBmhY7oy2A3h65ojYg3ic7otBiEKrBoj/aIKuBjjR5ppwi3jz5pkDA3BybphHY0+kRpmP4IVwNnlgZma4tpnEaJbatpiW6znP5plpAznl7nZQNqo3YJaFvpoaZjKsDdo37ql1ABL1rqTAY2qL5qmyg2qvbjPpACscRqsLaJApACpd7q/q21sE5rntA1s6bhQaA8tY7rn4ACkW7r40W1l5ZrveYJV6Nnu85eMUjivR7s/qBIgoL9a9rdtBsmbMYeilCjacSmWTEItsaubLkQgsOO7LR1NCm2bM+WC0qDbM2OV5/+bNPWC6EebZ8dtNNu7b5ANNX22EGYZNeu7b4ogrqO7WDFM9vu7cHoM90eV0YIgwL1beMeDAQIAyIObk8t7eN+7sNIbeb21DpIAei+btBIgX6bbi4Fs8XEbvBWDDNbbu6uUcYKb/Q2DckqbyKtsvR+b9TQMvZOUd3iR/i+79TQAOGa7wdVMvz+b9c4N/5uT6ICcAOHDaUacOv0sQNvcNkgMgVvzS9wagevcNhQAZGLcJeEMc61cA+PjRu7Zg0vSDD7cBNnjjMbcYM0sRNv/vHmWDEVJ8fzdnEaf471jvFh5LAa3/HoCDEcf0U/GGYeH/Ln2AHQ/fE3hDAiX3LrsDAkl0MzWF4mn/LqMIFjfnIcJDAq33L1UDAsL8I6eGcuH3PrIIHt/vIBxC8yX3P38C80j8AwZ3M5hw8zf/MAZK85z3P5kC87R78o13NApw8r7/PnA69AP3T7MC9Ct70gR3RHNxAjX3TT0/FHr3QD8XFJH7wZt3ROR5Abz3S5Q65OH3UGcS5QzzpGkAJSX3UHkQLyPvWR0603ZXVaZ5DgAmhYH7kvyOta7/UE4YAMz3V/cy1fL3YJoS1h/7c18CZjb/YI4YFLTvZeIy1nr3YR/kktaUc2PiAma+/2EQkD0c52I8Msby/3EvEscc80O+Bgc2/3ETmBlkt3O9t0d693E/l0eecyFLJ3fl8RGMr3KAOsfh/4FTEsgNcxMSBfgl94FCGCzD54BmNxhp/4FoFxiAewN+hwit/4FLGARLt47kIrjh95H3ErkI8uUSd5lf8RUz952+KqlY95IBErlw8tnJJ5nBcSn6p5xIKqnP95IrEqnoeriAJ6oycSjBp6rCrwo2/6Iklwpbep3XJ6qjeS4Ir6k7r5qt96Ktl5rA+ofed6sbeSf//6c1qpsU/7K5Eps3cmRgAUtY97LMGCV297RfIouc/7LCkpu9eklNd7/sDPkpbvez8q+sA/fC1JesJ/I2pHfMffEmxffCkiqMev/C5ZKMlH5LqyfM73kilw5MwvoHvqfNJfE38KfQvipNJf/TYZJdQvIHVifdlvk3h6/fRxhCuYfd1/kyvAddvfnW7afeF/E3L6fd6hgsUefuXvkgiYauPXnMZfful3k8h//sWJA32efu1/ExhoYutvm2HafvGfE2X6fq8ho/FP/zlhI/NnGltSf/ifk15q/5xR/fi/fzpxffrHmFTCf/8PFIAgsmYRwYIGDyJMqHAhw4YOH0KMKHEixYoWL2LMqHEjx44eP4IMKXIkyZImT6JMqXIly5YuXy768gEAzZo2/m/izKlzJ8+ePn8CDSp0KNGiRo8iTap0KdOmTp9CjSp1KtWqVq9izap1K9euXr+CDSt2LNmyZs+iTat2Ldu2bt/C3fnhC8y6du/izat3L9++fv8CDix4MOHCePk0iat4MePGjh9Djix5MuXKli9jzqx5M+fOnj+DDi36ZhM+hk+jTq16NevWrl/Dji17dko9Nkbjzq17N+/evn8DDy58OPHixo8jT66cpg09tJ9Djy59OvXq1q9jz26xzojl3r+DDy9+PPny5s+jT69+PXvwI+pojy9/Pv369u/jz+86UZj2/v8DGKCAAxJYoIEHIpigggvSFEYi+kEYoYQTUlih/oUXyubGEAxy2KGHH4IYoogjkliiiSeKNoQbGLLYoosvwhijjBfaYQKKN+KYo4478tijjz8CGaRoJtgxo5FHIpmkkksyqdIbEAgZpZRTUlmllVdimaWW7EHwRpNfghmmmGOSKSFiW6KZppprstmmm2/CGedOpZVZp5134pmnnncNYoScfwIaqKCDElqooYeOZsQgezLaqKOPQtpoHDAgWqmll2KaqaabcmopDHFEGqqoo5JaKoRUONCpqquy2qqrr8Iaq3oOUGGqrbfimquugvEhhay/AhussMMSW6yxYUlh2q7LMtuss89S1McSx1JbrbXXYputtpku0Qe034Ib/q64oq5Rw7bnopuuuuuy226HNQw0rrzz0lvvjGaU4K6++/Lbr7//AsxZCWbYW7DBByOcXRsPBNywww9DHLHEEyP1QBsJY5yxxhsHxscWFIMcssgjk1yytVsoy7HKK7Pcckd9FGGyzDPTXLPNN7dZhLcu89yzzz4PIgTOQxNdtNFHI52gEIv+3LTTT9PrxwxJU1211VdjnbVuM/gBtddfg20rHiFoXbbZZ6OdttphhYBH2G/DHXeZVFCwtt1345233nvTREGtcgMeuOAtXhEA34cjnrjii5McwBWDQx655PH1yrjll2OeuebaJju555+DzhoiTGxeuumno566pUwg/hK6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KzZhSx345ktfKhbhAGD/NGLahelBGSgBKyhBGeyXhHOa9q1iEX49+EWD/kGJGBx6oV91Agh6ocgHGEKLfyoWodylHzQswYztYRt+gS9ZAhN+YRvQnYg3xfpjX9nKPzS0XYvbARyiYRhyQRU8QRLSIAcSIAFyIA0kwRNUIReGIRrAASDa/RtIsKDBgwgTKlzIsKHDhxAjSpxIsaLFixgzatzIsaPHjyBDPsQHoKTJkyhTqlzJsqXLlzBjypxJs6bNmzhz6tzJs6fPn0CDCh1KtKjRo0iTKl3KtKnORUucSp1KtarVq1izat3KtavXr2DDikVqTqTZs2jTql3Ltq3bt3Djyp1Lt67du3jz6t3LV625sYADCx5MuLDhw4gTK17cdVETxpAjS55M/rmy5cuYM2tuOa2v58+gQ4seTbq06dOoU6tezbr1v2mbY8ueTbu27du4c+NcxEW379/AgwsfTry44F+ukytfzry58+fQo0ufTt30L+PYs2vfzr27d7CL6nwfT768+fPo0w8VVb29+/fw48ufT7++/fmi1Ovfz7+////g+QHggAQWaOCBCFrFz30MNujggxBGKOGEFDbHT4IYZqjhhhwOt8ggHYYo4ogkllhcWRWmqOKKLLbo4osw0veXiTTWaOONOAK1CCM59ujjj0AGOdQzMRZp5JFIJqnkkkxC9IyQUEYp5ZT6LbKIAFRmqeWWXCJoS5NghinmmGSWaSZqtnSp/uaabLapmJUcuCnnnHTWmVkjZ+ap55589unnnwU1YueghBZqaE5WnnDooow26qhRAgEq6aSUVmrppdS18+imnHaqpZVDeCrqqKQ22hmmqKaq6qqstpoWbKXGKuusB1opBa245qqrj7e46uuvwAYrbKq37Grssch6uMgbyTbr7LP7/THstNRWa+21L/4B7bbcdouYlXF4K+645Np2Drbopqvuuuwud0658MYrr1JWgjjvvfjmG5Yy7fbr778AB9yWMvoWbPDBKlnJB8IMN+zwT6YILPHEFFdssUGmPKzxxtxauUgDHIcs8sj1XGzyySin/Gs9I7fscqwew/DyzDTP/muNyjjnrPPOZlpT889AD+qxE0EXbfSxs/Cs9NJMN13hLEdHLbWUHt869dVYP7qP01x37fXXz+2T9dhkk+jxF2WnrTab24Dt9ttwx83XNmvXbfd/Hgt499585/il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"""
					self.send_header("Content-Type", "image/gif")
					self.wfile.write(base64.b64decode(base64data))
						
		finally:
			touch (g.tmplock)
			try:
				os.unlink(g.tmplock)
			except: 
				print ("unable to unlink "+g.tmplock)
			self.gateway.httpLock=self.gateway.httpLock-1
					

					
if __name__ == "__main__":
	if len(sys.argv)>=2:
		print ("One command line argument passed. Running in daemon mode without user interface")
		
		if len(sys.argv)==2:
			print ("Fatal error. Mandatory arguments missing.\n Try \"python cjdradio.py nogui autoplay\"\n Or try \"python cjdradio.py nogui <station tracker peer ip address> <path to MP3 shares folder> <station ID> <your tun interface ip> [podcast [path/to/covers.txt path/to/coverdir/]]\"")
			print ("The podcast option enables podcasts")
			print ("covers.txt define the cover of each album, first line album name, next line image file basename. Use UNIX-style line separators");
			print ("coverdir is the directory in which cover image files can be found");
			exit(0)
			
		
	o = Cjdradio()
	home = expanduser("~")
	basedir=os.path.join(home, ".cjdradio")
	
	if not os.path.isdir(basedir):
		os.makedirs(basedir)

	videosharesdir=os.path.join(basedir, "VideoShares")
	
	if not os.path.isdir(videosharesdir):
		os.makedirs(videosharesdir)

	videounshareddir=os.path.join(basedir, "VideoUnshared")
	
	if not os.path.isdir(videounshareddir):
		os.makedirs(videounshareddir)




	with open(os.path.join(basedir,'justtouched.txt'), 'w') as myfile:
		myfile.close()

	if len(sys.argv)==1:
		UIThread = Thread(target = Gtk.main)
		#UIThread.daemon = True
		UIThread.start()
		
			
		print ("UI started")
	ip="::"
	ip2="::"
	
	if o.getGateway().get_settings_ip6addr()!="::": 
		o.getGateway().peers.append(o.getGateway().get_settings_ip6addr())
		ip=o.getGateway().get_settings_ip6addr()
	
	tmplock = os.path.join(basedir, "cjdradio.lock")

	
	o.getGateway().tmplock = tmplock
	#useless AFAIK
	if len(sys.argv)>=6: 
		ip = sys.argv[5]
	if len(sys.argv)>=7:
		ip2 = sys.argv[6]
	
	
	WebRequestHandler.gateway=o.getGateway()
	WebRequestHandlerFlac.gateway=o.getGateway()
	WebRequestHandlerVideo.gateway=o.getGateway()
	
	server = HTTPServerV6(("", 55227), WebRequestHandler)
	o.getGateway().set_webserver(server)
	WebserverThread = Thread(target = server.serve_forever)
	o.getGateway().set_webserverThread(WebserverThread)

	flacserver = HTTPServerV6(("", 55228), WebRequestHandlerFlac)
	flacWebserverThread = Thread(target = flacserver.serve_forever)

	videoserver = HTTPServerV6(("", 55229), WebRequestHandlerVideo)
	videoWebserverThread = Thread(target = videoserver.serve_forever)








	if len(sys.argv)==1 or len(sys.argv)==3:

		WebserverThread.daemon = True
		flacWebserverThread.daemon = True
		videoWebserverThread.daemon = True

	
	flacWebserverThread.start()
	WebserverThread.start()
	videoWebserverThread.start()
	print ("Webservers started")
	
	o.getGateway().banner_daemon = Thread(target = banner_daemon, args = (o.getGateway(),))
	if len(sys.argv)==1 or len(sys.argv)==3:

		o.getGateway().banner_daemon.daemon = True
	
		o.getGateway().banner_daemon.start()
	
	print ("Banned stations daemon started")

	o.getGateway().crawler_thread = Thread( target = crawler_daemon, args= (o.getGateway(), ))
	o.getGateway().crawler_thread.daemon = True
	o.getGateway().crawler_thread.start()
	
	print ("Crawler thread started")

	home = expanduser("~")
	basedir=os.path.join(home, ".cjdradio")

	
	if len(sys.argv)>=6:
		g.shared_dir = sys.argv[3]	
		print ("Scanning "+sys.argv[3]+" directory for mp3 tags")
		g.ID=sys.argv[4]
	else: 
		print ('Scanning <$HOME>/.cjdradio directory for mp3 tags');
		g.shared_dir = os.path.join(basedir, "Shares")

	o.getGateway().scanthread = Thread( target = indexing_daemon, args = (o.getGateway(), ))
	o.getGateway().scanthread.daemon = True
	o.getGateway().scanthread.start()
	
	o.getGateway().pingthread = Thread( target = tracker_update_daemon, args = (o.getGateway(), ))
	o.getGateway().pingthread.daemon = True
	o.getGateway().pingthread.start()
	if len(sys.argv)==3:
		if g.get_settings_ip6addr=="" or g.get_settings_ip6addr=="::1": 
			print ("Sorry, fatal error")
			print ("Please set your tun interface IP address either in GUI tab named Network or in the ~/.cjdradio/settings_ip6addr.txt file")
			exit()
		print ("contacting initial peer")
		g.peers.append(g.get_settings_ip6addr())
		ip=g.get_settings_ip6addr()
		
		newpeers = []
		MyPeerList = []
		
		if os.path.exists(os.path.join(basedir, "settings_peersList.txt")): 
			with open(os.path.join(basedir,'settings_peersList.txt'), 'r') as myfile:
				MyPeerList=myfile.read().split("\n")
				myfile.close()

		MyPeerList.append("200:abce:8706:ea81:94:fcf4:e379:b988")
		MyPeerList.append("fc71:fa3a:414d:fe82:f465:369b:141a:f8c")

		if os.path.exists(os.path.join(basedir, "settings_crawledpeersList.txt")): 
			with open(os.path.join(basedir,'settings_crawledpeersList.txt'), 'r') as myfile:
				MyPeerList=MyPeerList+myfile.read().split("\n")
				myfile.close()
		
		dex=0;
		
		
		
		while dex < len(MyPeerList):
			initialPeer = MyPeerList[dex]
			try: 
				newpeers = []
				print("trying to reach initial peer "+initialPeer)
				newpeers = OcsadURLRetriever.retrieveURL("http://["+initialPeer+"]:55227/listpeers").split("\n")
				print(str(len(newpeers))+" new peers added from "+initialPeer)
				dex=len(MyPeerList)
			except: 
				print("This initial peer is currently offline")
				dex=dex+1
		
		newnewpeers = []
		for p in newpeers:
			if not p in g.peers: 
				newnewpeers.append(p)
		
		g.set_peers(g.peers+newnewpeers)

		# Launching playback
		
		ir = internetRadio(g, TUIDisplay(), True)			
		g.radio = ir
		ir.play()
		
		tui=True
		
		while tui: 
			try:
				inp = input ("User input watcher watching…\n")
			except: 
				tui=False
				if g.radio.player.is_playing(): 
					g.radio.stop()
				break
			if inp == "help":	
				print ("available commands: help, peers, wall <message to any connected client's console>, blockwall <ip>, \nplus, resetplus")
			elif inp.startswith("wall"): 
				for pe in g.get_peers(): 
					if pe != "":
						OcsadURLRetriever.retrieveURL("http://["+pe+"]:55227/wall?"+urllib.parse.quote(inp ,safe=''))
			elif inp.startswith("blockwall"): 
				print ("this feature is awaiting an implementation")
			elif inp == "peers":
				print (g.get_peers())
			elif inp == "plus": 
				print ("plussing current station")
				g.plus(g.radio.ip)
				print (f"station {g.radio.ip} has now a score of {g.plussed[g.radio.ip]}")
			elif inp == "resetplus":
				g.resetplus() 
			elif inp == "": 
				print("Skipping")
				if g.radio!=None:
					print("found radio")
					if g.radio.player.is_playing():
						print("radio is playing")
						g.radio.stop()
						g.radio.play()
					else:
						g.radio.stop()
						if not g.radio.threadPlay is None:
							print ("radio is buffering")
							g.radio.bufferingLock = False
							g.radio.threadPlay.join(0)
							g.radio.play()
			
						
	elif len(sys.argv)>=6:
		

		
		
		o.getGateway().settings_ip6addr=sys.argv[5]
		print ("contacting initial peer")
		g.registered = True
		g.set_processedPeers([])
		g.set_peers([])
		
		newpeers = []
		
		g.peers.append(g.get_settings_ip6addr())
		
		try: 
			newpeers = OcsadURLRetriever.retrieveURL("http://["+sys.argv[2]+"]:55227/listpeers").split("\n")
		except: 
			print("This initial peer is currently offline")
		newnewpeers = []
		for p in newpeers:
			if not p in g.peers: 
				newnewpeers.append(p)
		
		g.set_peers(g.peers+newnewpeers)
		
		if len(sys.argv)>=7:
			if len(sys.argv)==7:
				g.podcast = True
				g.podcaster = Podcaster(g, None, None, None, None, None, None, None, None)
			elif len(sys.argv)>=9:
				g.podcast = True
				g.podcaster = Podcaster (g, None, None, sys.argv[7], sys.argv[8], None, None, None)
