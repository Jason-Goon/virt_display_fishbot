# main.py
import os
os.environ["DISPLAY"] = ":99"
import cv2 as cv
import numpy as np
import pyautogui
import time

screenshot_counter = 0 

def cast_fishing():
    print("Casting fishing line...")
    pyautogui.press('1')  
    time.sleep(1.5)  

def take_screenshot():
    global screenshot_counter
    filename = f"screenshot_{screenshot_counter}.png"
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    screenshot_counter += 1
    print(f"Screenshot saved as {filename}")
    return filename

def find_bobber(screenshot_path, target_path="fishing_target.png", threshold=0.6):
    screenshot = cv.imread(screenshot_path)
    target = cv.imread(target_path)

    if screenshot is None or target is None:
        print("Error loading images.")
        return None

    result = cv.matchTemplate(screenshot, target, cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

    if max_val >= threshold:
        print(f"Bobber found at coordinates: ({max_loc[0]}, {max_loc[1]})")
        return max_loc  
    else:
        print("Bobber not found.")
        return None

def calculate_rgb_average(screenshot_path, bobber_x, bobber_y):
    screenshot = cv.imread(screenshot_path)
    box_size = 50
    half_box = box_size // 2
    start_x = max(bobber_x - half_box, 0)
    start_y = max(bobber_y - half_box, 0)
    end_x = min(bobber_x + half_box, screenshot.shape[1])
    end_y = min(bobber_y + half_box, screenshot.shape[0])
    box_area = screenshot[start_y:end_y, start_x:end_x]
    avg_rgb = box_area.mean(axis=(0, 1))
    avg_rgb = avg_rgb[::-1]  
    print(f"Average RGB in 50x50 box around the bobber: {avg_rgb}")
    return avg_rgb

def perform_shift_click(x, y):
    pyautogui.keyDown('shift')
    pyautogui.rightClick(x, y)
    pyautogui.keyUp('shift')
    print("Performed Shift + Right Click at the bobber location.")

def clean_up_screenshots():
    for file in os.listdir():
        if file.startswith("screenshot_") and file.endswith(".png"):
            os.remove(file)
    print("Temporary screenshots cleaned up.")


def fishing_loop():
    clean_up_screenshots()  
    while True:
        cast_fishing()
        screenshot_path = take_screenshot()
        bobber_location = find_bobber(screenshot_path, "fishing_target.png")
        if bobber_location is None:
            print("Bobber not found, retrying...")
            pyautogui.press('space') 
            time.sleep(1.5)  
            continue  

        initial_avg = calculate_rgb_average(screenshot_path, bobber_x=bobber_location[0], bobber_y=bobber_location[1])
        splash_detected = False
        start_time = time.time()
        
        while not splash_detected and (time.time() - start_time) < 30:
            screenshot_path = take_screenshot()
            current_avg = calculate_rgb_average(screenshot_path, bobber_x=bobber_location[0], bobber_y=bobber_location[1])

            
            if np.linalg.norm(current_avg - initial_avg) > 20:  # adjust threshold if needed
                print("Splash detected!")
                perform_shift_click(bobber_location[0], bobber_location[1])
                splash_detected = True
                time.sleep(3)  

        if not splash_detected:
            print("No splash detected within 30 seconds. Restarting the loop.")
            time.sleep(1.5)  
            continue 
        
        clean_up_screenshots()

if __name__ == "__main__":
    fishing_loop()
