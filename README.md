I wrote a python script to automatically display the cover art from the currently playing track in Pleaxamp.
I bought a 7" HDMI monitor ($33 on Amazon) and attached it to my plexamp headless Pi.  
Every 15 seconds it queries the plex server and if something is playing, displays the cover art.  If not, it's blank.
The script assumes that you know Linux to set the environment up, but its really as simple as running xserve without a window manager and getting everything to start at boot.  
I can't really comment on how secure it all is, but it's ok for an hour of my time.
