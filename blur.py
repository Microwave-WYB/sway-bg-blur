#!/bin/python3
import imp
from PIL import Image, ImageFilter
from os import system
from os import popen
from os import path
import time

BG_PATH = path.expanduser("~") + "/.cache/wallpaper.png"
CACHE_DIR = path.expanduser("~") + "/.cache/bg_blur"

# Generate blurred background
def gen_blur():
    print("[*] generating blurred backgrounds")
    global BG_PATH
    global CACHE_DIR
    system("cp " + BG_PATH + " " + CACHE_DIR)
    img = Image.open(BG_PATH)
    for i in range(6):
        blur = img.filter(ImageFilter.GaussianBlur(radius=10 * (i)))
        blur.save(CACHE_DIR + "/blur" + str(i) + ".png")
    print("[*] blurred backgrounds ready")

# Prepare all swaybg processes to set the blurred background
def prep_set_blur():
    global CACHE_DIR
    print("[*] preparing blur")
    # create 5 swaybg processes
    for i in range(5):
        system("swaybg -i " + CACHE_DIR + "/blur" + str(i+1) + ".png -m fill &")
        time.sleep(0.05)
    print("[*] blurred background prepared")

# Prepare all swaybg processes to unset the blurred background
def prep_unset_blur():
    global CACHE_DIR
    print("[*] preparing unblur")
    # create 5 swaybg processes
    for i in range(5):
        system("swaybg -i " + CACHE_DIR + "/blur" + str(5-i-1) + ".png -m fill &")
        time.sleep(0.05)
    print("[*] unblurred background prepared")

# Apply changes to swaybg processes
def apply_change():
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
        print("[!] Error: No wallpaper found in", BG_PATH)
        print("try adding `output \"*\" bg /home/$USER/.cache/wallpaper.jpg fill` to your ~/.config/sway/config, and move your wallpaper there")
        exit(1)
    if popen("diff " + BG_PATH + " " + CACHE_DIR + "/wallpaper.png").read() != "":
        # cache background
        system("cp " + BG_PATH + " " + CACHE_DIR)
        # generate blurred background
        gen_blur()
    # keep track of blurred state
    blurred = False
    # prepare to set blurred background
    prep_set_blur()
    # main loop
    while True:
        # check if a window is focused
        focused_window = popen("swaymsg -t get_tree | jq '.. | select(.type?) | select(.focused==true).pid'").read()
        if focused_window == "null\n" and blurred:
            # wait a moment maybe a window will be focused in a sec
            time.sleep(0.5)
        focused_window = popen("swaymsg -t get_tree | jq '.. | select(.type?) | select(.focused==true).pid'").read()
        # if a window is focused and blurred is false, apply blur
        if focused_window != "null\n" and not blurred:
            apply_change()
            # prepare to unset blurred background
            prep_unset_blur()
            blurred = True
        # if a window is not focused and blurred is true, unblur
        elif focused_window == "null\n" and blurred:
            apply_change()
            # prepare to set blurred background
            prep_set_blur()
            blurred = False
        else:
            pass
        time.sleep(0.5)

if __name__ == "__main__":
    main()
