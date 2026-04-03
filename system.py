import psutil


def get_system_status():
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    temp = psutil.sensors_temperatures()



    cpu_temp = None
    
    if "coretemp" in temp:
        for entry in temp["coretemp"]:
            if entry.label == "Package id 0":
                cpu_temp = entry.current
                break 
    return{
        "cpu":cpu,
        "memory":memory,
        "disk":disk,
        "cpu_temp":cpu_temp
    }    


if __name__ == "__main__":
    status = get_system_status()

    print("cpu:",status["cpu"], "%")
    print("memory:",status["memory"], "%")
    print("disk:",status["disk"], "%")
    print("cpu_temp:",status["cpu_temp"], "C")
