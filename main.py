import queue
import random
import sys
import pygame
from PyQt5 import uic
from PyQt5.QtCore import QParallelAnimationGroup, QPropertyAnimation, QTimer, QSize, QEasingCurve, QThread, QRect
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import *
from load_questions import loadEasy, loadMedium, loadHard
pygame.mixer.init()

#----------------------------------------------------------------------------------------------------------------------------------------------
class MainScreen(QMainWindow):
    """ The first screen you see when you launch the app"""
    def __init__(self):
        super().__init__()
        
    def initUI(self):
        uic.loadUi('ux/mainscreen.ui', self)
        pygame.mixer.music.load('assets/background_music.mp3')
        self.story.close()
        self.play.clicked.connect(self.prologue)
        pygame.mixer.music.play(-1, 0.0)

    def prologue(self):
        self.story.show()
        self.anim = QPropertyAnimation(self.story, b'size')
        self.anim.setDuration(1000)
        self.anim.setStartValue(QSize(0,0))
        self.anim.setEndValue(QSize(850, 450))
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim.start()
        animSound.play()

        self.anim.finished.connect(self.start)

    def start(self):
        lbl = QLabel()
        self.msg_lst = ['You are a archeologist who was wandering around a hidden tomb somewhere in the middle of a jungle |',
                        'You got lost and accidentally fell into a pit and ended up in the lost city of Oz |',
                        'The only way to return home is to seek the help of the Guru of Oz |',
                        "However, to meet the Guru you have to pass the Guru's test |",
                        'If you pass you go home, if you fail you remain in Oz for eternity !'
                        ] 
        self.message = queue.Queue()
        for char in self.msg_lst.pop(0):
            self.message.put(char)
        self.time = QTimer(self)
        self.time.timeout.connect(self.place)
        self.time.start(50)
        self.skip.clicked.connect(self.skipAbout)
    
    def place(self):
        if not self.message.empty():
            text = self.msg_lbl.text()
            self.msg_lbl.setText(text + self.message.get())
        else:
            try:
                QThread.sleep(2)
                for char in self.msg_lst.pop(0):
                    self.message.put(char)
                self.msg_lbl.clear()
            except IndexError:
                self.time.stop()

                self.anim = QPropertyAnimation(self.ready, b'geometry')
                self.anim.setDuration(1000)
                self.anim.setStartValue(QRect(310, 700, 230, 60))
                self.anim.setEndValue(QRect(310, 360, 230, 60))
                self.anim.setEasingCurve(QEasingCurve.InOutQuad)
                self.anim.start()
                
                self.skip.close()
                self.ready.setEnabled(True)
                self.ready.clicked.connect(self.gotogame)
    
    def skipAbout(self):
        self.time.stop()
        self.gotogame()

    def gotogame(self):
        difficulty = None
        for b in [self.easy, self.medium, self.hard]:
            if b.isChecked():
                difficulty = b.text()   
        game.difficulty = difficulty
        widget.addWidget(game)
        widget.setCurrentWidget(game)
        game.initUI()
        widget.removeWidget(main)

