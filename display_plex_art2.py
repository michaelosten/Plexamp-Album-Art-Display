#!/usr/bin/python3

import requests
import xml.etree.ElementTree as ET
import time
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import threading

# Plex token and user URL
PLEX_TOKEN = 'Your Plex Token'
PLEX_USER_URL = 'https://plex.tv/api/resources?includeHttps=1&includeRelay=1'
PLEX_SERVER_BASE_URL = None

# Temporary cover art file
COVER_ART_FILE = '/tmp/cover_art.jpg'

# Flag to stop the thread
stop_thread = False

def start_x_server():
    if not os.environ.get('DISPLAY'):
        print("Starting X server...")
        try:
            subprocess.run(['startx'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error starting X server: {e}")
            return False
        except FileNotFoundError:
            print("startx command not found. Make sure X server is installed.")
            return False
        except Exception as e:
            print(f"Unexpected error starting X server: {e}")
            return False
        
        time.sleep(5)
        os.environ['DISPLAY'] = ':0'
        print("X server started and DISPLAY set to :0")
    return True

def get_plex_server_public_address():
    headers = {
        'Accept': 'application/xml',
        'X-Plex-Token': PLEX_TOKEN
    }
    try:
        response = requests.get(PLEX_USER_URL, headers=headers)
        response.raise_for_status()
        print("Response text from Plex.tv API:", response.text)
        
        root = ET.fromstring(response.content)
        for device in root.findall('.//Device'):
            provides = device.get('provides')
            if provides == 'server':
                for connection in device.findall('.//Connection'):
                    if connection.get('protocol') == 'https' and connection.get('local') == '0':
                        return connection.get('uri')
        return None
    except requests.exceptions.RequestException as e:
        print(f"Failed to get Plex server public address: {e}")
        return None
    except ET.ParseError as e:
        print(f"Failed to parse XML response: {e}")
        print("Response text:", response.text)
        return None

def get_currently_playing_plex():
    headers = {
        'Accept': 'application/json',
        'X-Plex-Token': PLEX_TOKEN
    }
    try:
        response = requests.get(f'{PLEX_SERVER_BASE_URL}/status/sessions', headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get('MediaContainer', {}).get('Metadata', None)
    except requests.exceptions.RequestException as e:
        print(f"Failed to get currently playing from Plex: {e}")
        return None

def fetch_and_display_cover_art(metadata):
    if not metadata:
        print("Nothing Playing Currently")
        display_message("Nothing Playing Currently")
        return
    
    cover_art_url = None
    for item in metadata:
        if item['type'] == 'track':
            cover_art_url = f"{PLEX_SERVER_BASE_URL}{item['thumb']}?X-Plex-Token={PLEX_TOKEN}"
            break

    if cover_art_url:
        print(f"Cover art URL: {cover_art_url}")
        response = requests.get(cover_art_url)
        with open(COVER_ART_FILE, 'wb') as f:
            f.write(response.content)
        
        display_with_feh(COVER_ART_FILE)
    else:
        print("No cover art found")
        display_message("No cover art found")

def display_with_feh(image_path):
    print(f"Attempting to display image with feh: {image_path}")
    try:
        subprocess.Popen(['feh', '-F', '-Z', image_path])
    except Exception as e:
        print(f"Can't Display: {e}")

def display_message(message):
    print(message)
    if not os.environ.get('DISPLAY'):
        return

    img = Image.new('RGB', (800, 600), color='black')
    d = ImageDraw.Draw(img)
    fnt = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 40)
    w, h = d.textsize(message, font=fnt)
    d.text(((800-w)/2, (600-h)/2), message, font=fnt, fill=(255, 255, 255))

    message_image_path = '/tmp/message.jpg'
    img.save(message_image_path)
    
    display_with_feh(message_image_path)

def check_currently_playing():
    global stop_thread
    global PLEX_SERVER_BASE_URL
    current_cover_art_url = None
    while not stop_thread:
        print(f"{datetime.now()} - Checking for currently playing media...")
        metadata = get_currently_playing_plex()
        new_cover_art_url = None
        if metadata:
            for item in metadata:
                if item['type'] == 'track':
                    new_cover_art_url = f"{PLEX_SERVER_BASE_URL}{item['thumb']}?X-Plex-Token={PLEX_TOKEN}"
                    break
            
            if new_cover_art_url != current_cover_art_url:
                print(f"{datetime.now()} - New cover art URL detected: {new_cover_art_url}")
                current_cover_art_url = new_cover_art_url
                fetch_and_display_cover_art(metadata)
            else:
                print(f"{datetime.now()} - Cover art URL has not changed.")
        else:
            if current_cover_art_url:
                print(f"{datetime.now()} - Nothing is currently playing.")
                current_cover_art_url = None
                display_message("Nothing Playing Currently")
        
        for remaining in range(15, 0, -1):
            if stop_thread:
                break
            print(f"{datetime.now()} - Next fetch in {remaining} seconds...", end='\r')
            time.sleep(1)

def main():
    global PLEX_SERVER_BASE_URL
    PLEX_SERVER_BASE_URL = get_plex_server_public_address()
    if not PLEX_SERVER_BASE_URL:
        print("Could not get Plex server public address.")
        return
    
    if not start_x_server():
        print("Unable to start X server. Exiting.")
        return
    
    # Start the thread for checking currently playing media
    thread = threading.Thread(target=check_currently_playing)
    thread.start()

    try:
        while True:
            time.sleep(1)  # Main thread can be used for other tasks or simply sleep
    except KeyboardInterrupt:
        global stop_thread
        stop_thread = True
        thread.join()  # Wait for the thread to finish before exiting

if __name__ == "__main__":
    main()

