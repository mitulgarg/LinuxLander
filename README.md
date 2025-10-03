Click on HotKeys - SPACE + M to begin program
Agent checks specified log files for system level errors and suggests solutions in real time

Use troubleshooter.toml to setup configs


Steps to run - 
sudo systemctl daemon-reload
sudo systemctl restart troubleshooter.service


admin@MitulUbuntu1:~$ sudo systemctl status troubleshooter.service 
● troubleshooter.service - Linux Troubleshooter Agent
     Loaded: loaded (/etc/systemd/system/troubleshooter.service; enabled; prese>
     Active: active (running) since Fri 2025-10-03 18:36:24 UTC; 28s ago
 Invocation: 018353c74f1f42babf1562f3f3fdc737
   Main PID: 111853 (python3)
      Tasks: 2 (limit: 8516)
     Memory: 67.2M (peak: 67.6M)
        CPU: 466ms
     CGroup: /system.slice/troubleshooter.service
             └─111853 /home/admin/Desktop/LinuxProject/venv/bin/python3 main.py

Oct 03 18:36:24 MitulUbuntu1 systemd[1]: Started troubleshooter.service - Linux>
lines 1-12/12 (END)
