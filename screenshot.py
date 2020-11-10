#!C:\Users\polarice\anaconda3\python

#Load libraries
import cv2
import numpy as np
import pyautogui
from PIL import Image
import pytesseract
import sys
import time
import win32con
import win32gui
from datetime import datetime

#Function to return list of windows
def windowEnumerationHandler(hwnd, windows):
    windows.append((hwnd, win32gui.GetWindowText(hwnd)))

#Function to return grayscale array from screenshot    
def img_shot():
    
     #Take a screenshot
     img = np.array(pyautogui.screenshot())
        
     #Make cv2 images
     color_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
     gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
     
     return color_img, gray_img
    
#Define constants
check_val = 194
windows = []
click_coords = [102, 453]
check_coords = [500, 10, 50]
crop_coords =[25, 985, 0, 1250]
cryo_coords = [425, 540, 10, 200]
temp_coords = [445, 500, 700, 800]
status_coords = [150, 265, 10, 200]
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\polarice\AppData\Local\Tesseract-OCR\tesseract.exe'

#Get list of windows
win32gui.EnumWindows(windowEnumerationHandler, windows)

#Loop through windows
window_status = 1
for window in windows:

    #Check to see if there is window for hyperpolarizer control client
    if "Control Client" in window[1]:
    
        #Make sure window is full screen and in the foreground
        win32gui.ShowWindow(window[0], win32con.SW_SHOWNORMAL)
        win32gui.ShowWindow(window[0], win32con.SW_MAXIMIZE)
        win32gui.SetForegroundWindow(window[0])
        time.sleep(0.2)
        
        #Get screenshot
        img_color, img_gray = img_shot()

        #Make sure window is how we expect
        cryo_img = Image.fromarray(img_gray[cryo_coords[0]:cryo_coords[1], cryo_coords[2]:cryo_coords[3]])
        cryo_txt = pytesseract.image_to_string(cryo_img).split()
        if "Cryo" in cryo_txt == False:
            break
        
        #Click status tab if needed
        if np.all(img_gray[check_coords[0], check_coords[1]:check_coords[2]] == check_val) == False:

            #Click to make sure we have the correct tab
            pyautogui.click(x=click_coords[0], y=click_coords[1])
            
            #Take a screenshot
            img_color, img_gray = img_shot()
        
        #Stop checking
        window_status = 0
        break

#Stop if window couldn't be found       
if window_status == 1:
    print('ERROR: Cannot find a Control Window')
    sys.exit()

#Get images for temperature and status
img_temp = img_gray[temp_coords[0]:temp_coords[1],
                    temp_coords[2]:temp_coords[3]]
img_status = img_gray[status_coords[0]:status_coords[1],
                      status_coords[2]:status_coords[3]]
                    
#Run OCR to extract status 
status_str = pytesseract.image_to_string(Image.fromarray(img_status)).split()

#Process the image a bit
img_temp = cv2.resize(img_temp, (0, 0), fx = 2, fy = 2)

#Run OCR and see if it works
temp_str = pytesseract.image_to_string(img_temp, config="--psm 12 -c tessedit_char_whitelist=0123456789.K").strip().replace('K', '')

#See if thresholding helps
if len(temp_str) == 0:
    _, img_thr = cv2.threshold(cv2.bitwise_not(img_temp), 70, 255, cv2.THRESH_BINARY)
    temp_str = pytesseract.image_to_string(img_thr, config="--psm 12 -c tessedit_char_whitelist=0123456789.K").strip().replace('K', '')

#Place decimal play if we don't have one. A real hack but seems to work for now
if '.' not in temp_str and len(temp_str) >= 2:
    temp_str = temp_str[0] + '.' + temp_str[1::]
temp = float(temp_str)

#Make variable for status
if "Regen" in status_str:
    status = "Regen"
elif "Monitor" in status_str:
    status = "Ready"
else:
    status = "Other"

#Prep for file outpout
out_time = datetime.now()
img_time = out_time.strftime('%Y-%m-%d-%H-%M-%S')
out_dir = r'C:\Users\polarice\Documents\Github\wustl-spinlab-status'
out_path = r'%s\shots\%s.png'%(out_dir, img_time)

#Save color image
color_crop = img_color[crop_coords[0]:crop_coords[1], crop_coords[2]:crop_coords[3]]
cv2.imwrite(r'%s\assets\current.png'%(out_dir), color_crop)

#Append current status to file
temp_time = out_time.strftime('%Y-%m-%d %H:%M:%S')
with open(r'%s\temp_data.csv'%(out_dir), "a") as temp_file:
    temp_file.write("%s,%2.5f,%s\n"%(out_time, temp, status))