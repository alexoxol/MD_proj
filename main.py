from kivy.config import Config
from kivy.metrics import dp
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
import sqlite3
import requests

def winComb(*cells):
    return [True if i in cells else False for i in range(9)]

class GameWindow(Screen, MDFloatLayout):
    name = "game"
    turn = "X"
    cells_x = [False for _ in range(9)]
    cells_o = [False for _ in range(9)]
    curr_cells = cells_x
    btns = []
    myLabel = None
    # Выигрышные комбинации
    wins = [
        winComb(0,1,2),
        winComb(3,4,5),
        winComb(6,7,8),
        winComb(0,3,6),
        winComb(1,4,7),
        winComb(2,5,8),
        winComb(0,4,8),
        winComb(2,4,6)
    ]

    def on_pre_enter(self, *args):
        # Открыто окно. Рестарт или продолжение?
        records = self.parent.db_select("""
            SELECT * FROM cur_game
        """)
        if len(records) == 0:
            # Удаляем из БД
            self.parent.db_exec("""
                DELETE FROM cur_game
            """)
            self.restart()
        else:
            # Восстанавливаем состояние игры
            self.continueGame(records[0])

    def continueGame(self, rec):
        self.turn = rec[0]
        self.myLabel.text = f"Первым ходит {self.turn}"
        self.cells_x = eval(rec[1])
        self.cells_o = eval(rec[2])
        self.curr_cells = self.cells_x if self.turn == "X" else self.cells_o
        print(self.curr_cells)
        for i, btn in enumerate(self.btns):
            # Красим доску
            if self.cells_x[i]:
                btn.text = "X"
                btn.disabled = True
            elif self.cells_o[i]:
                btn.text = "O"
                btn.disabled = True
            else:
                btn.text = ""
                btn.disabled = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        myGrid = MDGridLayout()
        myGrid.cols = 3
        myGrid.rows = 3
        myGrid.md_bg_color = "white"
        myGrid.spacing = 2
        myGrid.size_hint = (None, None)
        scr_w = Config.getint('graphics', 'width')
        grid_w = scr_w * 0.9
        myGrid.height = grid_w # dp(300)
        myGrid.width = myGrid.height
        myGrid.pos_hint = {"center_x": 0.5, "center_y": 0.6}
        # Кнопки на грид
        for i in range(9):
            btn = Button(text = "")
            btn.font_size = "45sp"
            btn.tag = i
            # Добавляем в список кнопок
            self.btns.append(btn)
            btn.bind(on_press = self.presser)
            myGrid.add_widget(btn)
        self.add_widget(myGrid)

        # Метка
        self.myLabel = MDLabel(text = "Первым ходит X...", halign = "center", pos_hint = {"center_y": 0.25})
        self.myLabel.font_size = "32sp"
        self.ids["score_label"] = self.myLabel
        self.add_widget(self.myLabel)

        # Кнопка рестарт
        restartButton = MDRaisedButton(text = "Рестарт!", pos_hint = {"center_x": 0.5, "center_y": 0.15})
        self.ids["restart"] = restartButton
        restartButton.bind(on_press = self.restart)
        self.add_widget(restartButton)

    def presser(self, btn):
        btn.text = self.turn
        btn.disabled = True
        # Меняем текущий блок ячеек
        self.curr_cells = self.cells_x if self.turn == "X" else self.cells_o
        # Проставляем в этот блок True
        self.curr_cells[btn.tag] = True
        # Удаляем из БД
        self.parent.db_exec("""
            DELETE FROM cur_game
        """)
        # Провереям на победу
        win_index = self.checkForWin(self.curr_cells)
        if win_index >= 0:
            # Есть победитель
            self.myLabel.text = f"Победитель: {self.turn}"
            # Затемняем все кнопки
            for btn in self.btns:
                btn.disabled = True
        elif win_index == -2:
            # Ничья
            self.myLabel.text = f"Ничья!"
            # Затемняем все кнопки
            for btn in self.btns:
                btn.disabled = True
        else:
            # Нет победителя
            self.turn = "X" if self.turn == "O" else "O"
            self.myLabel.text = f"Ходит: {self.turn}"
            # Сохраняем в БД
            conn = sqlite3.connect("titactoe.db")
            cur = conn.cursor()
            turn = self.turn
            cells_x = str(self.cells_x)
            cells_o = str(self.cells_o)
            self.parent.db_exec(f"""
                INSERT into cur_game(turn, cells_x, cells_o) VALUES ('{turn}', '{cells_x}', '{cells_o}')
            """)
        r = requests.get("http://82.202.204.242:5000/db")
        self.ids['restart'].text = str(r.status_code)
        # print("Status Code", r.status_code)
        # print("JSON Response ", r.json())

    def checkForWin(self, cells):
        # Возвращаем индекс совпавшей линии, или -1 (никто не выиграл, продолжаем), или -2 (ничья)
        for i, win in enumerate(self.wins):
            comb_len = len([True for x, w in zip(cells, win) if x == w == True])
            if comb_len == 3:
                # Красим выигравшие ячейки
                winButtons = [btn for (btn, status) in zip(self.btns, win) if status]
                for btn in winButtons:
                    btn.color = "red"
                return i
        if sum(self.cells_x) + sum(self.cells_o) == 9:
            # Ничья
            return -2
        return -1

    def restart(self, instance = None):
        self.turn = "X"
        self.myLabel.text = f"Первым ходит {self.turn}"
        self.cells_x = [False for _ in range(9)]
        self.cells_o = [False for _ in range(9)]
        self.curr_cells = self.cells_x
        for btn in self.btns:
            btn.text = ""
            btn.color = "white"
            btn.disabled = False

