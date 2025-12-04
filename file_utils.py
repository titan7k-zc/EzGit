import os
import shutil
import customtkinter as ctk
from tkinter import messagebox

class FileUtilsMixin:
    """
    Mixin class containing all File System related logic.
    Expects the host class to have:
    - self.current_path
    - self.history_stack
    - self.future_stack
    - self.path_entry (CTkEntry)
    - self.file_scroll (CTkScrollableFrame)
    - self.checkbox_vars (dict)
    - self.log(message)
    - self.check_git_status()
    """

    def load_directory(self, path, add_history=True):
        if not os.path.isdir(path): return
        
        if add_history and path != self.current_path:
            self.history_stack.append(self.current_path)
            self.future_stack.clear() # Clear forward history on new nav
        
        self.current_path = path
        self.path_entry.delete(0, "end")
        self.path_entry.insert(0, self.current_path)
        
        # Clear File List
        for w in self.file_scroll.winfo_children(): w.destroy()
        self.checkbox_vars.clear()

        # List Files
        try:
            # Show ALL files (removed .git filter)
            items = sorted(os.listdir(path), key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))
            for item in items:
                full_path = os.path.join(path, item)
                is_dir = os.path.isdir(full_path)
                
                row = ctk.CTkFrame(self.file_scroll, fg_color="transparent")
                row.pack(fill="x", pady=1)

                var = ctk.BooleanVar()
                self.checkbox_vars[full_path] = var
                ctk.CTkCheckBox(row, text="", variable=var, width=24).pack(side="left", padx=5)

                if is_dir:
                    btn = ctk.CTkButton(row, text=f"📁 {item}", fg_color="transparent", anchor="w", 
                                        command=lambda p=full_path: self.load_directory(p))
                    btn.pack(side="left", fill="x", expand=True)
                else:
                    ctk.CTkLabel(row, text=f"📄 {item}", anchor="w").pack(side="left", fill="x", expand=True, padx=10)
        except Exception as e:
            self.log(f"Error listing files: {e}")

        self.check_git_status()

    def go_back(self):
        if self.history_stack:
            self.future_stack.append(self.current_path)
            prev = self.history_stack.pop()
            self.load_directory(prev, add_history=False)

    def go_forward(self):
        if self.future_stack:
            self.history_stack.append(self.current_path)
            next_path = self.future_stack.pop()
            self.load_directory(next_path, add_history=False)

    def go_up(self):
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path:
            self.load_directory(parent)

    def on_path_entry(self, event):
        path = self.path_entry.get()
        if os.path.isdir(path):
            self.load_directory(path)
        else:
            self.log("Invalid path entered.")

    def create_folder(self):
        dialog = ctk.CTkInputDialog(text="Enter Folder Name:", title="New Folder")
        name = dialog.get_input()
        if name:
            try:
                os.makedirs(os.path.join(self.current_path, name))
                self.log(f"Created folder: {name}")
                self.load_directory(self.current_path, add_history=False)
            except Exception as e:
                self.log(f"Error creating folder: {e}")

    def rename_item(self):
        selected = [p for p, v in self.checkbox_vars.items() if v.get()]
        if len(selected) != 1:
            self.log("Please select exactly one item to rename.")
            return
        
        old_path = selected[0]
        old_name = os.path.basename(old_path)
        dialog = ctk.CTkInputDialog(text=f"Rename '{old_name}' to:", title="Rename")
        new_name = dialog.get_input()
        
        if new_name:
            try:
                new_path = os.path.join(os.path.dirname(old_path), new_name)
                os.rename(old_path, new_path)
                self.log(f"Renamed {old_name} to {new_name}")
                self.load_directory(self.current_path, add_history=False)
            except Exception as e:
                self.log(f"Error renaming: {e}")

    def delete_items(self):
        selected = [p for p, v in self.checkbox_vars.items() if v.get()]
        if not selected:
            self.log("No items selected to delete.")
            return
        
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {len(selected)} item(s)?\nThis cannot be undone."):
            return

        for path in selected:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                self.log(f"Deleted: {path}")
            except Exception as e:
                self.log(f"Error deleting {path}: {e}")
        
        self.load_directory(self.current_path, add_history=False)
