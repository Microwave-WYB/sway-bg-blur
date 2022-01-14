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

"""
    img = Image.open(BG_PATH)
    img = img.filter(ImageFilter.GaussianBlur(radius=50))
    img.save(CACHE_DIR + "/blur.png")

while True:
    # check for focused window
    pid = popen("swaymsg -t get_tree | jq '.. | select(.type?) | select(.focused==true).pid'").read()
    if pid == "null\n" and focused:
        # sleep for 2 seconds to avoid confusion
        time.sleep(2)
    if pid == "null\n"  and focused:
        # undo blur
        print("Unsetting blur")
        #system("swaymsg output '*' background " + CACHE_DIR + "/wallpaper.png fill")
        swaybg_pid = popen("pidof swaybg").read()
        system("swaybg -i " + CACHE_DIR + "/wallpaper.png -m fill &")
        time.sleep(0.5)
        system("kill " + swaybg_pid)
        focused = False
    elif pid != "null\n" and not focused:
        # set blur
        print("Setting blur")
        #system("swaymsg output '*' background " + CACHE_DIR + "/blur.png fill")
        swaybg_pid = popen("pidof swaybg").read()

        time.sleep(0.5)
        system("kill " + swaybg_pid)
        focused = True
    else:
        # do nothing
        time.sleep(0.3)
"""
def gen_blur():
    print("[*] generating blurred backgrounds")
    global BG_PATH
    global CACHE_DIR
    # generate blurred background files
    system("cp " + BG_PATH + " " + CACHE_DIR)
    img = Image.open(BG_PATH)
    for i in range(6):
        blur = img.filter(ImageFilter.GaussianBlur(radius=10 * (i)))
        blur.save(CACHE_DIR + "/blur" + str(i) + ".png")
    print("[*] blurred backgrounds ready")

def prep_set_blur():
    global CACHE_DIR
    print("[*] preparing blur")
    # create 5 swaybg processes
    for i in range(5):
        system("swaybg -i " + CACHE_DIR + "/blur" + str(i+1) + ".png -m fill &")
        time.sleep(0.05)
    print("[*] blurred background prepared")

def prep_unset_blur():
    global CACHE_DIR
    print("[*] preparing unblur")
    # create 5 swaybg processes
    for i in range(5):
        system("swaybg -i " + CACHE_DIR + "/blur" + str(5-i-1) + ".png -m fill &")
        time.sleep(0.05)
    print("[*] unblurred background prepared")

def change_blur():
    print("[*] applying effects")
    # kill 5 swaybg processes from lower to higher pid
    pids = popen("pidof swaybg").read().split(" ")
    for i in range(5):
        system("kill " + pids[5-i])
        print("killed process", pids[5-i])
        time.sleep(0.06)
    print("[*] effects applied")

def main():
    global BG_PATH
    global CACHE_DIR

    # refresh background
    system("pkill swaybg")
    system("swaybg -i " + CACHE_DIR + "/wallpaper.png -m fill &")
    if not path.exists(BG_PATH):
        print("[!] Error: No wallpaper found in ~/.cache/wallpaper")
        print("try adding `output \"*\" bg /home/$USER/.cache/wallpaper fill` to your ~/.config/sway/config, and move your wallpaper there")
        exit(1)
    if False: # TODO: Add cache check
        # cache background
        system("cp " + BG_PATH + " " + CACHE_DIR)
    gen_blur()
    blurred = False
    prep_set_blur()
    while True:
        focused_window = popen("swaymsg -t get_tree | jq '.. | select(.type?) | select(.focused==true).pid'").read()
        if focused_window != "null\n" and not blurred:
            change_blur()
            prep_unset_blur()
            blurred = True
        elif focused_window == "null\n" and blurred:
            change_blur()
            prep_set_blur()
            blurred = False
        else:
            pass
        time.sleep(1)
if __name__ == "__main__":
    main()
