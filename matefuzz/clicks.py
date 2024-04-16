import pyautogui
import time
import random
import sys
import os
from multiprocessing import Process
import math
import subprocess
import chardet

# def task():
#     os.system("mate-calc")

# process = Process(target=task)
# process.start()

def sfc32(a, b, c, d):
    a &= 0xFFFFFFFF
    b &= 0xFFFFFFFF
    c &= 0xFFFFFFFF
    d &= 0xFFFFFFFF
    def rng():
        nonlocal a, b, c, d
        t = (a + b) & 0xFFFFFFFF
        a = b ^ (b >> 9)
        b = (c + (c << 3)) & 0xFFFFFFFF
        c = ((c << 21) | (c >> 11)) & 0xFFFFFFFF
        d = (d + 1) & 0xFFFFFFFF
        t = (t + d) & 0xFFFFFFFF
        c = (c + t) & 0xFFFFFFFF
        return t / 4294967296
    return rng

def xfnv1a(string):
    h = 2166136261
    for char in string:
        h ^= ord(char)
        h = (h * 16777619) & 0xFFFFFFFF
    def seed_scramble():
        nonlocal h
        h += h << 13
        h ^= h >> 7
        h += h << 3
        h ^= h >> 17
        h += h << 5
        return h & 0xFFFFFFFF
    return seed_scramble

def generateRandomNumber(seedstring):
    num = xfnv1a(seedstring)
    return sfc32(num(), num(), num(), num())

def getWindowCoords():
    window_list = [] #start x, start y, width, height
    window_command = "xwininfo -id $(xdotool getactivewindow)"
    window_info = subprocess.check_output(window_command, shell=True)
    window_info = window_info.decode('utf-8')
    info = window_info.split("\n")
    for res in info:
        temp = res.split(":")
        if(len(temp)>1):
            match temp[0].strip():
                case "Absolute upper-left X":
                    window_list.append(int(temp[1].strip()))
                case "Absolute upper-left Y":
                    window_list.append(int(temp[1].strip()))
                case "Width":
                    window_list.append(int(temp[1].strip()))
                case "Height":
                    window_list.append(int(temp[1].strip()))
    return window_list

def getScreenResolution():
    resolution_command = "xdpyinfo | grep dimensions | awk '{ print $2 }'"
    resol_value = subprocess.check_output(resolution_command, shell=True)
    resol_value = resol_value.decode('utf-8')
    resol_value_split = resol_value.split('x')
    return int(resol_value_split[0])

time.sleep(3)

# window_coords = getWindowCoords()
# start_x = window_coords[0]
# start_y = window_coords[1]
# width = window_coords[2]
# height = window_coords[3]

start_x = 50
start_y = 114
width = 432
height = 245

y_padding = 40

seed = ""
with open('./out/.cur_input', 'r', encoding='iso-8859-1') as f:
	seed = f.read()

random_number = generateRandomNumber(seed)

for i in range(10):
    val = random_number()
    x_val = (start_x - 10) + width * val
    y_val = (start_y + y_padding - 10) + (height - y_padding) * val
    pyautogui.click(math.floor(x_val),math.floor(y_val))

time.sleep(1)

pyautogui.keyDown('ctrlleft')
pyautogui.press('q')
pyautogui.keyUp('ctrlleft')