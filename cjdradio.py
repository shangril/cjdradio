#!/usr/bin/env python


from time import sleep 

import random

from datetime import datetime
try: 
	from pytz import timezone
except:
	print ("Error importing pytz ! Try \"pip install pytz\"")
	exit(0)

import sys
import os


try:
	from tinytag import TinyTag
except:
	print ("Error importing TinyTag ! Try \"pip install tinytag\"")
	exit(0)
	
try:
	if len(sys.argv)==1: 
		import vlc
except:
	print ("Error importing python-vlc ! Try \"pip install python-vlc\"")
if len(sys.argv)==1: 
	import gi
	gi.require_version('Gtk', '3.0')
	from gi.repository import Gtk	

from os.path import expanduser

from threading import Thread

import urllib.request

import requests


from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import socket

def indexing_daemon(g): 
	while True: 
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
								myfile.write("%s" % tags.artist)
								myfile.close()
						if not os.path.exists(os.path.join(datadir, mp3.name+".album.txt")):
							tags = TinyTag.get(os.path.join(shareddir, mp3.name))
						
							with open(os.path.join(datadir,mp3.name+'.album.txt'), 'w') as myfile:
								myfile.write("%s" % tags.album)
								myfile.close()
						if not os.path.exists(os.path.join(datadir, mp3.name+".title.txt")):
							tags = TinyTag.get(os.path.join(shareddir, mp3.name))
						
							with open(os.path.join(datadir,mp3.name+'.title.txt'), 'w') as myfile:
								myfile.write("%s" % tags.title)
								myfile.close()
				unshareddir=os.path.join(basedir, "Unshared")
				if not os.path.exists(unshareddir):
					os.makedirs(unshareddir)
				files = os.scandir(unshareddir)
				for mp3 in files: 
					if mp3.name.endswith(".mp3"):
						if not os.path.exists(os.path.join(datadir, mp3.name+".artist.txt")):
							tags = TinyTag.get(os.path.join(unshareddir, mp3.name))
						
							with open(os.path.join(datadir,mp3.name+'.artist.txt'), 'w') as myfile:
								myfile.write("%s" % tags.artist)
								myfile.close()
						if not os.path.exists(os.path.join(datadir, mp3.name+".album.txt")):
							tags = TinyTag.get(os.path.join(unshareddir, mp3.name))
						
							with open(os.path.join(datadir,mp3.name+'.album.txt'), 'w') as myfile:
								myfile.write("%s" % tags.album)
								myfile.close()
						if not os.path.exists(os.path.join(datadir, mp3.name+".title.txt")):
							tags = TinyTag.get(os.path.join(unshareddir, mp3.name))
						
							with open(os.path.join(datadir,mp3.name+'.title.txt'), 'w') as myfile:
								myfile.write("%s" % tags.title)
								myfile.close()


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
									myfile.write("%s" % tags.artist)
									myfile.close()
							if not os.path.exists(os.path.join(datadir, mp3.name+".album.txt")):
								tags = TinyTag.get(os.path.join(shareddir, mp3.name))
						
								with open(os.path.join(datadir,mp3.name+'.album.txt'), 'w') as myfile:
									myfile.write("%s" % tags.album)
									myfile.close()
							if not os.path.exists(os.path.join(datadir, mp3.name+".title.txt")):
								tags = TinyTag.get(os.path.join(shareddir, mp3.name))
						
								with open(os.path.join(datadir,mp3.name+'.title.txt'), 'w') as myfile:
									myfile.write("%s" % tags.title)
									myfile.close()
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
			g.set_peers([])
			#finally: 
			#	lock.release()
			newpeers = []
			
			
			
			g.peers.append(g.get_settings_ip6addr())
			
			try: 
				newpeers = OcsadURLRetriever.retrieveURL("http://["+b.get_object("cb_initial_peers").get_active_text()+"]:55227/listpeers", reqtimeout = 12).split("\n")

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
							b.get_object("discover_button").set_label("Discover new stations peers ("+str(len(g.peers))+")")
						finally: 
							#lock.release()
							print("Banner daemon updated Discover New Station Peers")
					finally: 
						g.cbsinglestationlock = False
			except: 
				print ("Initial peer not responding")
				
		#then we can retest each banned peer to see if it pong and if so remove it from banned
		newBanned = []
		for p in g.bannedStations:
			if p!='':
				try: 
					pong = ''
					pong = OcsadURLRetriever.retrieveURL("http://["+p+"]:55227/ping",  max_length = 120000, reqtimeout = 8)
					if pong!='pong':
						raise ValueError("no replying peer "+p+" on ping request")
				except: 
					newBanned.append(p)
		#lock = threading.Lock()		
		#lock.acquire()
		#try:
		g.bannedStations = newBanned
		#finally: 
		#	lock.release()
		
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
	registered = False
	bannedArtists=[]

	accessList = []

	dling = False;

	radio = None

	shared_dir = ''

	scan = None
	
	scanThread = None
	
	ID = 'Another random'
	
	webserver_thread = None
	bannerdaemon_thread = None
	bannedStations = []
	settings_ip6addr = "::"
	webserver = None
	
	processedPeers=[]
	peers = []
	
	h = None
	
	cbsinglestationlock=False;

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
				self.settings_ip6addr=myfile.read()
				myfile.close()
				if len(sys.argv)==1:

					self.builder.get_object("settings_ip6addr").set_text(self.settings_ip6addr)
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

		
			self.builder.get_object("cb_initial_peers").append_text("fc71:fa3a:414d:fe82:f465:369b:141a:f8c")
			self.builder.get_object("cb_initial_peers").set_active(0)
			
			
	def shared_dir_scan(self):
		if self.scan == None:
			self.scan = os.scandir (self.shared_dir)
		return self.scan
