import tkinter as tk
from tkinter import ttk
import random
import json
import re
#from Drivers.power_supply import PowerSupply - test afterwards

class TestEngine:
    def __init__(self, sequence, treeview):
        self.sequence = sequence
        self.treeview = treeview
        self.results = []
        #self.power_supply = PowerSupply()
        #self.power_supply.open_connection("GPIB::1")  # Example resource name
        #self.command_registry = self.power_supply.register_commands()
        self.update_treeview()

    

    def run_test(self, test, row_id):
        if test['check'] == 0:
            self.treeview.item(row_id, values=(test['id'], '✗', test['testname'], test['min'], test['max'], "", test['units'], "SKIPPED"))
            return

        print(f"Running test: {test['testname']}")
        for step in test['steps']:
            self.execute_step(step)

        measured_value = random.uniform(test['min'] - 1, test['max'] + 1)
        print(f"Measured value: {measured_value} {test['units']}")
        pass_fail = self.check_limits(measured_value, test)

        check_icon = '✔' if test['check'] == 1 else '✗'
        self.treeview.item(row_id, values=(test['id'], check_icon, test['testname'], test['min'], test['max'], measured_value, test['units'], pass_fail))

        self.results.append({
            "testname": test['testname'],
            "measured_value": measured_value,
            "pass_fail": pass_fail,
            "units": test['units']
        })

    def execute_step(self, step):
        print(f"Executing step: {step}")
        command_match = re.match(r'(\w+)\((.*?)\)', step)
        if command_match:
            command, params = command_match.groups()
            params = [int(p.strip()) for p in params.split(',') if p.strip()]

            if command in self.command_registry:
                try:
                    self.command_registry[command](*params)
                except TypeError as e:
                    print(f"Parameter mismatch for {command}: {e}")
                except Exception as e:
                    print(f"Error executing {command}: {e}")

    def check_limits(self, value, test):
        return 'Pass' if test['min'] <= value <= test['max'] else 'Fail'

    def run_sequence(self):
        print(f"Running test sequence: {self.sequence['test sequence name']} (Version: {self.sequence['version']})")
        for test in self.sequence['testlist']['testarray']:
            for item in self.treeview.get_children():
                if self.treeview.item(item, 'values')[2] == test['testname']:
                    self.run_test(test, item)
        self.print_results()
        self.power_supply.close_connection()

    def print_results(self):
        print("\nTest Results:")
        for result in self.results:
            print(f"{result['testname']}: {result['pass_fail']} (Measured: {result['measured_value']} {result['units']})")

    def update_treeview(self):
        for test in self.sequence['testlist']['testarray']:
            check_icon = '✔' if test['check'] == 1 else '✗'
            status = "" if test['check'] == 1 else "SKIPPED"
            row = self.treeview.insert("", "end", values=(test['id'], check_icon, test['testname'], test['min'], test['max'], "", test['units'], status), tags=('active' if test['check'] == 1 else 'disabled'))


class Application(tk.Tk):
    def __init__(self, sequence):
        super().__init__()
        self.title("Test Sequence")
        self.geometry("1300x400")

        self.treeview = ttk.Treeview(self, columns=("id", "Check", "Test Name", "Min", "Max", "Measured Value", "Units", "Status"), show="headings")

        self.treeview.heading("id", text="ID", anchor='center')
        self.treeview.heading("Check", text="Check", anchor='center')
        self.treeview.heading("Test Name", text="Test Name", anchor='w')  # Left aligned
        self.treeview.heading("Min", text="Min", anchor='center')
        self.treeview.heading("Max", text="Max", anchor='center')
        self.treeview.heading("Measured Value", text="Measured Value", anchor='center')
        self.treeview.heading("Units", text="Units", anchor='center')
        self.treeview.heading("Status", text="Status", anchor='center')

        for col in ("id", "Check", "Test Name", "Min", "Max", "Measured Value", "Units", "Status"):
            self.treeview.column(col, anchor='center', width=150)

        self.treeview.column("Test Name", anchor='w', width=250)

        self.treeview.pack(fill=tk.BOTH, expand=True)

        self.engine = TestEngine(sequence, self.treeview)
        self.treeview.tag_configure('disabled', foreground='gray')

        self.run_button = tk.Button(self, text="Run Test Sequence", command=self.engine.run_sequence)
        self.run_button.pack(pady=10)

    @staticmethod
    def load_sequence_from_file(filename):
        with open(filename, 'r') as file:
            sequence = json.load(file)
        return sequence

sequence_file = "test_seq2.json"
try:
    sequence = Application.load_sequence_from_file(sequence_file)
    app = Application(sequence)
    app.mainloop()
except FileNotFoundError:
    print(f"Error: The file {sequence_file} was not found.")
except json.JSONDecodeError:
    print(f"Error: Failed to parse the JSON file {sequence_file}.")

