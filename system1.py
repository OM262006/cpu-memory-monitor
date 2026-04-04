import psutil
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
from collections import deque
import numpy as np
from datetime import datetime
import platform
import os

class GamingSystemMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Gaming System Monitor - FPS Optimizer")
        self.root.geometry("1200x700")
        self.root.configure(bg='#1a1a2e')
        
        # Variables for data storage
        self.cpu_history = deque(maxlen=50)
        self.memory_history = deque(maxlen=50)
        self.disk_history = deque(maxlen=50)
        self.temp_history = deque(maxlen=50)
        self.fps_history = deque(maxlen=50)
        
        # Monitoring flag
        self.monitoring = True
        
        # Setup UI
        self.setup_ui()
        
        # Start monitoring
        self.update_stats()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        # Create main container
        main_container = tk.Frame(self.root, bg='#1a1a2e')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for gauges
        left_panel = tk.Frame(main_container, bg='#16213e', relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Right panel for graphs
        right_panel = tk.Frame(main_container, bg='#16213e', relief=tk.RAISED, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Title
        title = tk.Label(left_panel, text="🎮 GAMING SYSTEM MONITOR", 
                        font=('Arial', 16, 'bold'), bg='#16213e', fg='#e94560')
        title.pack(pady=10)
        
        # FPS Counter (User input for manual FPS)
        fps_frame = tk.Frame(left_panel, bg='#16213e')
        fps_frame.pack(pady=10)
        tk.Label(fps_frame, text="Current Game FPS:", font=('Arial', 10), 
                bg='#16213e', fg='white').pack(side=tk.LEFT, padx=5)
        self.fps_entry = tk.Entry(fps_frame, width=10, font=('Arial', 12))
        self.fps_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(fps_frame, text="Update", command=self.update_fps, 
                 bg='#e94560', fg='white', font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        
        # Create gauge displays
        self.create_gauge(left_panel, "CPU Usage", 0, '#00ff88')
        self.create_gauge(left_panel, "Memory Usage", 1, '#ffa500')
        self.create_gauge(left_panel, "Disk Usage", 2, '#ff4444')
        self.create_gauge(left_panel, "CPU Temperature", 3, '#00b4d8')
        
        # System info frame
        info_frame = tk.Frame(left_panel, bg='#0f3460', relief=tk.GROOVE, bd=2)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(info_frame, text="System Information", font=('Arial', 12, 'bold'),
                bg='#0f3460', fg='#e94560').pack(pady=5)
        
        self.system_info = tk.Label(info_frame, text="", font=('Arial', 9),
                                   bg='#0f3460', fg='white', justify=tk.LEFT)
        self.system_info.pack(pady=5)
        
        # Gaming tips frame
        tips_frame = tk.Frame(left_panel, bg='#0f3460', relief=tk.GROOVE, bd=2)
        tips_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(tips_frame, text="💡 Gaming Optimization Tips", font=('Arial', 12, 'bold'),
                bg='#0f3460', fg='#e94560').pack(pady=5)
        
        self.tip_label = tk.Label(tips_frame, text="", font=('Arial', 9),
                                 bg='#0f3460', fg='white', wraplength=300, justify=tk.LEFT)
        self.tip_label.pack(pady=5, padx=10)
        
        # Alert frame
        alert_frame = tk.Frame(left_panel, bg='#0f3460', relief=tk.GROOVE, bd=2)
        alert_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.alert_label = tk.Label(alert_frame, text="✅ System Status: Normal", 
                                   font=('Arial', 10, 'bold'), bg='#0f3460', fg='#00ff88')
        self.alert_label.pack(pady=5)
        
        # Control buttons
        btn_frame = tk.Frame(left_panel, bg='#16213e')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="⏸️ Pause", command=self.toggle_monitoring,
                 bg='#ffa500', fg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📊 Export Data", command=self.export_data,
                 bg='#00b4d8', fg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🔄 Refresh", command=self.manual_refresh,
                 bg='#e94560', fg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        # Setup graphs in right panel
        self.setup_graphs(right_panel)
        
        # Update system info
        self.update_system_info()
        
    def create_gauge(self, parent, title, index, color):
        frame = tk.Frame(parent, bg='#16213e')
        frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(frame, text=title, font=('Arial', 11, 'bold'),
                bg='#16213e', fg='white').pack()
        
        # Progress bar
        progress = ttk.Progressbar(frame, length=250, mode='determinate', 
                                   style=f"custom.Horizontal.TProgressbar")
        progress.pack(pady=5)
        
        # Value label
        value_label = tk.Label(frame, text="0%", font=('Arial', 14, 'bold'),
                              bg='#16213e', fg=color)
        value_label.pack()
        
        # Store references
        if index == 0:
            self.cpu_bar = progress
            self.cpu_label = value_label
        elif index == 1:
            self.memory_bar = progress
            self.memory_label = value_label
        elif index == 2:
            self.disk_bar = progress
            self.disk_label = value_label
        elif index == 3:
            self.temp_bar = progress
            self.temp_label = value_label
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(f"custom.Horizontal.TProgressbar", background=color, thickness=20)
        
    def setup_graphs(self, parent):
        # Create figure for subplots
        self.fig = Figure(figsize=(8, 8), facecolor='#16213e')
        
        # CPU & Memory graph
        self.ax1 = self.fig.add_subplot(311)
        self.ax1.set_facecolor('#0f3460')
        self.ax1.set_title('CPU & Memory Usage', color='white', fontsize=10)
        self.ax1.set_xlabel('Time (seconds)', color='white', fontsize=8)
        self.ax1.set_ylabel('Usage (%)', color='white', fontsize=8)
        self.ax1.tick_params(colors='white')
        self.line1_cpu, = self.ax1.plot([], [], label='CPU', color='#00ff88', linewidth=2)
        self.line1_mem, = self.ax1.plot([], [], label='Memory', color='#ffa500', linewidth=2)
        self.ax1.legend(loc='upper right', facecolor='#16213e', labelcolor='white')
        self.ax1.grid(True, alpha=0.3)
        
        # Temperature & Disk graph
        self.ax2 = self.fig.add_subplot(312)
        self.ax2.set_facecolor('#0f3460')
        self.ax2.set_title('Temperature & Disk Usage', color='white', fontsize=10)
        self.ax2.set_xlabel('Time (seconds)', color='white', fontsize=8)
        self.ax2.set_ylabel('Value', color='white', fontsize=8)
        self.ax2.tick_params(colors='white')
        self.line2_temp, = self.ax2.plot([], [], label='Temp (°C)', color='#00b4d8', linewidth=2)
        self.line2_disk, = self.ax2.plot([], [], label='Disk (%)', color='#ff4444', linewidth=2)
        self.ax2.legend(loc='upper right', facecolor='#16213e', labelcolor='white')
        self.ax2.grid(True, alpha=0.3)
        
        # FPS graph
        self.ax3 = self.fig.add_subplot(313)
        self.ax3.set_facecolor('#0f3460')
        self.ax3.set_title('Game FPS', color='white', fontsize=10)
        self.ax3.set_xlabel('Time (seconds)', color='white', fontsize=8)
        self.ax3.set_ylabel('FPS', color='white', fontsize=8)
        self.ax3.tick_params(colors='white')
        self.line3_fps, = self.ax3.plot([], [], label='FPS', color='#e94560', linewidth=2)
        self.ax3.legend(loc='upper right', facecolor='#16213e', labelcolor='white')
        self.ax3.grid(True, alpha=0.3)
        self.ax3.set_ylim(0, 200)
        
        self.fig.tight_layout()
        
        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def get_system_status(self):
        cpu = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent if platform.system() != 'Windows' else psutil.disk_usage('C:\\').percent
        
        # Get CPU temperature (platform specific)
        cpu_temp = None
        if hasattr(psutil, "sensors_temperatures"):
            temp = psutil.sensors_temperatures()
            if "coretemp" in temp:
                for entry in temp["coretemp"]:
                    if entry.label == "Package id 0":
                        cpu_temp = entry.current
                        break
            elif platform.system() == "Windows":
                # Try to get temperature using WMI on Windows
                try:
                    import wmi
                    w = wmi.WMI()
                    temperature = w.Win32_PerfFormattedData_Counters_ThermalZoneInformation()[0].Temperature
                    cpu_temp = temperature / 10.0
                except:
                    cpu_temp = None
        else:
            cpu_temp = None
            
        return {
            "cpu": cpu,
            "memory": memory,
            "disk": disk,
            "cpu_temp": cpu_temp if cpu_temp else 0
        }
    
    def update_stats(self):
        if self.monitoring:
            status = self.get_system_status()
            
            # Update gauges
            self.cpu_bar['value'] = status['cpu']
            self.cpu_label.config(text=f"{status['cpu']:.1f}%")
            
            self.memory_bar['value'] = status['memory']
            self.memory_label.config(text=f"{status['memory']:.1f}%")
            
            self.disk_bar['value'] = status['disk']
            self.disk_label.config(text=f"{status['disk']:.1f}%")
            
            if status['cpu_temp']:
                temp_value = status['cpu_temp']
                self.temp_bar['value'] = min(100, temp_value)
                self.temp_label.config(text=f"{temp_value:.1f}°C")
                
                # Color coding for temperature
                if temp_value > 85:
                    self.temp_label.config(fg='#ff4444')
                    self.update_alert("⚠️ HIGH TEMPERATURE! Consider better cooling!", 'danger')
                elif temp_value > 75:
                    self.temp_label.config(fg='#ffa500')
                    self.update_alert("⚠️ Temperature is high", 'warning')
                else:
                    self.temp_label.config(fg='#00b4d8')
            else:
                self.temp_label.config(text="N/A")
            
            # Add to history
            self.cpu_history.append(status['cpu'])
            self.memory_history.append(status['memory'])
            self.disk_history.append(status['disk'])
            self.temp_history.append(status['cpu_temp'] if status['cpu_temp'] else 0)
            
            # Update graphs
            self.update_graphs()
            
            # Check for optimization tips
            self.show_optimization_tips(status)
            
            # Update color based on usage
            self.update_gauge_colors(status)
        
        # Schedule next update
        self.root.after(1000, self.update_stats)
    
    def update_graphs(self):
        x = range(len(self.cpu_history))
        
        self.line1_cpu.set_data(x, list(self.cpu_history))
        self.line1_mem.set_data(x, list(self.memory_history))
        
        self.line2_temp.set_data(x, list(self.temp_history))
        self.line2_disk.set_data(x, list(self.disk_history))
        
        if self.fps_history:
            self.line3_fps.set_data(x[:len(self.fps_history)], list(self.fps_history))
        
        # Adjust limits
        for ax in [self.ax1, self.ax2, self.ax3]:
            ax.relim()
            ax.autoscale_view()
            if ax == self.ax3 and self.fps_history:
                ax.set_ylim(0, max(200, max(self.fps_history) + 20))
        
        self.canvas.draw()
    
    def update_gauge_colors(self, status):
        # CPU color
        if status['cpu'] > 80:
            self.cpu_label.config(fg='#ff4444')
        elif status['cpu'] > 60:
            self.cpu_label.config(fg='#ffa500')
        else:
            self.cpu_label.config(fg='#00ff88')
        
        # Memory color
        if status['memory'] > 85:
            self.memory_label.config(fg='#ff4444')
            self.update_alert("⚠️ Low Memory! Close background apps!", 'warning')
        elif status['memory'] > 70:
            self.memory_label.config(fg='#ffa500')
        else:
            self.memory_label.config(fg='#ffa500')
    
    def update_fps(self):
        try:
            fps = float(self.fps_entry.get())
            self.fps_history.append(fps)
            
            # FPS alert
            if fps < 30:
                self.update_alert("⚠️ Low FPS! Consider lowering graphics settings!", 'danger')
            elif fps < 60:
                self.update_alert("⚠️ FPS below 60 - optimization recommended", 'warning')
            else:
                self.update_alert("✅ FPS is good!", 'success')
                
        except ValueError:
            pass
    
    def update_alert(self, message, level='info'):
        colors = {
            'info': '#00b4d8',
            'warning': '#ffa500',
            'danger': '#ff4444',
            'success': '#00ff88'
        }
        self.alert_label.config(text=message, fg=colors.get(level, 'white'))
        
        # Auto-clear after 3 seconds for non-critical alerts
        if level != 'danger':
            self.root.after(3000, lambda: self.alert_label.config(
                text="✅ System Status: Normal", fg='#00ff88'))
    
    def show_optimization_tips(self, status):
        tips = []
        
        if status['cpu'] > 80:
            tips.append("• Close unnecessary background processes")
            tips.append("• Set game process priority to High")
        elif status['cpu'] > 60:
            tips.append("• CPU usage is moderate - optimal for gaming")
        
        if status['memory'] > 85:
            tips.append("• Free up RAM by closing browser tabs")
            tips.append("• Consider adding more RAM")
        elif status['memory'] > 70:
            tips.append("• Close memory-heavy applications")
        
        if status['cpu_temp'] and status['cpu_temp'] > 80:
            tips.append("• Clean PC dust and improve ventilation")
            tips.append("• Check thermal paste application")
        elif status['cpu_temp'] and status['cpu_temp'] > 70:
            tips.append("• Monitor temperature - consider better cooling")
        
        if not tips:
            tips.append("• System running optimally!")
            tips.append("• Enable VSync for smoother gameplay")
            tips.append("• Update GPU drivers for best performance")
        
        tip_text = "\n".join(tips[:3])
        self.tip_label.config(text=tip_text)
    
    def update_system_info(self):
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        ram_gb = psutil.virtual_memory().total / (1024**3)
        
        info_text = f"CPU: {cpu_count} cores @ {cpu_freq.current:.0f}MHz\n"
        info_text += f"RAM: {ram_gb:.1f} GB\n"
        info_text += f"OS: {platform.system()} {platform.release()}\n"
        info_text += f"Python: {platform.python_version()}"
        
        self.system_info.config(text=info_text)
    
    def toggle_monitoring(self):
        self.monitoring = not self.monitoring
        status = "Paused" if not self.monitoring else "Monitoring"
        self.update_alert(f"System monitoring {status}", 'info')
    
    def manual_refresh(self):
        self.update_system_info()
        self.update_alert("System information refreshed!", 'success')
    
    def export_data(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gaming_stats_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write("GAMING SYSTEM MONITOR DATA\n")
            f.write(f"Exported: {datetime.now()}\n")
            f.write("="*50 + "\n\n")
            
            f.write("CPU History (%):\n")
            f.write(f"{list(self.cpu_history)}\n\n")
            
            f.write("Memory History (%):\n")
            f.write(f"{list(self.memory_history)}\n\n")
            
            f.write("Temperature History (°C):\n")
            f.write(f"{list(self.temp_history)}\n\n")
            
            f.write("FPS History:\n")
            f.write(f"{list(self.fps_history)}\n")
        
        messagebox.showinfo("Export Complete", f"Data exported to {filename}")
    
    def on_closing(self):
        self.monitoring = False
        self.root.destroy()

def main():
    root = tk.Tk()
    app = GamingSystemMonitor(root)
    
    # Set window icon if available
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    root.mainloop()

if __name__ == "__main__":
    # Check if required packages are installed
    try:
        import matplotlib
        import numpy
    except ImportError:
        print("Installing required packages...")
        os.system("pip install matplotlib numpy")
        print("Please restart the application")
        exit()
    
    main()