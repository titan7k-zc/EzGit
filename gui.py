import customtkinter as ctk
import os
import platform
from git_utils import GitUtilsMixin
from file_utils import FileUtilsMixin

# Set appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class GitHubHelperApp(ctk.CTk, GitUtilsMixin, FileUtilsMixin):
    def __init__(self):
        super().__init__()

        if platform.system() == "Windows":
            script_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(script_dir, "zc.ico")
            self.iconbitmap(icon_path)

        # Window setup
        self.title("ZC EzGit v2.0")
        self.geometry("1100x700")

        # State
        self.current_path = os.getcwd()
        self.history_stack = []
        self.future_stack = []
        self.checkbox_vars = {}  # path -> BooleanVar
        self.git_found = False

        # Layout Configuration
        self.grid_columnconfigure(1, weight=1)  # Main area expands
        self.grid_rowconfigure(0, weight=1)

        # ================== LEFT SIDEBAR ==================
        self.sidebar = ctk.CTkFrame(self, width=400, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(3, weight=1) # File list expands

        # --- File Manager Section ---
        self.logo_label = ctk.CTkLabel(self.sidebar, text="File Manager", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Navigation Controls (Back/Forward/Up)
        self.nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.nav_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        self.back_btn = ctk.CTkButton(self.nav_frame, text="⬅", width=40, command=self.go_back)
        self.back_btn.pack(side="left", padx=2)
        
        self.fwd_btn = ctk.CTkButton(self.nav_frame, text="➡", width=40, command=self.go_forward)
        self.fwd_btn.pack(side="left", padx=2)
        
        self.up_btn = ctk.CTkButton(self.nav_frame, text="⬆ Up", width=60, command=self.go_up)
        self.up_btn.pack(side="left", padx=2)
        
        self.refresh_btn = ctk.CTkButton(self.nav_frame, text="↻", width=40, command=lambda: self.load_directory(self.current_path))
        self.refresh_btn.pack(side="left", padx=2)

        # Path Entry
        self.path_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Path")
        self.path_entry.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.path_entry.bind("<Return>", self.on_path_entry)

        # File List (Moved above buttons)
        self.file_scroll = ctk.CTkScrollableFrame(self.sidebar, label_text="Files")
        self.file_scroll.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        # File Operations (Moved below list)
        self.file_ops_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.file_ops_frame.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        
        ctk.CTkButton(self.file_ops_frame, text="+ Folder", width=80, command=self.create_folder, fg_color="#2ea043").pack(side="left", padx=2, expand=True)
        ctk.CTkButton(self.file_ops_frame, text="Rename", width=80, command=self.rename_item, fg_color="#d9534f").pack(side="left", padx=2, expand=True)
        ctk.CTkButton(self.file_ops_frame, text="Delete", width=80, command=self.delete_items, fg_color="#d9534f").pack(side="left", padx=2, expand=True)


        # ================== MAIN AREA (CENTER) ==================
        self.main_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_area.grid_rowconfigure(2, weight=1) # Tabs expand
        self.main_area.grid_columnconfigure(0, weight=1)

        # --- Top: Output & Config ---
        self.top_frame = ctk.CTkFrame(self.main_area)
        self.top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Output Terminal
        self.output_text = ctk.CTkTextbox(self.top_frame, height=120, font=("Consolas", 12))
        self.output_text.pack(fill="x", padx=10, pady=10)
        self.output_text.configure(state="disabled")

        # Config Editor
        self.config_frame = ctk.CTkFrame(self.main_area)
        self.config_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkLabel(self.config_frame, text="Git Config", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        self.conf_grid = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        self.conf_grid.pack(fill="x", padx=5, pady=5)
        
        # Name
        self.name_frame = ctk.CTkFrame(self.conf_grid, fg_color="transparent")
        self.name_frame.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(self.name_frame, text="Name").pack(anchor="w")
        self.name_entry = ctk.CTkEntry(self.name_frame, placeholder_text="User Name")
        self.name_entry.pack(fill="x")

        # Email
        self.email_frame = ctk.CTkFrame(self.conf_grid, fg_color="transparent")
        self.email_frame.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(self.email_frame, text="Email").pack(anchor="w")
        self.email_entry = ctk.CTkEntry(self.email_frame, placeholder_text="Email")
        self.email_entry.pack(fill="x")

        # URL
        self.url_frame = ctk.CTkFrame(self.conf_grid, fg_color="transparent")
        self.url_frame.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(self.url_frame, text="Repo URL").pack(anchor="w")
        self.remote_entry = ctk.CTkEntry(self.url_frame, placeholder_text="Repo URL")
        self.remote_entry.pack(fill="x")
        
        ctk.CTkButton(self.conf_grid, text="Save", width=60, command=self.save_config).pack(side="left", padx=5, pady=(20, 0))


        # --- Bottom: Tabs ---
        self.tabs = ctk.CTkTabview(self.main_area)
        self.tabs.grid(row=2, column=0, sticky="nsew")
        
        self.tab_basic = self.tabs.add("Basic Actions")
        self.tab_remote = self.tabs.add("Remote Operations")
        self.tab_advanced = self.tabs.add("Advanced Tools")

        self.setup_basic_tab()
        self.setup_remote_tab()
        self.setup_advanced_tab()


        # ================== RIGHT SIDEBAR ==================
        self.right_sidebar = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.right_sidebar.grid(row=0, column=2, sticky="nsew")
        self.right_sidebar.grid_rowconfigure(1, weight=1) # Branch list expands

        # --- Branch Manager Section ---
        ctk.CTkLabel(self.right_sidebar, text="Branch Manager", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.branch_scroll = ctk.CTkScrollableFrame(self.right_sidebar, label_text="Branches")
        self.branch_scroll.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Branch Creation
        self.new_branch_frame = ctk.CTkFrame(self.right_sidebar, fg_color="transparent")
        self.new_branch_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        self.new_branch_entry = ctk.CTkEntry(self.new_branch_frame, placeholder_text="New Branch Name")
        self.new_branch_entry.pack(fill="x", pady=5)
        
        self.create_br_btn = ctk.CTkButton(self.new_branch_frame, text="Create", width=80, command=lambda: self.create_branch(False))
        self.create_br_btn.pack(side="left", padx=2, expand=True)
        
        self.create_switch_btn = ctk.CTkButton(self.new_branch_frame, text="Create & Switch", width=120, command=lambda: self.create_branch(True))
        self.create_switch_btn.pack(side="left", padx=2, expand=True)

        # Initial Load
        self.load_directory(self.current_path)


    # ================== TAB SETUP ==================
    def setup_basic_tab(self):
        t = self.tab_basic
        
        # Row 1: Setup
        r1 = ctk.CTkFrame(t, fg_color="transparent")
        r1.pack(fill="x", pady=10)
        ctk.CTkButton(r1, text="Clone from URL", command=self.git_clone, fg_color="#5865F2").pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(r1, text="Initialize Repo", command=lambda: self.run_git("git init"), fg_color="#5865F2").pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(r1, text="Status", command=lambda: self.run_git("git status")).pack(side="left", fill="x", expand=True, padx=5)

        # Row 2: Staging
        r2 = ctk.CTkFrame(t, fg_color="transparent")
        r2.pack(fill="x", pady=10)
        ctk.CTkButton(r2, text="Stage Selected", command=self.git_add_selected, fg_color="green").pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(r2, text="Stage All (.)", command=lambda: self.run_git("git add ."), fg_color="green").pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(r2, text="Stage Changes (-A)", command=lambda: self.run_git("git add -A"), fg_color="green").pack(side="left", fill="x", expand=True, padx=5)

        # Row 3: Commit
        r3 = ctk.CTkFrame(t, fg_color="transparent")
        r3.pack(fill="x", pady=10)
        self.commit_entry = ctk.CTkEntry(r3, placeholder_text="Commit Message")
        self.commit_entry.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(r3, text="Commit", command=self.git_commit, fg_color="#2ea043").pack(side="left", padx=5)

        # Row 4: History
        r4 = ctk.CTkFrame(t, fg_color="transparent")
        r4.pack(fill="x", pady=10)
        ctk.CTkButton(r4, text="View Last 10 Commits (Log)", command=lambda: self.run_git("git log --oneline -n 10 --graph --decorate")).pack(fill="x", padx=5)

    def setup_remote_tab(self):
        t = self.tab_remote
        
        ctk.CTkButton(t, text="Upload", command=lambda: self.run_git("git pull"), height=40).pack(fill="x", padx=20, pady=10)
        ctk.CTkButton(t, text="Download", command=lambda: self.run_git("git push"), height=40).pack(fill="x", padx=20, pady=10)
        ctk.CTkButton(t, text="Sync", command=lambda: self.run_git("git fetch"), height=40).pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(t, text="First Push", font=("Arial", 14, "bold")).pack(pady=(40, 5))
        ctk.CTkButton(t, text="Push -u origin <current_branch>", command=self.git_push_u, fg_color="#7289da").pack(fill="x", padx=20, pady=5)

    def setup_advanced_tab(self):
        t = self.tab_advanced
        
        ctk.CTkLabel(t, text="Danger Zone / Advanced", font=("Arial", 14, "bold")).pack(pady=10)
        
        ctk.CTkButton(t, text="Unstage Selected (Restore --staged)", command=self.git_unstage_selected, fg_color="#d9534f").pack(fill="x", padx=20, pady=10)
        ctk.CTkButton(t, text="Discard Changes in Selected (Restore)", command=self.git_discard_selected, fg_color="#d9534f").pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(t, text="Show Diff", command=lambda: self.run_git("git diff")).pack(fill="x", padx=20, pady=10)

    def log(self, text):
        self.output_text.configure(state="normal")
        self.output_text.insert("end", f"{text}\n")
        self.output_text.see("end")
        self.output_text.configure(state="disabled")
