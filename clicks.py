import pyautogui
import time
import random
import sys
import os
from multiprocessing import Process
import math
import subprocess
import chardet

seed_path = './out/.cur_input'
start_x = 0
start_y = 0
width = 0
height = 0

if len(sys.argv) > 2 and sys.argv[1] != None and sys.argv[2] != None:
    target_program = sys.argv[1]
    seed_path = sys.argv[2]

    def task():
        os.system(target_program)

    process = Process(target=task)
    process.start()

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

def execute_operation(operator, operands):
    if operator == 'CLICK':
        # Use the operands as a percent of the screen to click in order to stay within the window
        x_percent = operands[0]/256.0
        y_percent = operands[1]/256.0
        x_coord = start_x + x_percent * width
        y_coord = start_y + y_percent * height 
        pyautogui.click(math.floor(x_coord),math.floor(y_coord))
        result = f'Clicked at: {x_coord}, {y_coord}'
    else:
        result = None

    print(f'Executing {operator} with operands {operands}: {result}')
    return result


time.sleep(3)

window_coords = getWindowCoords()
start_x = window_coords[0]
start_y = window_coords[1]
width = window_coords[2]
height = window_coords[3]

print("Coordinates || StartX: " + str(start_x) + " || StartY: " + str(start_y) + " || Width: " + str(width) + " || Height: " + str(height))

y_padding = 40

operators = {
    0x01: ('CLICK', 2),  # Operator + Operand Count
    0x02: ('MOVETO', 0)
}

with open(seed_path, 'rb') as f:
	data = f.read()

# Add a sleep when running in Qemu mode because the target program takes a lot of time to open
# time.sleep(25)

i = 0
while i < len(data):
    byte = data[i]
    
    # Loop through the bytes until we find a valid operator code
    if byte in operators:
        operator, operand_count = operators[byte]
        operands = []
        
        # Iterate through the operands for the operation we hit
        for _ in range(operand_count):
            i += 1
            if i < len(data):
                operands.append(data[i])
            else:
                raise ValueError("File ended unexpectedly while reading operands")
        
        execute_operation(operator, operands)
    else:
        print(f'Ignoring unknown byte: {byte}')

    i += 1


time.sleep(1)

pyautogui.keyDown('ctrlleft')
pyautogui.press('q')
pyautogui.keyUp('ctrlleft')
