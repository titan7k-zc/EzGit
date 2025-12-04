import subprocess
import threading
import os
import customtkinter as ctk

class GitUtilsMixin:
    """
    Mixin class containing all Git-related logic.
    Expects the host class to have:
    - self.current_path
    - self.log(message)
    - self.load_directory(path, add_history=False)
    - self.branch_scroll (CTkScrollableFrame)
    - self.name_entry, self.email_entry, self.remote_entry (CTkEntry)
    - self.run_git(command, refresh=True) (Helper wrapper)
    """

    def run_git(self, command, refresh=True):
        self.log(f"$ {command}")
        def task():
            try:
                # Use --no-pager to avoid hanging on commands that paginate
                cmd_to_run = command
                if "git log" in command or "git diff" in command:
                     if "--no-pager" not in command:
                        cmd_to_run = command.replace("git ", "git --no-pager ", 1)

                result = subprocess.run(cmd_to_run, shell=True, cwd=self.current_path, capture_output=True, text=True, encoding='utf-8', errors='replace')
                if result.stdout: self.log(result.stdout)
                
                # Git sends progress to stderr, so check return code
                if result.stderr:
                    if result.returncode != 0:
                        self.log(f"Error: {result.stderr}")
                    else:
                        self.log(result.stderr) # Log as info
                
                if refresh:
                    self.after(0, lambda: self.load_directory(self.current_path, add_history=False))
            except Exception as e:
                self.log(f"Exception: {e}")
        threading.Thread(target=task).start()

    def check_git_status(self):
        git_dir = os.path.join(self.current_path, ".git")
        if os.path.isdir(git_dir):
            self.git_found = True
            self.load_git_config()
            self.load_branches()
        else:
            self.git_found = False
            for w in self.branch_scroll.winfo_children(): w.destroy()
            ctk.CTkLabel(self.branch_scroll, text="Not a git repo").pack(pady=10)
            self.name_entry.delete(0, "end")
            self.email_entry.delete(0, "end")
            self.remote_entry.delete(0, "end")

    def load_git_config(self):
        def get_conf(key):
            try: return subprocess.check_output(f"git config {key}", shell=True, cwd=self.current_path, text=True).strip()
            except: return ""
        def get_remote():
            try: return subprocess.check_output("git remote get-url origin", shell=True, cwd=self.current_path, text=True).strip()
            except: return ""

        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, get_conf("user.name"))
        self.email_entry.delete(0, "end")
        self.email_entry.insert(0, get_conf("user.email"))
        self.remote_entry.delete(0, "end")
        self.remote_entry.insert(0, get_remote())

    def save_config(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        url = self.remote_entry.get()
        if name: self.run_git(f'git config user.name "{name}"', refresh=False)
        if email: self.run_git(f'git config user.email "{email}"', refresh=False)
        if url:
            try:
                subprocess.check_call("git remote", shell=True, cwd=self.current_path, stdout=subprocess.DEVNULL)
                self.run_git(f'git remote set-url origin "{url}"', refresh=False)
            except:
                self.run_git(f'git remote add origin "{url}"', refresh=False)
        self.log("Config saved.")

    def load_branches(self):
        for w in self.branch_scroll.winfo_children(): w.destroy()

        try:
            # Use git for-each-ref for reliable parsing
            # Format: %(refname:short)|%(HEAD)
            # HEAD will be '*' if it's the current branch, otherwise empty
            cmd = 'git for-each-ref --format="%(refname:short)|%(HEAD)" refs/heads refs/remotes'
            output = subprocess.check_output(
                cmd, 
                shell=True, 
                cwd=self.current_path, 
                text=True, 
                stderr=subprocess.DEVNULL,
                encoding='utf-8'
            )

            lines = output.splitlines()

            local_branches = []      # list of (name, is_current)
            remote_branches = {}     # remote_name -> list of branch names
            
            for line in lines:
                if not line.strip(): continue
                parts = line.split("|")
                if len(parts) != 2: continue
                
                ref_name, is_head = parts
                is_current = (is_head == "*")
                
                if ref_name.startswith("origin/") or "/" in ref_name:
                    # It's likely a remote branch or has a slash
                    # Check if it starts with a known remote? 
                    # Actually for-each-ref returns 'origin/main', 'master', etc.
                    # refs/heads/master -> master
                    # refs/remotes/origin/main -> origin/main
                    
                    # Wait, for-each-ref with refname:short strips refs/heads and refs/remotes
                    # So 'refs/heads/main' becomes 'main'
                    # 'refs/remotes/origin/HEAD' becomes 'origin/HEAD'
                    
                    if "/" in ref_name:
                        # Likely remote
                        remote_name, branch_name = ref_name.split("/", 1)
                        if branch_name == "HEAD": continue # Skip HEAD pointer
                        
                        if remote_name not in remote_branches:
                            remote_branches[remote_name] = []
                        remote_branches[remote_name].append(branch_name)
                    else:
                        # Local branch
                        local_branches.append((ref_name, is_current))
                else:
                    # Local branch
                    local_branches.append((ref_name, is_current))

            # ------------------- Display Local Branches -------------------
            if local_branches:
                lbl = ctk.CTkLabel(self.branch_scroll, text="Local Branches", font=ctk.CTkFont(size=14, weight="bold"))
                lbl.pack(anchor="w", padx=20, pady=(10, 5))

                for name, is_current in local_branches:
                    display_text = f"{name} (current)" if is_current else name

                    btn = ctk.CTkButton(
                        self.branch_scroll,
                        text=display_text,
                        fg_color="#5865F2" if is_current else "transparent",
                        text_color="white" if is_current else None,
                        font=ctk.CTkFont(weight="bold") if is_current else None,
                        anchor="w",
                        height=32,
                        command=lambda n=name: self.run_git(f"git checkout {n}")
                    )
                    btn.pack(fill="x", pady=2, padx=20)

                    if not is_current:
                        btn.configure(border_width=1, border_color="#555555")

            # ------------------- Display Remote Branches -------------------
            if remote_branches:
                lbl = ctk.CTkLabel(self.branch_scroll, text="Remote Branches", font=ctk.CTkFont(size=14, weight="bold"))
                lbl.pack(anchor="w", padx=20, pady=(20, 5))

                for remote_name in sorted(remote_branches.keys()):
                    sub_lbl = ctk.CTkLabel(self.branch_scroll, text=remote_name, font=ctk.CTkFont(size=12))
                    sub_lbl.pack(anchor="w", padx=35, pady=(8, 2))

                    for branch_name in sorted(remote_branches[remote_name]):
                        full_remote_branch = f"{remote_name}/{branch_name}"
                        btn = ctk.CTkButton(
                            self.branch_scroll,
                            text=branch_name,
                            fg_color="transparent",
                            text_color="#aaaaaa",
                            anchor="w",
                            height=30,
                            command=lambda b=full_remote_branch: self.run_git(f"git checkout {b}")
                        )
                        btn.pack(fill="x", pady=1, padx=40)
                        btn.configure(hover_color="#333333")

            if not local_branches and not remote_branches:
                ctk.CTkLabel(self.branch_scroll, text="No branches found", text_color="#888888").pack(pady=20)

        except subprocess.CalledProcessError as e:
            ctk.CTkLabel(self.branch_scroll, text="Git error (not a repo?)", text_color="red").pack(pady=10)
            self.log(f"Git branch error: {e}")
        except Exception as e:
            ctk.CTkLabel(self.branch_scroll, text="Failed to load branches", text_color="red").pack(pady=10)
            self.log(f"Branch load exception: {e}")

    def create_branch(self, switch):
        name = self.new_branch_entry.get()
        if not name:
            self.log("Enter a branch name.")
            return
        cmd = f"git checkout -b {name}" if switch else f"git branch {name}"
        self.run_git(cmd)
        self.new_branch_entry.delete(0, "end")

    def git_clone(self):
        url = self.remote_entry.get()
        if url: self.run_git(f"git clone {url}")
        else: self.log("Enter URL in Remote URL field.")

    def get_selected_files(self):
        return [f'"{os.path.relpath(p, self.current_path)}"' for p, v in self.checkbox_vars.items() if v.get()]

    def git_add_selected(self):
        files = self.get_selected_files()
        if files: self.run_git("git add " + " ".join(files))
        else: self.log("No files selected.")

    def git_unstage_selected(self):
        files = self.get_selected_files()
        if files: self.run_git("git restore --staged " + " ".join(files))
        else: self.log("No files selected.")

    def git_discard_selected(self):
        files = self.get_selected_files()
        if files: self.run_git("git restore " + " ".join(files))
        else: self.log("No files selected.")

    def git_commit(self):
        msg = self.commit_entry.get()
        if msg:
            self.run_git(f'git commit -m "{msg}"')
            self.commit_entry.delete(0, "end")
        else: self.log("Enter commit message.")

    def git_push_u(self):
        try:
            branch = subprocess.check_output("git rev-parse --abbrev-ref HEAD", shell=True, cwd=self.current_path, text=True).strip()
            self.run_git(f"git push -u origin {branch}")
        except: self.log("Could not determine current branch.")
