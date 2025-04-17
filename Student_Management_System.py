import tkinter as tk
from tkinter import messagebox, ttk
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class StudentManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")

        # Input Frame
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10)

        self.validate_id = root.register(self.validate_integer)

        # Labels and Entries
        labels = ["Student ID", "Name", "Age", "Gender", "CGPA"]
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(self.frame, text=label).grid(row=i, column=0)
            if label == "Gender":
                entry = ttk.Combobox(self.frame, values=["Male", "Female", "Other"])
            else:
                entry = tk.Entry(self.frame)
                if label == "Student ID":
                    entry.config(validate="key", validatecommand=(self.validate_id, '%P'))
            entry.grid(row=i, column=1)
            self.entries[label] = entry

        # Buttons
        buttons = [
            ("Add Student", self.add_student),
            ("Search", self.search_student),
            ("Update", self.update_student),
            ("Delete", self.delete_student),
            ("Export CSV", self.export_to_csv),
            ("Export PDF", self.export_to_pdf),
            ("Show All", self.show_all)
        ]

        for i, (text, cmd) in enumerate(buttons):
            tk.Button(self.frame, text=text, command=cmd).grid(row=5 + i // 2, column=i % 2, pady=5)

        # Treeview
        self.tree = ttk.Treeview(self.root, columns=("ID", "Name", "Age", "Gender", "CGPA"), show='headings')
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(pady=10)

        self.show_all()

    def validate_integer(self, val):
        return val.isdigit() or val == ""

    def get_entry_data(self):
        return [self.entries["Student ID"].get().strip(),
                self.entries["Name"].get().strip(),
                self.entries["Age"].get().strip(),
                self.entries["Gender"].get().strip(),
                self.entries["CGPA"].get().strip()]

    def clear_entries(self):
        for entry in self.entries.values():
            if isinstance(entry, ttk.Combobox):
                entry.set('')
            else:
                entry.delete(0, tk.END)

    def show_all(self):
        self.tree.delete(*self.tree.get_children())
        try:
            with open('students.csv', 'r') as f:
                for row in csv.reader(f):
                    if row:
                        self.tree.insert("", tk.END, values=row)
        except FileNotFoundError:
            pass

    def add_student(self):
        data = self.get_entry_data()
        if all(data):
            with open('students.csv', 'a', newline='') as f:
                csv.writer(f).writerow(data)
            messagebox.showinfo("Success", "Student added.")
            self.clear_entries()
            self.show_all()
        else:
            messagebox.showwarning("Input Error", "Please fill all fields.")

    def search_student(self):
        sid = self.entries["Student ID"].get().strip()
        if not sid:
            messagebox.showwarning("Input Error", "Enter Student ID to search.")
            return
        self.tree.delete(*self.tree.get_children())
        found = False
        try:
            with open('students.csv', 'r') as f:
                for row in csv.reader(f):
                    if row and row[0] == sid:
                        self.tree.insert("", tk.END, values=row)
                        found = True
                        break
            if not found:
                messagebox.showinfo("Not Found", "Student ID not found.")
        except FileNotFoundError:
            messagebox.showerror("Error", "File not found.")

    def update_student(self):
        sid = self.entries["Student ID"].get().strip()
        updated = False
        data = self.get_entry_data()
        if not all(data):
            messagebox.showwarning("Input Error", "Fill in all fields to update.")
            return

        try:
            rows = []
            with open('students.csv', 'r') as f:
                for row in csv.reader(f):
                    if row and row[0] == sid:
                        rows.append(data)
                        updated = True
                    else:
                        rows.append(row)
            if updated:
                with open('students.csv', 'w', newline='') as f:
                    csv.writer(f).writerows(rows)
                messagebox.showinfo("Updated", f"Student ID {sid} updated.")
                self.clear_entries()
                self.show_all()
            else:
                messagebox.showinfo("Not Found", "Student ID not found.")
        except FileNotFoundError:
            messagebox.showerror("Error", "File not found.")

    def delete_student(self):
        sid = self.entries["Student ID"].get().strip()
        deleted = False
        try:
            rows = []
            with open('students.csv', 'r') as f:
                for row in csv.reader(f):
                    if row and row[0] != sid:
                        rows.append(row)
                    elif row and row[0] == sid:
                        deleted = True

            with open('students.csv', 'w', newline='') as f:
                csv.writer(f).writerows(rows)

            if deleted:
                messagebox.showinfo("Deleted", f"Student ID {sid} deleted.")
            else:
                messagebox.showinfo("Not Found", "Student ID not found.")

            self.clear_entries()
            self.show_all()
        except FileNotFoundError:
            messagebox.showerror("Error", "File not found.")

    def export_to_csv(self):
        with open('students_export.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            for item in self.tree.get_children():
                writer.writerow(self.tree.item(item)["values"])
        messagebox.showinfo("Exported", "Data exported to students_export.csv")

    def export_to_pdf(self):
        c = canvas.Canvas("students_export.pdf", pagesize=letter)
        c.setFont("Helvetica", 12)
        c.drawString(50, 750, "Student List")
        y = 730
        for item in self.tree.get_children():
            row = self.tree.item(item)["values"]
            c.drawString(50, y, f"ID: {row[0]}, Name: {row[1]}, Age: {row[2]}, Gender: {row[3]}, CGPA: {row[4]}")
            y -= 20
        c.save()
        messagebox.showinfo("Exported", "Data exported to students_export.pdf")

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManagementSystem(root)
    root.mainloop()
