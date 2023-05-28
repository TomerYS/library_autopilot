import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry('230x430')
        self.title('Room Reservation System')

        self.days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
        self.hours = [f"{i}:00" for i in range(8, 21)]

        self.label_username = tk.Label(self, text="Username:")
        self.label_password = tk.Label(self, text="Password:")
        self.label_room_list = tk.Label(self, text="Preferred Room List:")
        self.label_days_list = tk.Label(self, text="Choose days and hours:")

        self.entry_username = tk.Entry(self)
        self.entry_password = tk.Entry(self, show="*")

        self.label_username.grid(row=0, column=0, sticky='e')
        self.entry_username.grid(row=0, column=1, sticky='w')
        self.label_password.grid(row=1, column=0, sticky='e')
        self.entry_password.grid(row=1, column=1, sticky='w')
        self.label_room_list.grid(row=2, column=0, sticky='w', columnspan=2)
        self.label_days_list.grid(row=5, column=0, sticky='w', columnspan=2)

        self.room_listbox = tk.Listbox(self, selectmode=tk.SINGLE, width=10, height=10)
        for room in [13,14,15,16,18,19,108,109,110,111]:
            self.room_listbox.insert(tk.END, room)
        self.room_listbox.grid(row=3, column=0, columnspan=2)

        self.button_up = tk.Button(self, text="Move Up", command=self.move_up, width=10)
        self.button_down = tk.Button(self, text="Move Down", command=self.move_down, width=10)
        self.button_up.grid(row=4, column=0)
        self.button_down.grid(row=4, column=1)

        self.day_vars = []
        self.comboboxes = []
        for i, day in enumerate(self.days, start=6):
            var = tk.IntVar()
            chk = tk.Checkbutton(self, text=day, variable=var)
            chk.grid(row=i, column=0, sticky='w')
            
            combobox = ttk.Combobox(self, values=self.hours, state='readonly', width=5)
            combobox.set(self.hours[0])  # set the default value
            combobox.grid(row=i, column=1, sticky='e')
            
            self.day_vars.append(var)
            self.comboboxes.append(combobox)

        self.submit_button = tk.Button(self, text="Submit", command=self.submit, width=10)
        self.submit_button.grid(row=i+1, column=0, columnspan=2)

    def move_up(self):
        selected_rooms = self.room_listbox.curselection()
        for selected_room in selected_rooms:
            if selected_room > 0:
                temp = self.room_listbox.get(selected_room)
                self.room_listbox.delete(selected_room)
                self.room_listbox.insert(selected_room - 1, temp)
                self.room_listbox.select_clear(selected_room)
                self.room_listbox.select_set(selected_room - 1)

    def move_down(self):
        selected_rooms = self.room_listbox.curselection()
        for selected_room in reversed(selected_rooms):
            if selected_room < self.room_listbox.size() - 1:
                temp = self.room_listbox.get(selected_room)
                self.room_listbox.delete(selected_room)
                self.room_listbox.insert(selected_room + 1, temp)
                self.room_listbox.select_clear(selected_room)
                self.room_listbox.select_set(selected_room + 1)

    def submit(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        room_list = [self.room_listbox.get(i) for i in range(self.room_listbox.size())]

        # print("Username: ", username)
        # print("Password: ", password)
        # print("Preferred Rooms: ", room_list)

        selected_days_hours = [(day, combobox.get()) for day, var, combobox in zip(self.days, self.day_vars, self.comboboxes) if var.get()]
        # print("Selected Days and Hours: ", selected_days_hours)

        if len(selected_days_hours) > 4:
            messagebox.showinfo("Submission Error", "You can select up to 4 days only!")
        elif len(selected_days_hours) == 0:
            messagebox.showinfo("Submission Error", "You must select at least 1 day!")
        elif len(username) == 0 or len(password) == 0:
            messagebox.showinfo("Submission Error", "You must enter username and password!")
        else:
            messagebox.showinfo("Submission Successful", "Your data has been submitted successfully!")
            self.result = username, password, room_list, selected_days_hours
            self.destroy()

def main():
    app = Application()
    app.mainloop()
    return app.result  # return the result

if __name__ == "__main__":
    print(main())  # print the result