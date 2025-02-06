import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re


class TestSequenceEditor:
    def __init__(self, root):
        self.root = root
        self.json_data = None  # No file loaded initially
        self.json_filename = None  # File name is unknown until user imports

        self.root.title("Test Sequence Editor")

        # Define columns with new order
        columns = ("Check", "ID", "Test Name", "Steps", "Min", "Max", "Units")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")

        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)

            # Auto-adjust column width based on column name
            col_width = max(120, len(col) * 10)

            # Center alignment for most columns, except "Test Name" and "Steps" (left-aligned)
            anchor = "center" if col not in ["Test Name", "Steps"] else "w"
            self.tree.column(col, width=col_width, anchor=anchor)

        # Checkbox column setup
        self.tree.heading("Check", text="✔", anchor="center")
        self.tree.column("Check", width=50, anchor="center")

        self.tree.pack(expand=True, fill="both")
        self.tree.bind("<Double-1>", self.on_double_click)  # Enable editing on double-click

        # Buttons
        button_frame = tk.Frame(root)
        button_frame.pack(fill="x", pady=5)

        tk.Button(button_frame, text="Add Test", command=self.add_test).pack(side="left", padx=5)
        tk.Button(button_frame, text="Delete Test", command=self.delete_test).pack(side="left", padx=5)
        tk.Button(button_frame, text="Import File", command=self.import_json).pack(side="left", padx=5)
        tk.Button(button_frame, text="Export File", command=self.export_json).pack(side="left", padx=5)
        tk.Button(button_frame, text="Save Changes", command=self.save_json).pack(side="right", padx=5)

    def load_json(self, file_path):
        """ Load JSON file and return parsed data """
        with open(file_path, 'r') as file:
            return json.load(file)

    def populate_treeview(self):
        """ Populate Treeview with parsed test sequence data """
        self.tree.delete(*self.tree.get_children())  # Clear existing data

        for test in self.json_data["testlist"]["testarray"]:
            steps_str = ", ".join(test["steps"])
            check_symbol = "✅" if test["check"] == 1 else "❌"
            item_id = self.tree.insert("", "end", values=(
                check_symbol, test["id"], test["testname"],
                steps_str, test["min"], test["max"], test["units"]
            ))

            # Gray out disabled rows
            if test["check"] == 0:
                self.tree.item(item_id, tags=("disabled",))

        self.tree.tag_configure("disabled", foreground="gray")

    def on_double_click(self, event):
        """ Handle double-click events: Checkbox toggle and inline editing """
        item = self.tree.selection()[0]
        column_id = self.tree.identify_column(event.x)
        column_index = int(column_id[1:]) - 1

        if column_index == 0:  # Toggle checkbox
            self.toggle_checkbox(item)
        else:  # Edit other fields
            self.edit_treeview_cell(item, column_index)

    def toggle_checkbox(self, item):
        """ Toggle checkbox state """
        values = list(self.tree.item(item, "values"))
        current_check = 1 if values[0] == "✅" else 0
        new_check = 0 if current_check else 1
        values[0] = "✅" if new_check else "❌"

        self.tree.item(item, values=values)

        # Update JSON data
        test_id = int(values[1])
        for test in self.json_data["testlist"]["testarray"]:
            if test["id"] == test_id:
                test["check"] = new_check

        # Gray out row if disabled
        if new_check == 0:
            self.tree.item(item, tags=("disabled",))
        else:
            self.tree.item(item, tags=())

    def edit_treeview_cell(self, item, column_index):
        """ Enable inline editing of Treeview cells """
        x, y, width, height = self.tree.bbox(item, column_index)
        value = self.tree.item(item, "values")[column_index]

        self.entry_edit = tk.Entry(self.root)
        self.entry_edit.insert(0, value)
        self.entry_edit.focus()
        self.entry_edit.place(x=x, y=y + height, width=width, height=height)

        self.entry_edit.bind("<Return>", lambda e: self.update_treeview(item, column_index))
        self.entry_edit.bind("<FocusOut>", lambda e: self.entry_edit.destroy())

    def update_treeview(self, item, column_index):
        """ Update cell value in Treeview """
        new_value = self.entry_edit.get()
        values = list(self.tree.item(item, "values"))
        values[column_index] = new_value
        self.tree.item(item, values=values)
        self.entry_edit.destroy()

    def add_test(self):
        """ Add a new test to JSON and update Treeview """
        if self.json_data is None:
            messagebox.showwarning("Warning", "No test sequence loaded")
            return

        new_test = {
            "id": len(self.json_data["testlist"]["testarray"]) + 1,
            "check": 1,
            "testname": "New Test",
            "steps": ["setup(10)", "measure()"],
            "min": 0.0,
            "max": 10.0,
            "units": "V"
        }
        self.json_data["testlist"]["testarray"].append(new_test)
        self.populate_treeview()

    def delete_test(self):
        """ Remove selected test from JSON and update Treeview """
        if self.json_data is None:
            messagebox.showwarning("Warning", "No test sequence loaded")
            return

        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No test selected")
            return

        item_values = self.tree.item(selected_item, "values")
        self.json_data["testlist"]["testarray"] = [
            test for test in self.json_data["testlist"]["testarray"] if str(test["id"]) != item_values[1]
        ]
        self.populate_treeview()

    def save_json(self):
        """ Save modified test sequence back to JSON file with correct step formatting """
        if self.json_data is None:
            messagebox.showwarning("Warning", "No test sequence loaded")
            return

        if self.json_filename is None:
            messagebox.showwarning("Warning", "No file to save")
            return

        updated_tests = []
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            check_value = 1 if values[0] == "✅" else 0  # Convert checkbox symbol back to integer
            
            # Use regex to correctly extract function calls
            steps_list = re.findall(r'\b\w+\([^)]*\)', values[3])  
            steps_list = [step.strip() for step in steps_list]

            updated_tests.append({
                "id": int(values[1]),
                "check": check_value,
                "testname": values[2],
                "steps": steps_list,
                "min": float(values[4]),
                "max": float(values[5]),
                "units": values[6]
            })

        self.json_data["testlist"]["testarray"] = updated_tests

        with open(self.json_filename, 'w') as file:
            json.dump(self.json_data, file, indent=4)

        messagebox.showinfo("Success", "Test sequence saved successfully")

    def import_json(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not file_path:
            return
        self.json_filename = file_path  # Store the selected file path
        self.json_data = self.load_json(file_path)  # Load the selected file
        self.populate_treeview()
        self.update_title_on_file_upload(file_path)

    def export_json(self):
        if self.json_data is None:
            messagebox.showwarning("Warning", "No test sequence loaded")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if not file_path:
            return
        updated_tests = []
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            check_value = 1 if values[0] == "✅" else 0
            steps_list = re.findall(r'\b\w+\([^)]*\)', values[3])
            updated_tests.append({
                "id": int(values[1]),
                "check": check_value,
                "testname": values[2],
                "steps": steps_list,
                "min": float(values[4]),
                "max": float(values[5]),
                "units": values[6]
            })
        self.json_data["testlist"]["testarray"] = updated_tests
        with open(file_path, "w") as file:
            json.dump(self.json_data, file, indent=4)
        messagebox.showinfo("Success", "Test sequence exported successfully")

    def update_title_on_file_upload(self, path_name):
        # Update the window title with the selected file's name
        file_name = path_name.split("/")[-1]  # Extract file name from path
        self.root.title(f"Test Sequence Editor - File: {file_name}")

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = TestSequenceEditor(root)
    root.mainloop()