#----------------------------------------------------------------------------------------------------------------------------------------------
class GameScreen(QMainWindow):
    """ The game screen"""
    def __init__(self, difficulty):
        super().__init__()
        self.difficulty = difficulty
    
    def initUI(self):
        uic.loadUi('ux/gameScreen.ui', self)
        pygame.mixer.music.fadeout(100)
        pygame.mixer.music.load('assets/game_sound.mp3')
        pygame.mixer.music.play(-1, 0.0)
        
        self.breakout()
        self.chances = 3
        self.message.close()
        self.option_btns = [self.a, self.b, self.c, self.d]
        
        self.generateQuestions()
        for btn in self.option_btns:
            btn.clicked.connect(self.chosen)
        
    def breakout(self):
        self.anim = QPropertyAnimation(self.story, b'size')
        self.anim.setDuration(1000)
        self.anim.setStartValue(QSize(850,450))
        self.anim.setEndValue(QSize(0, 0))
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim.start()
        animSound.play()

    def generateQuestions(self):
        bank = None
        self.number = 10
        if self.difficulty == 'Easy':
            bank = loadEasy()
            self.diff_lbl.setText('Easy')
            self.diff_lbl.setStyleSheet("font: 15pt 'Courier';color: white;background-color: rgb(0, 170, 0);border-radius: 15")
        elif self.difficulty == 'Medium':
            bank = loadMedium()
            self.diff_lbl.setText('Medium')
            self.diff_lbl.setStyleSheet("font: 15pt 'Courier';color: white;background:rgb(0, 85, 255);border-radius: 15")
        else:
            bank = loadHard()
            self.diff_lbl.setText('Hard')
            self.diff_lbl.setStyleSheet("font: 15pt 'Courier';color: white;background:rgb(255, 41, 34);border-radius: 15")

        self.questions = []
        # This is to make sure we dont pick the same questions
        while len(self.questions) < self.number:
            choice = random.choice(bank)
            if choice not in self.questions:
                self.questions.append(choice)
        random.shuffle(self.questions)

        self.current = 0
        self.displayQuestion()
        
    def displayQuestion(self):
        question = self.questions[self.current]['question']
        options = self.questions[self.current]['options']
        self.question_lbl.setText(question)

        for i in range(len(self.option_btns)):
            if len(options[i]) >= 45:
                self.option_btns[i].setFont(QFont('Courier', 8))
            elif len(options[i]) >= 30:
                self.option_btns[i].setFont(QFont('Courier', 10))
            else:
                self.option_btns[i].setFont(QFont('Courier', 14))

            self.option_btns[i].setText(options[i])

    def chosen(self):
        sender = self.sender()
        if sender.text() == self.questions[self.current]['answer']:
            self.current += 1
            if self.checkEnd():
                return
            self.displayQuestion()
        else:
            self.checkLose()

    def checkLose(self):
        if self.chances:
            self.message.show()

            self.anim = QPropertyAnimation(self.message, b'geometry')
            self.anim.setDuration(500)
            self.anim.setStartValue(QRect(160, 700, 680, 400))
            self.anim.setEndValue(QRect(160, 50, 680, 400))
            self.anim.setEasingCurve(QEasingCurve.InOutQuad)
            self.anim.start()
            

            self.retry_btn.clicked.connect(lambda: self.message.close())
            self.chances -= 1
        else:
            widget.addWidget(game_lost)
            widget.setCurrentWidget(game_lost)
            widget.removeWidget(game)
            game_lost.initUI()

    def checkEnd(self):
        if self.current == self.number-1:
            widget.addWidget(game_won)
            widget.setCurrentWidget(game_won)
            widget.removeWidget(game)
            game_won.initUI()
            return True
        return False

#----------------------------------------------------------------------------------------------------------------------------------------------
class GameWon(QMainWindow):
    """ The screen when you win the game"""
    def __init__(self):
        super().__init__()
        
    def initUI(self):
        uic.loadUi('ux/winscreen.ui', self)
        pygame.mixer.music.fadeout(100)
        pygame.mixer.music.load('assets/passed.mp3')
        pygame.mixer.music.play(0,0.0)
        self.replay.clicked.connect(self.gotomain)

    def gotomain(self):
        widget.addWidget(main)
        widget.setCurrentWidget(main)
        widget.removeWidget(game_won)
        main.initUI()

#----------------------------------------------------------------------------------------------------------------------------------------------
class GameLost(QMainWindow):
    """ The screen when you lose the game"""
    def __init__(self):
        super().__init__()
    
    def initUI(self):
        uic.loadUi('ux/losescreen.ui', self)
        pygame.mixer.music.fadeout(100)
        pygame.mixer.music.load('assets/' + random.choice(['laugh', 'laugh2']) + '.mp3')
        pygame.mixer.music.play(0, 0.0)
        self.replay.clicked.connect(self.gotomain)
    
    def gotomain(self):
        widget.addWidget(main)
        widget.setCurrentWidget(main)
        widget.removeWidget(game_lost)
        main.initUI()

#===================================================================================================================================================
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName('The Guru of Oz')
    app.setWindowIcon(QIcon('assets/wizard.png'))
    animSound= pygame.mixer.Sound('assets/effect.mp3')

    # The screens
    main = MainScreen()
    game = GameScreen('Medium')
    game_won = GameWon()
    game_lost = GameLost()
    
    widget = QStackedWidget()
    widget.addWidget(main)
    widget.setFixedHeight(500)
    widget.setFixedWidth(1000)
    widget.show()
    main.initUI() # starts the main application

    try:
        sys.exit(app.exec_())
    except SystemExit:
        pass



