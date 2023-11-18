from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivymd.app import MDApp

Builder.load_file('kv_MDFirst.kv')

class MyLayout(Widget):
    def __init__(self, **kwargs):
        super(MyLayout, self).__init__(**kwargs)

class MyApp(MDApp):
    def build(self):
        return MyLayout()

MyApp().run()
