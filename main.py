from kivy.lang import Builder
from kivymd.app import MDApp
import sqlite3

class MyApp(MDApp):
    conn = None
    def build(self):
        self.theme_cls.theme_style = "Dark" # or "Light/Dark"
        self.theme_cls.primary_palette = "BlueGray"

        # Connection
        self.conn = sqlite3.connect("first_db.db")
        # Cursor
        cur = self.conn.cursor()
        # Create table
        cur.execute("""
            CREATE TABLE if not exists customers(
                name text
            )
        """)
        # Commit changes
        self.conn.commit()
        # Close connection
        # self.conn.close()

        return Builder.load_file('kv.kv')

    def submit(self):
        # Cursor
        cur = self.conn.cursor()
        # Add a record
        cur.execute(f"INSERT into customers VALUES ('{self.root.ids.word_input.text}')")
        # Commit changes
        self.conn.commit()

        self.root.ids.word_label.text = "Record added."
        self.root.ids.word_input.text = ""

    def show(self):
        # Cursor
        cur = self.conn.cursor()
        # Show records
        cur.execute("""
            SELECT * FROM customers
        """)
        records = cur.fetchall()
        word = ""
        for rec in records:
            word += f"\n{rec[0]}"
        self.root.ids.word_label.text = word

MyApp().run()
