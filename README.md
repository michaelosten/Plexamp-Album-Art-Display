I wrote a python script to automatically display the cover art from the currently playing track in Pleaxamp.
I bought a 7" HDMI monitor ($39 on Amazon) and attached it to my plexamp headless Pi.  Any HDMI montitor would work.  I probably should have spent a couple more dollars for a touchscreen version.  Here is what I ordered.  https://www.amazon.com/dp/B0B8S9DYQC?psc=1&ref=ppx_yo2ov_dt_b_product_details

Every 15 seconds it queries the plex server and if something is playing, displays the cover art.  If not, it's blank.
The script assumes that you know Linux to set the environment up, but its really as simple as running xserve without a window manager and getting everything to start at boot.  
I can't really comment on how secure it all is, but it's ok for an hour of my time.
![IMG_2056](https://github.com/user-attachments/assets/0b669635-4658-4599-8b55-83bd5a78c232)
