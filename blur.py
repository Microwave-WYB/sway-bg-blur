#!/bin/python3
import imp
from xml.dom.expatbuilder import parseFragmentString
from PIL import Image, ImageFilter
from os import system
from os import popen
from os import path
import time

BG_PATH = "/home/wyb/.cache/wallpaper.png"
CACHE_DIR = "/home/wyb/.cache/bg_blur"
if not path.exists(BG_PATH):
    print("[!] Error: No wallpaper found in ~/.cache/wallpaper")
    print("try adding `output \"*\" bg /home/$USER/.cache/wallpaper fill` to your ~/.config/sway/config, and move your wallpaper there")
    exit(1)

focused = False

print("diff " + BG_PATH + " " + CACHE_DIR + "/wallpaper.png")

# check if background is cached
if system("diff " + BG_PATH + " " + CACHE_DIR + "/wallpaper.png") == 0:
    print("[*] Background is cached")
else:
    print("[*] Background is not cached")
        # cache background
    system("cp " + BG_PATH + " " + CACHE_DIR)

    img = Image.open(BG_PATH)
    img = img.filter(ImageFilter.GaussianBlur(radius=50))
    img.save(CACHE_DIR + "/blur.png")

while True:
    # check for focused window
    pid = popen("swaymsg -t get_tree | jq '.. | select(.type?) | select(.focused==true).pid'").read()
    if pid == "null\n"  and focused:
        # undo blur
        #system("swaymsg output '*' background " + CACHE_DIR + "/wallpaper.png fill")
        swaybg_pid = popen("pidof swaybg").read()
        system("swaybg -i " + CACHE_DIR + "/wallpaper.png -m fill &")
        time.sleep(0.1)
        system("kill " + swaybg_pid)
        focused = False
    elif pid != "null\n" and not focused:
        # set blur
        #system("swaymsg output '*' background " + CACHE_DIR + "/blur.png fill")
        swaybg_pid = popen("pidof swaybg").read()
        system("swaybg -i " + CACHE_DIR + "/blur.png -m fill &")
        time.sleep(0.2)
        system("kill " + swaybg_pid)
        focused = True
    else:
        # do nothing
        time.sleep(0.4)
