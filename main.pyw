import sys
import platform

# Windows-only imports (loaded later)
# import ctypes  <-- DO NOT import globally on Linux

from gui import GitHubHelperApp
# test user branch push test

def run_app():
    app = GitHubHelperApp()
    app.mainloop()


if __name__ == "__main__":
    system = platform.system()

    # ---------------------------
    # Windows: Check admin rights
    # ---------------------------
    if system == "Windows":
        import ctypes

        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            is_admin = False

        if is_admin:
            run_app()
        else:
            # Relaunch with admin rights
            executable = sys.executable

            # Switch python.exe → pythonw.exe for GUI-only startup
            if executable.endswith("python.exe"):
                executable = executable.replace("python.exe", "pythonw.exe")

            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                executable,
                " ".join(sys.argv),
                None,
                1,
            )
            sys.exit()  # Prevent falling through on Windows

    # ---------------------------
    # Linux & macOS: run normally
    # ---------------------------
    else:
        # No admin elevation needed or supported for GUI apps
        run_app()
