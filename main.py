from kivy.lang import Builder
from kivy.app import App
import sqlite3
import subprocess
from motor_control import activate_motor
import datetime

Builder.load_file("pill_dispenser.kv")

# Initialize the database
def init_database():
    conn = sqlite3.connect('pill_dispenser.db')
    cursor = conn.cursor()
    
    # Create users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            name TEXT,
            age INTEGER,
            birthday TEXT,
            address TEXT,
            blood_type TEXT,
            symptoms TEXT
        )
    ''')

    # Create reminders table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            reminder_time TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

# Database handling class
class Database:
    @staticmethod
    def connect_db():
        return sqlite3.connect('pill_dispenser.db')

    @staticmethod
    def create_user(username, password, name, age, birthday, address, blood_type, symptoms):
        conn = Database.connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, name, age, birthday, address, blood_type, symptoms) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (username, password, name, age, birthday, address, blood_type, symptoms))
        conn.commit()
        conn.close()

    @staticmethod
    def update_user(username, **kwargs):
        conn = Database.connect_db()
        cursor = conn.cursor()
        for key, value in kwargs.items():
            cursor.execute(f"UPDATE users SET {key} = ? WHERE username = ?", (value, username))
        conn.commit()
        conn.close()

# Kivy screen classes
class LoginScreen(Screen):
    def login(self, username, password):
        conn = Database.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            App.get_running_app().root.current = 'status'
        else:
            print("Invalid credentials")  # Replace with UI feedback

class RegisterScreen(Screen):
    def register_user(self, username, password, name, age, birthday, address, blood_type, symptoms):
        Database.create_user(username, password, name, age, birthday, address, blood_type, symptoms)
        App.get_running_app().root.current = 'login'

class ProfileScreen(Screen):
    def update_profile(self, name, age, birthday, address, blood_type, symptoms):
        username = "CURRENT_USER"  # Replace with the current logged-in username
        Database.update_user(username, name=name, age=age, birthday=birthday, address=address, blood_type=blood_type, symptoms=symptoms)

class StatusScreen(Screen):
    def get_sensor_data(self, script_name):
        output = subprocess.run(["python3", f"sensor_scripts/{script_name}"], capture_output=True, text=True)
        return output.stdout.strip()

    def display_status(self):
        self.ids.temp_label.text = f"Temperature: {self.get_sensor_data('temp_sensor_code.py')} °C"
        self.ids.humid_label.text = f"Humidity: {self.get_sensor_data('humidity_sensor_code.py')} %"
        self.ids.fill_status.text = f"Container: {self.get_sensor_data('height_sensor_code.py')}"

class ReminderScreen(Screen):
    def set_reminder(self, date, time):
        reminder_time = f"{date} {time}"
        # Here you would store the reminder time and check it periodically to activate the motor
        self.schedule_reminder(reminder_time)

    def schedule_reminder(self, reminder_time):
        reminder_dt = datetime.datetime.strptime(reminder_time, "%Y-%m-%d %H:%M")
        now = datetime.datetime.now()
        if reminder_dt > now:
            time_diff = (reminder_dt - now).total_seconds()
            App.get_running_app().root.current = 'status'
            # Schedule the motor activation
            self.trigger_motor(time_diff)

    def trigger_motor(self, time_delay):
        from threading import Timer
        Timer(time_delay, activate_motor).start()

class PillDispenserApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(ProfileScreen(name='profile'))
        sm.add_widget(ReminderScreen(name='reminder'))
        sm.add_widget(StatusScreen(name='status'))
        return sm

if __name__ == '__main__':
    PillDispenserApp().run()