class MainWindow(Screen, MDFloatLayout):
    name = "main"
    myFloatLayout = None
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        lblTitle = MDLabel(text = "Крестики-нолики", halign = "center")
        lblTitle.pos_hint = {"center_x": 0.5, "center_y": 0.8}
        lblTitle.font_size = "36sp"
        self.add_widget(lblTitle)

        btnStart = MDRaisedButton(text="Старт")
        btnStart.font_size = "26sp"
        btnStart.size_hint = (0.3, 0.1)
        btnStart.pos_hint =  {"center_x": 0.5, "y": 0.58}
        btnStart.bind(on_press = self.start)
        self.add_widget(btnStart)

    def on_pre_enter(self, *args):
        # Добавляем кнопку "Продолжить" (в on_pre_enter, потому что в __init__ не видно self.parent)
        records = self.parent.db_select("""
            SELECT * FROM cur_game
        """)
        if len(records) > 0:
            btnCont = MDRaisedButton(text="Продолжить")
            btnCont.font_size = "26sp"
            btnCont.size_hint = (0.3, 0.1)
            btnCont.pos_hint = {"center_x": 0.5, "y": 0.42}
            btnCont.bind(on_press=self.cont)
            self.add_widget(btnCont)

    def start(self, btn):
        # Очищаем БД
        self.parent.db_exec("""
            DELETE FROM cur_game
        """)
        self.parent.current = "game"

    def cont(self, btn):
        self.parent.current = "game"

class WindowManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Создаем таблицу
        self.db_exec("""
            CREATE TABLE if not exists cur_game(
                turn text,
                cells_x text,
                cells_o text
            )
        """)
        self.add_widget(MainWindow())
        self.add_widget(GameWindow())
        self.current = "main"

    def db_exec(self, sql):
        conn = sqlite3.connect("titactoe.db")
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        conn.close()

    def db_select(self, sql):
        conn = sqlite3.connect("titactoe.db")
        cur = conn.cursor()
        cur.execute(sql)
        res = cur.fetchall()
        conn.close()
        return res

class MyApp(MDApp):
    winman = None
    def build(self):
        self.winman = WindowManager()
        return self.winman

MyApp().run()
