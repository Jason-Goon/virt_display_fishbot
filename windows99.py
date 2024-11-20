# windows99.py
import subprocess
import os
import time

class VirtualDisplayManager:
    def __init__(self, display_id=99):
        self.display_id = display_id
        self.display_var = f":{self.display_id}"
        self.xephyr_process = None
        self.wm_process = None
        self.alacritty_process = None

    def start_virtual_display(self):
        self.xephyr_process = subprocess.Popen(
            ["Xephyr", self.display_var, "-screen", "1024x768"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        time.sleep(2) 
        print(f"Virtual display started on DISPLAY {self.display_var}")

    def start_window_manager(self):
        # window manager (DWM)
        wm_env = os.environ.copy()
        wm_env["DISPLAY"] = self.display_var
        self.wm_process = subprocess.Popen(
            ["dwm"],
            env=wm_env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        print("Window manager (DWM) started in virtual display.")
        time.sleep(2)  

    def launch_alacritty(self):
        alacritty_env = os.environ.copy()
        alacritty_env["DISPLAY"] = self.display_var
        self.alacritty_process = subprocess.Popen(
            ["alacritty"],
            env=alacritty_env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        print("Alacritty terminal launched in virtual display.")
        time.sleep(2)

    def activate_alacritty_and_send_keystring(self, keystring):
        print("Activating Alacritty window and sending input...")
        xdotool_env = {"DISPLAY": self.display_var}
        window_id_output = subprocess.check_output(
            ["xdotool", "search", "--onlyvisible", "--class", "Alacritty"],
            env=xdotool_env
        )
        window_id = window_id_output.strip().decode('utf-8')
        print(f"Alacritty window ID: {window_id}")

        subprocess.run(["xdotool", "windowactivate", "--sync", window_id], env=xdotool_env)
        subprocess.run(["xdotool", "type", "--delay", "100", keystring], env=xdotool_env)
        subprocess.run(["xdotool", "key", "Return"], env=xdotool_env)
        print(f"Sent keystring '{keystring}' to Alacritty.")

    def stop_virtual_display(self):
        if self.alacritty_process:
            self.alacritty_process.terminate()
            print("Alacritty process terminated.")
        if self.wm_process:
            self.wm_process.terminate()
            print("Window manager (DWM) process terminated.")
        if self.xephyr_process:
            self.xephyr_process.terminate()
            print("Xephyr process terminated.")

    def __enter__(self):
        self.start_virtual_display()
        self.start_window_manager()
        self.launch_alacritty()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop_virtual_display()



if __name__ == "__main__":
    with VirtualDisplayManager(display_id=99) as vdm:
        vdm.activate_alacritty_and_send_keystring("steam")
        input("Press Enter to terminate the virtual display.")
