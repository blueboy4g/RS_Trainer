import tkinter as tk
from tkinter import messagebox
import json
import os


APP_NAME = "Azulyn"
APPDATA_DIR = os.path.join(os.environ["APPDATA"], APP_NAME)
CONFIG_PATH = os.path.join(APPDATA_DIR, "keybinds.json")


ICON_PATH = "Resources/azulyn_icon.ico"

MODIFIER_ALIASES = {
    "CTRL": "LCTRL", "LCTRL": "LCTRL",
    "SHIFT": "LSHIFT", "LSHIFT": "LSHIFT",
    "ALT": "LALT", "LALT": "LALT"
}

class AbilityKeybindEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Keybind Editor")
        self.abilities = {}

        self.setup_ui()
        self.load_json()

    def setup_ui(self):
        # Scrollable area
        container = tk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container, height=500)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Header
        # tk.Label(self.scrollable_frame, text="Ability", width=18, anchor="w").grid(row=0, column=0, padx=5, sticky="w")
        # tk.Label(self.scrollable_frame, text="Key", width=12, anchor="w").grid(row=0, column=1, padx=5, sticky="w")
        # tk.Label(self.scrollable_frame, text="Ctrl", width=8, anchor="w").grid(row=0, column=2, padx=5)
        # tk.Label(self.scrollable_frame, text="Shift", width=8, anchor="w").grid(row=0, column=3, padx=5)
        # tk.Label(self.scrollable_frame, text="Alt", width=8, anchor="w").grid(row=0, column=4, padx=5)

        self.rows_container = self.scrollable_frame  # use same frame for alignment

        # Bottom save button
        bottom = tk.Frame(self.root)
        bottom.pack(fill=tk.X, pady=10)

        tk.Button(bottom, text="SAVE", command=self.save_json, background='gray', foreground='black', fg='black', width=20,
                  font=('Helvetica 13 bold italic') ).pack()

    def add_section(self, title, ability_list, start_row):
        collapsed = tk.BooleanVar(value=True)

        # Row: Section label in col 0, expand/collapse button in col 1
        tk.Label(self.rows_container, text="       " + title, font=("Arial", 12, "bold")).grid(
            row=start_row, column=0, sticky="w", padx=5
        )

        toggle_button = tk.Button(self.rows_container, text="[+]", width=3)
        toggle_button.grid(row=start_row, column=0, sticky="w")

        # Content frame (hidden until expanded)
        content_frame = tk.Frame(self.rows_container)
        content_frame.grid(row=start_row + 1, column=0, columnspan=5, sticky="w")
        content_frame.grid_remove()

        def toggle():
            if collapsed.get():
                content_frame.grid()
                toggle_button.config(text="[-]")
                collapsed.set(False)
            else:
                content_frame.grid_remove()
                toggle_button.config(text="[+]")
                collapsed.set(True)

        toggle_button.config(command=toggle)

        # ➕ Header row inside each section
        tk.Label(content_frame, text="Ability", width=18, anchor="w").grid(row=0, column=0, padx=5, sticky="w")
        tk.Label(content_frame, text="Key", width=12, anchor="w").grid(row=0, column=1, padx=5, sticky="w")
        tk.Label(content_frame, text="Ctrl", width=8, anchor="w").grid(row=0, column=2, padx=5)
        tk.Label(content_frame, text="Shift", width=8, anchor="w").grid(row=0, column=3, padx=5)
        tk.Label(content_frame, text="Alt", width=8, anchor="w").grid(row=0, column=4, padx=5)

        # Ability rows (start at row=1 now)
        for i, (name, keys) in enumerate(ability_list, start=1):
            self.add_ability_row(content_frame, i, name, keys)

        return start_row + 2 + len(ability_list)


    def load_json(self):
        if not os.path.exists(CONFIG_PATH):
            messagebox.showerror("Missing File", f"Cannot find: {CONFIG_PATH}")
            return

        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)

        keybinds = data.get("ABILITY_KEYBINDS", {})

        # Sort abilities by their appearance in the JSON
        abilities = list(keybinds.items())

        sections = {
            "Gear": [],
            "Misc": [],
            "Melee": [],
            "Range": [],
            "Magic": [],
            "Necromancy": [],
            "Defence": []
        }

        current_section = "Gear"
        for name, keys in abilities:
            if name.lower() == "adrenaline_potion":
                current_section = "Misc"
            if name.lower() == "assault":
                current_section = "Melee"
            if name.lower() == "binding_shot":
                current_section = "Range"
            if name.lower() == "animate_dead":
                current_section = "Magic"
            if name.lower() == "bloat":
                current_section = "Necromancy"
            if name.lower() == "anticipation":
                current_section = "Defence"

            sections[current_section].append((name, keys))

        row = 1
        for section_name, ability_list in sections.items():
            row = self.add_section(section_name, ability_list, row)


    def save_json(self):
        data = {"ABILITY_KEYBINDS": {}}
        for name, (modifiers, key_entry) in self.abilities.items():
            key = key_entry.get().strip()
            mods = []
            if modifiers["ctrl"].get():
                mods.append("LCTRL")
            if modifiers["shift"].get():
                mods.append("SHIFT")
            if modifiers["alt"].get():
                mods.append("ALT")
            if key:
                mods.append(key.upper())
            data["ABILITY_KEYBINDS"][name] = mods

        with open(CONFIG_PATH, "w") as f:
            json.dump(data, f, indent=2)

        messagebox.showinfo("Saved", f"Saved to:\n{CONFIG_PATH}")

    def add_ability_row(self, parent_frame, row_num, ability_name, keys):
        tk.Label(parent_frame, text=ability_name, width=25, anchor="w").grid(row=row_num, column=0, padx=5, sticky="w")

        key_entry = tk.Entry(parent_frame, width=12)
        key_entry.grid(row=row_num, column=1, padx=5, sticky="w")

        ctrl_var = tk.BooleanVar()
        shift_var = tk.BooleanVar()
        alt_var = tk.BooleanVar()

        tk.Checkbutton(parent_frame, variable=ctrl_var).grid(row=row_num, column=2, padx=5)
        tk.Checkbutton(parent_frame, variable=shift_var).grid(row=row_num, column=3, padx=5)
        tk.Checkbutton(parent_frame, variable=alt_var).grid(row=row_num, column=4, padx=5)

        for k in keys:
            normalized = MODIFIER_ALIASES.get(k.upper(), None)
            if normalized == "LCTRL":
                ctrl_var.set(True)
            elif normalized == "LSHIFT":
                shift_var.set(True)
            elif normalized == "LALT":
                alt_var.set(True)
            else:
                key_entry.insert(0, k.upper())

        self.abilities[ability_name] = (
            {"ctrl": ctrl_var, "shift": shift_var, "alt": alt_var},
            key_entry
        )


if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap(ICON_PATH)
    root.geometry("550x650")
    app = AbilityKeybindEditor(root)
    root.mainloop()
