* prerequisites

You'll need to install Python>= 3.12.3, libvlc and PIP (python package installer) through your usual software channels provided by your operating system. 

* How to join a Cjdns network: 
  please refer to https://cremroad.com/hyperboria

* installation of dependencies
  
  pip install python-vlc

  pip install tinytag

  pip install pytz
  
  ** Note that externally managed environnements will require either a virtual environnement, the use of externally managed package provided by your distribution (like as an example python3-vlc and so on, if available) or the use of --break-system-packages with Pip, which is dangerous for your system install
  
* run the app

  python3 cjdradio.py
* daemon mode
  
  python3 cjdradio.py no-gui