class Handler:


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
			peersList=myfile.write("%s" % peersList)
			myfile.close()
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
		
	def onBanArtist (self, *args): 
		g.bannedArtists.append(g.radio.artist)
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
		print("Stopped web server, bannerdaemon, scan thread")
		Gtk.main_quit()
	def onID(self, *args):
		g.ID = b.get_object("station_id").get_text()

		home = expanduser("~")
		basedir=os.path.join(home, ".cjdradio")
		
		if not os.path.isdir(basedir):
			os.makedirs(basedir)


							
		with open(os.path.join(basedir,'settings_id.txt'), 'w') as myfile:
			myfile.write("%s" % g.ID)
			myfile.close()


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
			peersList=myfile.write("%s" % peersList)
			myfile.close()
		g.load_settings_from_disk()
		
	def onWebserverRestart(self, *args): 
		newIP=b.get_object("settings_ip6addr").get_text()
		
		home = expanduser("~")
		basedir=os.path.join(home, ".cjdradio")
		
			
		with open(os.path.join(basedir,'settings_ip6addr.txt'), 'w') as myfile:
			myfile.write("%s" % newIP)
			myfile.close()
			
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
		
		


class HTTPServerV6(ThreadingHTTPServer):
	address_family = socket.AF_INET6

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
				while peer=='' or peer in self.g.bannedStations:
					tmpPeer = random.choice (self.g.peers)
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
						self.g.get_builder().get_object("cbsinglestation").remove_all()
						for i in self.g.peers: 
							if i not in self.g.bannedStations:
								while g.cbsinglestationlock:
									sleep (0.5)
								
								g.cbsinglestationlock = True
								try: 
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
						try: 
							if self.bufferingLock:
								char_array+=char
							else:
								raise ValueError("Skip")
							#
						finally: 
							self.bufferingLock = False
						if len(char_array)>32000000:
							char_array=b""
							valid=False
							print("MP3 file greater than 32000 kilibytes, or Skip signal, received, aborting")
							break
					print ("Finished download")
				except:
					char_arry=b""
			
			
				if len(char_array)>0: 
					home = expanduser("~")
					datadir=os.path.join(home, ".cjdradio")


					with open(os.path.join(datadir,'temp.mp3'), 'wb') as myfile:
						myfile.write(char_array)
						myfile.close()
					if self.player is not None and self.player.is_playing():
						self.player.stop() 
					
					self.player = vlc.MediaPlayer(os.path.join(datadir,'temp.mp3'), 'rb')
					em = self.player.event_manager()
					em.event_attach(vlc.EventType.MediaPlayerEndReached, self.onEnded, self.player)

					

					
					self.display.set_text(song.split("\n")[1]+" - "+song.split("\n")[3]+" ["+song.split("\n")[2]+"]")
					
					myid = "Another random"
					
					try: 
						myid = OcsadURLRetriever.retrieveURL("http://["+self.ip+"]:55227/id")
						
					except: 
						pass
					if len(myid)>60:
						myid = myid[0-60]	
					#lock = threading.Lock()
					#lock.acquire()
					
					#try: 
					self.g.get_builder().get_object("lasttuned").set_text(self.ip+"\n"+myid)
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
	def retrieveURL(url, max_length = 32000, reqtimeout = 800):
		try: 
			r = requests.get(url, timeout=reqtimeout, stream=True)
			char_array=b"";
			for char in r.iter_content(1024):
				char_array+=char
				if len(char_array)>max_length:
					raise ValueError("Invalid Ocsad URL")
			return char_array.decode("utf-8")
		except(TimeoutError):
			raise ValueError("Invalid Ocsad URL")
		except: 
			raise
class WebRequestHandlerFlac(BaseHTTPRequestHandler):
	gateway = None
		
	def do_GET(self):
		
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

		if path=='/flac':
			print (query)
			basename = os.path.basename(urllib.parse.unquote(query))
			filepath = os.path.join(g.shared_dir, basename)
			if basename.endswith(".flac") and os.path.exists(filepath):
				if not os.path.getsize(filepath) > 4000000000:
					with open(filepath, 'rb') as myfile:
						tmp = myfile.read()
						myfile.close()
						self.wfile.write(tmp)
				else:
					print ("Trying to serve a flac file greater than 4GiB, aborting")				
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

