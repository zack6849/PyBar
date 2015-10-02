import subprocess
import psutil
import pipes
import time
import sys

seperator = "   "

def get_date():
    return time.strftime("%A, %B, %d, %G @ %I:%M %p")

def get_output(command):
    return subprocess.check_output(command, shell=True).decode("utf-8").strip()

def is_music_playing():
    status = get_output("mpc status | grep playing | wc -l")
    return "1" in status

def get_cpu_usage():
    return "{:02.0f}".format(psutil.cpu_percent(interval=None)) + "%"

def get_ram_used():
     return "{:02.0f}".format(psutil.virtual_memory().percent) + "%"

def get_playing():
    if is_music_playing():
        return get_output("mpc -f \"[%albumartist% - %title%]\" | tr '\n' '|'| cut -d'|' -f1")

def get_current_window():
    return get_output("xtitle")

def get_workspaces(monitor):
    active = "\ue099"
    inactive = "\ue0e7"
    workspaces = get_output("bspc query -D").splitlines()
    line = ""
    print("Length: " + str(len(workspaces)))
    print(type(workspaces))
    for workspace in workspaces: 
        workspace = int(workspace)        
        if monitor == 0 and workspace in range(1,6):
            line += str(workspace) + " "
        if monitor == 1 and workspace in range(6, 11):
            line += str(workspace) + " "
    return line

def get_active_workspace(monitor):
    tree = get_output("bspc query -T").splitlines()
    flag = False
    for line in tree:
        if "DVI-" + str(monitor) in line:
            flag = True
        if flag and line.startswith("\t") and not line.startswith("\t\t"):
            workspace = int(line.split(" ")[0].strip())
            if monitor == 0 and workspace in range(0, 6) and "*" in line:
                return workspace
            if monitor == 1 and workspace in range(6,11) and "*" in line:
                return workspace

def get_workspace_text(monitor):
    focused_color = "%{F#0066FF}"
    unfocused_color = "%{F#66CCFF}"
    window_icon = "\ue056"
    lines = ""

    active_workspace = get_active_workspace(monitor)
    if monitor == 0:
        workspace_range = range(1,6)
    if monitor == 1:
        workspace_range = range(6, 11)

    for num in workspace_range:
        if num == active_workspace:
            lines += focused_color + "%{A:bspc desktop -f " + str(num) + ":}" + window_icon + "%{A}%{F-} "
        else:
            lines += unfocused_color + "%{A:bspc desktop -f " + str(num) + ":}" + window_icon + "%{A}%{F-} "

    return lines.strip()

def get_text():
    lines = "%{B#333333}%{l} %MONITORSTATUS%"
    lines += "%{c}" + get_current_window() + seperator +"%{r}"

    if is_music_playing():
        lines += "  %{FMagenta}\ue05c "
        lines += "%{FCyan}" + get_playing() + "%{F-}"
        lines += " %{FMagenta}\ue05c%{F-}  "

    lines += "%{F-}"
    if is_music_playing():
        lines += "%{A:mpc toggle:} \ue059 %{A} "
    else:
        lines += "%{A:mpc toggle:} \ue058 %{A} "
    lines += "%{F-}"

    lines += seperator
    lines += "%{FCyan}\ue022" + get_cpu_usage() + "%{%F-}"
    lines += seperator
    lines += "%{FGreen}\ue021" + get_ram_used() + "%{F-}"
    lines += seperator
    lines += "%{FYellow}\ue016" + get_date() + "%{F-}"

    return "%{S0} " + lines.replace("%MONITORSTATUS%", get_workspace_text(1)) + " %{S1} " + lines.replace("%MONITORSTATUS%", get_workspace_text(0)) 

if __name__ == "__main__":
    while True:
        sys.stdout.write(get_text() + "\n")
        sys.stdout.flush()
        time.sleep(0.5)
