import sys
import ctypes
from gui import GitHubHelperApp

if __name__ == "__main__":
    # Check for admin rights
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False

    if is_admin:
        app = GitHubHelperApp()
        app.mainloop()
    else:
        # Re-run the program with admin rights
        # Try to use pythonw.exe to avoid console window
        executable = sys.executable
        if "python.exe" in executable:
            executable = executable.replace("python.exe", "pythonw.exe")
            
        ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, " ".join(sys.argv), None, 1)