class WebRequestHandler(BaseHTTPRequestHandler):
	gateway = None
		
	def do_GET(self):
		

		home = expanduser("~")
		basedir=os.path.join(home, ".cjdradio")

		path = urllib.parse.urlparse(self.path).path
		query = urllib.parse.urlparse(self.path).query
	
		self.send_response(200)
		self.send_header("Server", "Cjdradio")
		if (path!="/mp3" and path!="flac"):
			self.send_header("Content-Type", "text/plain")
		else:
			if path=="/mp3": 
				self.send_header("Content-Type", "audio/mpeg")
			if path=="/flac":
				self.send_header("Content-Type", "audio/flac")
		self.end_headers()
		reply="Cjdradio\n"
		reply=reply+"Version: 0.1\n"
		

		
		if path=="/":
			self.wfile.write("Cjdradio\n0.1\nhttps://github.com/shangril/cjdradio".encode("utf-8"))
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
			#import threading
			#lock = threading.Lock()
			#lock.acquire()
			#try: 
			self.wfile.write(self.gateway.ID.encode("utf-8"))
			#finally: 
			#	lock.release()
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
		if path=='/mp3':
			print (query)
			basename = os.path.basename(urllib.parse.unquote(query))
			filepath = os.path.join(g.shared_dir, basename)
			if basename.endswith(".mp3") and os.path.exists(filepath):
				if not os.path.getsize(filepath) > 30000000:
					with open(filepath, 'rb') as myfile:
						tmp = myfile.read()
						myfile.close()
						self.wfile.write(tmp)
				else:
					print ("Trying to serve a mp3 file greater than 30000 kilibytes, aborting")
			else: 
				if self.client_address[0]==g.settings_ip6addr or self.client_address[0] in g.accessList: 
				#local machine or allowed one
					unshareddir=os.path.join(basedir, "Unshared")
					if not os.path.exists(unshareddir):
						os.makedirs(unshareddir)

					filepath = os.path.join(unshareddir, basename)
					if basename.endswith(".mp3") and os.path.exists(filepath):
						if not os.path.getsize(filepath) > 30000000:
							with open(filepath, 'rb') as myfile:
								tmp = myfile.read()
								myfile.close()
								self.wfile.write(tmp)
						else:
							print ("Trying to serve a mp3 file greater than 30000 kilibytes, aborting")
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

					
					
if __name__ == "__main__":
	if len(sys.argv)>=2:
		print ("One command line argument passed. Running in daemon mode without user interface")
		
		if len(sys.argv)!=6:
			print ("Fatal error. Mandatory arguments missing.\n Try \"python cjdradio.py nogui <station tracker peer ip address> <path to MP3 shares folder> <station ID> <your tun0 interface ip>\"")
			exit(0)
			
		
	o = Cjdradio()
	home = expanduser("~")
	basedir=os.path.join(home, ".cjdradio")
	
	if not os.path.isdir(basedir):
		os.makedirs(basedir)
	with open(os.path.join(basedir,'justtouched.txt'), 'w') as myfile:
		myfile.close()

	if len(sys.argv)==1:
		UIThread = Thread(target = Gtk.main)
		#UIThread.daemon = True
		UIThread.start()
		
			
		print ("UI started")
	ip="::"
	
	if o.getGateway().get_settings_ip6addr()!="::": 
		o.getGateway().peers.append(o.getGateway().get_settings_ip6addr())
		ip=o.getGateway().get_settings_ip6addr()
	
	if len(sys.argv)==6: 
		ip = sys.argv[5]
	
	WebRequestHandler.gateway=o.getGateway()
	WebRequestHandlerFlac.gateway=o.getGateway()
	
	server = HTTPServerV6((ip, 55227), WebRequestHandler)
	o.getGateway().set_webserver(server)
	WebserverThread = Thread(target = server.serve_forever)
	o.getGateway().set_webserverThread(WebserverThread)

	flacserver = HTTPServerV6((ip, 55228), WebRequestHandlerFlac)
	flacWebserverThread = Thread(target = flacserver.serve_forever)

	if len(sys.argv)==1:

		WebserverThread.daemon = True
		flacWebserverThread.daemon = False


	
	flacWebserverThread.start()
	WebserverThread.start()
	print ("Webservers started")
	
	o.getGateway().banner_daemon = Thread(target = banner_daemon, args = (o.getGateway(),))
	if len(sys.argv)==1:

		o.getGateway().banner_daemon.daemon = True
	
		o.getGateway().banner_daemon.start()
	
	print ("Banned stations daemon started")

	home = expanduser("~")
	basedir=os.path.join(home, ".cjdradio")

	
	if len(sys.argv)==6:
		g.shared_dir = sys.argv[3]	
		print ("Scanning "+sys.argv[3]+" directory for mp3 tags")
		g.ID=sys.argv[4]
	else: 
		print ('Scanning <$HOME>/.cjdradio directory for mp3 tags');
		g.shared_dir = os.path.join(basedir, "Shares")

	o.getGateway().scanthread = Thread( target = indexing_daemon, args = (o.getGateway(), ))
	o.getGateway().scanthread.daemon = True
	o.getGateway().scanthread.start()
						
	if len(sys.argv)==6:
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

		
