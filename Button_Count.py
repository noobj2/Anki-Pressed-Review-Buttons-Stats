#// auth_ Mohamad Janati
#// AmirHassan Asvadi ;)
#// Copyright (c) 2020 Mohamad Janati (freaking stupid, right? :|)

from os.path import  join, dirname
from aqt import mw
from aqt.qt import *
import time
from aqt.utils import showInfo

def refreshConfig():
    global C_buttonCount_type, C_buttonCount_scope, C_buttonCount_timeSpinbox, C_buttonCount_period

    config = mw.addonManager.getConfig(__name__)

    C_buttonCount_type = config['ButtonCount_ Type']
    C_buttonCount_scope = config['ButtonCount_ Scope']
    C_buttonCount_timeSpinbox = config['ButtonCount_ Time Spinbox']
    C_buttonCount_period = config['ButtonCount_ Period']

class SettingsMenu(QDialog):
    refreshConfig()
    addon_path = dirname(__file__)
    images = join(addon_path, 'images')
    def __init__(self, parent=None):
        super(SettingsMenu, self).__init__(parent)
        self.mainWindow()

    def mainWindow(self):
        images = self.images
        self.createFirstTab()
        self.loadCurrent()

        tabs = QTabWidget()
        tabs.addTab(self.tab1, "Stats")

        vbox = QVBoxLayout()
        vbox.addWidget(tabs)

        self.setLayout(vbox)
        self.setWindowTitle("Pressed Buttons Stats")
        self.setWindowIcon(QIcon(images + "/icon.png"))

    def createFirstTab(self):
        images = self.images
        decks = mw.col.decks.all()
        deckname_list = []
        deckid_list = []
        for deck in decks:
            deck_name = deck["name"]
            deck_id = deck["id"]
            deckname_list.append(deck_name)
            deckid_list.append("({})".format(deck_id))
        refreshConfig()
        selected_type = C_buttonCount_type
        selected_scope = C_buttonCount_scope
        selected_time = C_buttonCount_timeSpinbox
        if C_buttonCount_period == 1:
            selected_time *= 60
        elif C_buttonCount_period == 2:
            selected_time *= 60*24
        elif C_buttonCount_period == 3:
            selected_time *= 60*24*7
        elif C_buttonCount_period == 4:
            selected_time *= 60*24*30
        elif C_buttonCount_period == 5:
            selected_time *= 60*24*30*12
        today = time.time()
        limit = ((today*1000) - (selected_time*60*1000))
        if selected_type == 0:
            type = ""
        elif selected_type == 1:
            type = "and type = 0"
        elif selected_type == 2:
            type = "and type = 1"
        elif selected_type == 3:
            type = "and type = 2"
        elif selected_type == 4:
            type = "and type = 3"
        elif selected_type == 5:
            type = "and (type = 0 or type = 2)"
        if selected_scope == 0:
            scope = ""
        else:
            scope = "and cid in (select id from cards where did in {})".format(deckid_list[int(selected_scope) - 1])
        pressed_again = mw.col.db.scalar("""select sum(case when ease = 1 then 1 else 0 end) from revlog where id  > {} {} {}""".format(limit,type, scope))
        pressed_hard = mw.col.db.scalar("""select sum(case when ease = 2 then 1 else 0 end) from revlog where id  > {} {} {}""".format(limit, type, scope))
        pressed_good = mw.col.db.scalar("""select sum(case when ease = 3 then 1 else 0 end) from revlog where id  > {} {} {}""".format(limit, type, scope))
        pressed_easy = mw.col.db.scalar("""select sum(case when ease = 4 then 1 else 0 end) from revlog where id  > {} {} {}""".format(limit, type, scope))
        if not pressed_again:
            pressed_again = 0
        if not pressed_hard:
            pressed_hard = 0
        if not pressed_good:
            pressed_good = 0
        if not pressed_easy:
            pressed_easy = 0
        pressed_all = pressed_again + pressed_hard + pressed_good + pressed_easy
        if not pressed_all:
            pressed_all = 1
        if pressed_again or pressed_hard or pressed_good or pressed_easy:
            buttonsCount_text = """<style>
            table, th, td {
              border: 1px solid black;
              border-collapse: collapse;
            }
            </style>
            """
            buttonsCount_text += """<table cellpadding=5 width=100%>"""
            buttonsCount_text += """<tr>"""
            buttonsCount_text += """<th width=100 align=left>{}</th><th width=100 align=left>{}</th><th width=100 align=left>{}</th>""".format("button", "Count", "Percent")
            buttonsCount_text += """</tr>"""
            buttonsCount_text += """<tr>"""
            buttonsCount_text += """<td>{}</td><td>{}</td><td>{:.2f}%</td><""".format("Again", pressed_again, float((pressed_again/pressed_all)*100))
            buttonsCount_text += """</tr>"""
            buttonsCount_text += """<tr>"""
            buttonsCount_text += """<td>{}</td><td>{}</td><td>{:.2f}%</td>""".format("Hard", pressed_hard, float((pressed_hard/pressed_all)*100))
            buttonsCount_text += """</tr>"""
            buttonsCount_text += """<tr>"""
            buttonsCount_text += """<td>{}</td><td>{}</td><td>{:.2f}%</td>""".format("Good", pressed_good, float((pressed_good/pressed_all)*100))
            buttonsCount_text += """</tr>"""
            buttonsCount_text += """<tr>"""
            buttonsCount_text += """<td>{}</td><td>{}</td><td>{:.2f}%</td>""".format("Easy", pressed_easy, float((pressed_easy/pressed_all)*100))
            buttonsCount_text += """</tr>"""
            buttonsCount_text += """</table>"""
        else:
            buttonsCount_text = "No reviews found."

        reviewButton_designs = QLabel()
        reviewButton_designs.setText(buttonsCount_text)
        reviewButtonDesigns_scroll = QScrollArea()
        reviewButtonDesigns_scroll.setWidget(reviewButton_designs)
        find_button = QPushButton("Find")
        for_label = QLabel("Reviews for")
        self.type_select = QComboBox()
        self.type_select.addItems([ "All Cards", "Learn Cards", "Review Cards", "re-Learn Cards", "Cram Cards", "Learn + re-Learn Cards"])
        self.scope_select = QComboBox()
        in_label = QLabel("in")
        self.scope_select.addItems(["Whole Collection"])
        self.scope_select.addItems(deckname_list)
        past_title = QLabel("in past")
        self.time_spinbox = QSpinBox()
        self.time_spinbox.setMinimum(0)
        self.period_select = QComboBox()
        self.period_select.addItems(["Minutes", "Hours", "Days", "Weeks", "Months", "Years"])
        bottom_holder = QHBoxLayout()
        bottom_holder.addWidget(find_button)
        bottom_holder.addWidget(for_label)
        bottom_holder.addWidget(self.type_select)
        bottom_holder.addWidget(in_label)
        bottom_holder.addWidget(self.scope_select)
        bottom_holder.addWidget(past_title)
        bottom_holder.addWidget(self.time_spinbox)
        bottom_holder.addWidget(self.period_select)
        find_button.clicked.connect(lambda: self.onFind())

        layout = QVBoxLayout()
        layout.addWidget(reviewButtonDesigns_scroll)
        layout.addLayout(bottom_holder)
        self.tab1 = QWidget()
        self.tab1.setLayout(layout)

    def loadCurrent(self):
        self.type_select.setCurrentIndex(C_buttonCount_type)
        self.scope_select.setCurrentIndex(C_buttonCount_scope)
        self.time_spinbox.setValue(int(C_buttonCount_timeSpinbox))
        self.period_select.setCurrentIndex(C_buttonCount_period)

    def onFind(self):
        conf = {
        "ButtonCount_ Type": self.type_select.currentIndex(),
        "ButtonCount_ Scope": self.scope_select.currentIndex(),
        "ButtonCount_ Time Spinbox": self.time_spinbox.value(),
        "ButtonCount_ Period": self.period_select.currentIndex(),
      }
        mw.addonManager.writeConfig(__name__, conf)
        self.accept()
        refreshConfig()
        SettingsMenu().exec()

def open_settings(self):
    settings = SettingsMenu()
    settings.exec()

def no_config():
    showInfo("No Config available")
    refreshConfig()
    SettingsMenu().exec()


def setupMenu():
    settings = QAction('Pressed Review Button &Stats', mw)
    settings.triggered.connect(open_settings)
    mw.form.menuTools.addAction(settings)
setupMenu()
mw.addonManager.setConfigAction(__name__, no_config)
