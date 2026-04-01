import psutil

cpu = psutil.cpu_percent(interval=1)
memory = psutil.virtual_memory().percent
disk = psutil.disk_usage('/').percent
temp = psutil.sensors_temperatures()
per_core = psutil.cpu_percent(percpu=True)
print("CPU Usage:", cpu, "%")
print("Memory Usage:", memory, "%")
print("Disk Usage:", disk, "%")
cpu_temp = None
if "coretemp" in temp:
    for enter in temp["coretemp"]:
        if enter.label == "Package id 0":
            cpu_temp = enter.current
            break
if cpu_temp is not None:
    print("cpu temperature:",cpu_temp,"C")
else:
    print("cpu temp not found")
