import psutil

cpu = psutil.cpu_percent(interval=1)
memory = psutil.virtual_memory().percent
disk = psutil.disk_usage('/').percent

print("CPU Usage:", cpu, "%")
print("Memory Usage:", memory, "%")
print("Disk Usage:", disk, "%")

if cpu <= 10:
    print(" System is idle")

elif cpu <= 60:
    print(" System is in normal usage")

elif cpu <= 85:
    print(" System is under high load")

else:
    print(" System is under critical load")


if memory > 80:
    print(" High memory usage")

if disk > 90:
    print(" Disk almost full")