import math
import time
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread

AU_IN_M = 149597870700  # Astronomical Unit in meters

class TickBombingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EVE Tick Bombing Calculator")
        self.root.geometry("650x650")
        self.root.resizable(False, False)
        
        # Colors
        self.bg_color = "#121212"
        self.frame_color = "#1E1E1E"
        self.text_color = "#FFFFFF"
        self.accent_color = "#4A90E2"
        self.warning_color = "#FF5555"
        self.success_color = "#55FF55"
        self.normal_color = "#4A90E2"
        
        # Try to set the icon
        try:
            self.root.iconbitmap("assets/app_icon.ico")
        except:
            pass  # Ignore if icon not found
        
        self.setup_ui()
        self.running = False
        self.countdown_thread = None
        self.paused = False
        self.pause_time = 0
        
    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        self.root.configure(bg=self.bg_color)
        style.configure('TFrame', background=self.frame_color)
        style.configure('TLabel', background=self.frame_color, foreground=self.text_color)
        style.configure('TButton', background=self.accent_color, foreground=self.text_color)
        style.configure('TEntry', fieldbackground="#2D2D2D", foreground=self.text_color)
        style.configure('Horizontal.TProgressbar', background=self.accent_color)
        style.configure('TLabelframe', background=self.frame_color, foreground=self.text_color)
        style.configure('TLabelframe.Label', background=self.frame_color, foreground=self.accent_color)
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Input Parameters", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Input fields
        ttk.Label(input_frame, text="Target Warp Distance (AU):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.distance_entry = ttk.Entry(input_frame)
        self.distance_entry.grid(row=0, column=1, sticky=tk.EW, pady=2)
        
        ttk.Label(input_frame, text="Target Warp Speed (AU/s):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.warp_speed_entry = ttk.Entry(input_frame)
        self.warp_speed_entry.grid(row=1, column=1, sticky=tk.EW, pady=2)
        
        ttk.Label(input_frame, text="Target Sub Warp Speed (m/s):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.subwarp_speed_entry = ttk.Entry(input_frame)
        self.subwarp_speed_entry.grid(row=2, column=1, sticky=tk.EW, pady=2)
        
        ttk.Label(input_frame, text="Bomb Detonation Time (s):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.detonation_entry = ttk.Entry(input_frame)
        self.detonation_entry.grid(row=3, column=1, sticky=tk.EW, pady=2)
        
        ttk.Label(input_frame, text="Align Alert (seconds before):").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.align_alert_entry = ttk.Entry(input_frame)
        self.align_alert_entry.insert(0, "3")
        self.align_alert_entry.grid(row=4, column=1, sticky=tk.EW, pady=2)
        
        ttk.Label(input_frame, text="Bomb Alert (seconds before):").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.bomb_alert_entry = ttk.Entry(input_frame)
        self.bomb_alert_entry.insert(0, "1")
        self.bomb_alert_entry.grid(row=5, column=1, sticky=tk.EW, pady=2)
        
        # Button row
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.calc_button = ttk.Button(button_frame, text="Calculate", command=self.calculate)
        self.calc_button.pack(side=tk.LEFT, padx=5)
        
        self.start_button = ttk.Button(button_frame, text="Start Timer", command=self.start_countdown, state=tk.DISABLED)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop Timer", command=self.stop_countdown, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Timer display section
        timer_frame = ttk.Frame(main_frame)
        timer_frame.pack(fill=tk.X, pady=(10, 5))
        
        # Digital display frame
        digital_frame = ttk.Frame(timer_frame)
        digital_frame.pack()
        
        self.countdown_var = tk.StringVar(value="00:00:00")
        self.countdown_label = ttk.Label(digital_frame, textvariable=self.countdown_var, 
                                      font=('Helvetica', 24), background=self.frame_color, 
                                      foreground=self.normal_color)
        self.countdown_label.pack()
        
        # Status message
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(timer_frame, textvariable=self.status_var, 
                               font=('Helvetica', 12), background=self.frame_color,
                               foreground=self.text_color)
        status_label.pack(pady=(5, 0))
        
        # Progress bar
        self.progress = ttk.Progressbar(timer_frame, orient='horizontal', length=400, mode='determinate')
        self.progress.pack(pady=(10, 0))
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a text widget for results with better formatting
        self.results_text = tk.Text(results_frame, height=12, bg="#2D2D2D", fg=self.text_color, 
                                  font=('Consolas', 10), padx=10, pady=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.results_text.pack(side="left", fill="both", expand=True)
        
        # Configure text tags for results display
        self.results_text.tag_configure("section_title", foreground="#4A90E2", font=('Helvetica', 10, 'bold'))
        
        # Set default values
        self.distance_entry.insert(0, "1")  # 1 AU
        self.warp_speed_entry.insert(0, "5")
        self.subwarp_speed_entry.insert(0, "200")
        self.detonation_entry.insert(0, "5")
    
    def calculate_time_in_warp(self, max_warp_speed, max_subwarp_speed, warp_dist):
        """
        Calculate the time and distance parameters for a warp in EVE Online.
        
        Args:
            max_warp_speed: Maximum warp speed in AU/s
            max_subwarp_speed: Maximum sub-warp speed in m/s
            warp_dist: Warp distance in meters
            
        Returns:
            Tuple containing various warp timing and distance parameters
        """
        k_accel = max_warp_speed
        k_decel = min(max_warp_speed / 3, 2)
        warp_dropout_speed = min(max_subwarp_speed / 2, 100)
        max_ms_warp_speed = max_warp_speed * AU_IN_M

        # Calculate acceleration time and distance
        accel_time = math.log(max_ms_warp_speed / k_accel) / k_accel
        accel_dist = (max_ms_warp_speed / k_accel) * (1 - math.exp(-k_accel * accel_time))

        # Calculate deceleration time and distance
        decel_time = math.log(max_ms_warp_speed / warp_dropout_speed) / k_decel
        decel_dist = (max_ms_warp_speed / k_decel) * (1 - math.exp(-k_decel * decel_time))

        # Calculate cruise distance and time
        minimum_dist = accel_dist + decel_dist
        cruise_dist = max(0, warp_dist - minimum_dist)
        cruise_time = cruise_dist / max_ms_warp_speed if max_ms_warp_speed > 0 else 0

        total_time = accel_time + cruise_time + decel_time
        
        return total_time, accel_time, cruise_time, decel_time, accel_dist, cruise_dist, decel_dist, k_accel, k_decel, max_ms_warp_speed
    
    def calculate_distance_remaining(self, time_left, k_decel, max_ms_warp_speed, warp_dropout_speed, decel_dist):
        """
        Calculate how much distance will be covered in the remaining time
        
        Args:
            time_left: Time remaining in seconds
            k_decel: Deceleration constant
            max_ms_warp_speed: Maximum warp speed in m/s
            warp_dropout_speed: Speed at warp dropout in m/s
            decel_dist: Total deceleration distance in meters
            
        Returns:
            Distance remaining in meters
        """
        if time_left <= 0:
            return 0
        
        # Check if we're in deceleration phase for the entire remaining time
        if time_left >= math.log(max_ms_warp_speed / warp_dropout_speed) / k_decel:
            return decel_dist  # Shouldn't happen since we're calculating for the end of warp
        
        # Distance covered during deceleration phase
        distance = (max_ms_warp_speed / k_decel) * (1 - math.exp(-k_decel * time_left))
        return distance
    
    def calculate(self):
        """
        Calculate all warp parameters and bomb launch timing based on user inputs
        """
        try:
            # Get input values
            distance_au = float(self.distance_entry.get())
            distance_m = distance_au * AU_IN_M
            warp_speed = float(self.warp_speed_entry.get())
            subwarp_speed = float(self.subwarp_speed_entry.get())
            detonation_time = float(self.detonation_entry.get())
            
            # Validate inputs
            if distance_au <= 0 or warp_speed <= 0 or subwarp_speed <= 0 or detonation_time <= 0:
                messagebox.showerror("Input Error", "All values must be greater than zero.")
                return
            
            # Calculate warp parameters
            (total_time, accel_time, cruise_time, decel_time, 
             accel_dist, cruise_dist, decel_dist, 
             k_accel, k_decel, max_ms_warp_speed) = self.calculate_time_in_warp(warp_speed, subwarp_speed, distance_m)
            
            warp_dropout_speed = min(subwarp_speed / 2, 100)
            
            # Calculate distance that will be covered during the detonation time
            distance_during_detonation = self.calculate_distance_remaining(
                detonation_time, k_decel, max_ms_warp_speed, warp_dropout_speed, decel_dist)
            
            remaining_distance_at_launch = distance_during_detonation
            remaining_distance_au = remaining_distance_at_launch / AU_IN_M
            
            # Calculate when to launch (time when remaining distance equals distance covered in detonation time)
            launch_time = total_time - detonation_time
            
            # Calculate current speed at launch time
            if launch_time <= accel_time:
                current_speed = k_accel * AU_IN_M * math.exp(k_accel * launch_time)
            elif launch_time <= (accel_time + cruise_time):
                current_speed = warp_speed * AU_IN_M  # Max speed
            else:
                time_in_decel = launch_time - accel_time - cruise_time
                current_speed = warp_speed * AU_IN_M * math.exp(-k_decel * time_in_decel)
            
            # Format results in a clean, readable way
            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete(1.0, tk.END)
            
            # Add colored sections
            self.add_result_section("TARGET INFORMATION", [
                f"Warp Distance: {distance_au:.2f} AU ({distance_m/1000:,.0f} km)",
                f"Warp Speed: {warp_speed} AU/s",
                f"Sub Warp Speed: {subwarp_speed} m/s",
                f"Bomb Detonation Time: {detonation_time} seconds"
            ])
            
            self.add_result_section("WARP TIME BREAKDOWN", [
                f"Acceleration Phase: {accel_time:.2f} seconds (distance: {accel_dist/1000:,.0f} km)",
                f"Cruise Phase: {cruise_time:.2f} seconds (distance: {cruise_dist/1000:,.0f} km)",
                f"Deceleration Phase: {decel_time:.2f} seconds (distance: {decel_dist/1000:,.0f} km)",
                f"\nTotal Warp Time: {total_time:.2f} seconds"
            ])
            
            self.add_result_section("BOMB LAUNCH TIMING", [
                f"Launch Bomb at: {launch_time:.2f} seconds after warp start",
                f"Which is {detonation_time:.2f} seconds before landing",
                f"\nAt launch time:",
                f"- Distance remaining: {remaining_distance_au:.4f} AU ({remaining_distance_at_launch/1000:,.0f} km)",
                f"- Current speed: {current_speed:,.0f} m/s ({current_speed/AU_IN_M:.2f} AU/s)",
                f"- This distance will be covered in exactly {detonation_time:.2f} seconds"
            ])
            
            self.results_text.config(state=tk.DISABLED)
            
            # Store values for countdown
            self.launch_time = launch_time
            self.total_time = total_time
            self.detonation_time = detonation_time
            
            # Enable timer controls
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            
            # Reset progress bar
            self.progress['maximum'] = total_time
            self.progress['value'] = 0
            
        except ValueError as e:
            messagebox.showerror("Input Error", "Please enter valid numbers in all fields.")
    
    def add_result_section(self, title, items):
        """
        Add a formatted section to the results display
        
        Args:
            title: Section title
            items: List of text items to display in the section
        """
        self.results_text.insert(tk.END, f"{title}\n", "section_title")
        for item in items:
            self.results_text.insert(tk.END, f"  {item}\n")
        self.results_text.insert(tk.END, "\n")
    
    def start_countdown(self):
        """
        Start the countdown timer
        """
        if not hasattr(self, 'launch_time'):
            messagebox.showwarning("Warning", "Please calculate first before starting countdown.")
            return
        
        if self.paused:
            remaining_time = self.pause_time
        else:
            remaining_time = self.launch_time
        
        self.running = True
        self.paused = False
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Counting down...")
        self.countdown_label.config(foreground=self.normal_color)
        
        align_alert = float(self.align_alert_entry.get())
        bomb_alert = float(self.bomb_alert_entry.get())
        
        self.countdown_thread = Thread(target=self.run_countdown, args=(remaining_time, align_alert, bomb_alert))
        self.countdown_thread.daemon = True  # Allow app to exit even if thread is running
        self.countdown_thread.start()
    
    def stop_countdown(self):
        """
        Stop the countdown timer
        """
        self.running = False
        self.paused = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.countdown_var.set("00:00:00")
        self.status_var.set("Ready")
        self.progress['value'] = 0
        self.countdown_label.config(foreground=self.normal_color)
    
    def run_countdown(self, remaining_time, align_alert, bomb_alert):
        """
        Run the countdown timer in a separate thread
        
        Args:
            remaining_time: Time remaining in seconds
            align_alert: Time in seconds before launch to show align alert
            bomb_alert: Time in seconds before launch to show bomb alert
        """
        start_time = time.time() - (self.launch_time - remaining_time)
        align_alert_triggered = False
        bomb_alert_triggered = False
        
        while self.running and remaining_time > 0:
            current_time = time.time()
            elapsed = current_time - start_time
            remaining_time = max(0, self.launch_time - elapsed)
            self.pause_time = remaining_time
            
            # Update progress
            progress_value = min(elapsed, self.total_time)
            self.root.after(0, lambda v=progress_value: self.progress.configure(value=v))
            
            # Update display
            hours, remainder = divmod(remaining_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
            self.root.after(0, lambda s=time_str: self.countdown_var.set(s))
            
            # Check for alerts
            if not align_alert_triggered and remaining_time <= align_alert:
                self.root.after(0, self.trigger_alert, "ALIGN NOW!", self.warning_color)
                align_alert_triggered = True
            
            if not bomb_alert_triggered and remaining_time <= bomb_alert:
                self.root.after(0, self.trigger_alert, "LAUNCH BOMB!", self.success_color)
                bomb_alert_triggered = True
            
            time.sleep(0.05)
        
        if remaining_time <= 0 and self.running:
            self.root.after(0, self.trigger_alert, "TARGET LANDING!", self.warning_color)
            self.root.after(0, self.stop_countdown)
    
    def trigger_alert(self, message, color):
        """
        Trigger a visual alert on the UI
        
        Args:
            message: Message to display
            color: Color to use for the alert
        """
        self.status_var.set(message)
        self.countdown_label.config(foreground=color)

if __name__ == "__main__":
    root = tk.Tk()
    app = TickBombingApp(root)
    root.mainloop()
