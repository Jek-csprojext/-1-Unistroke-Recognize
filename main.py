'''
直接執行main.py即可開啟$1 Unistroke Recognizer
'''
from tkinter import Tk, Canvas, Label, StringVar, PhotoImage, Frame
from dollar_16 import Dollar
from dollar_128 import Dollar_t

class Paint:

    PEN_SIZE = 3
    WINDOW_TITLE = 'Number Recognizer'
    MIN_N_POINTS = 10
    NOT_ENOUGH_POINTS_MESSAGE = 'Too few points made.Please try again'

    def __init__(self):
        # points
        self.old_point = (None, None)
        self.points = []
        self.recognizer = Dollar()
        self.recognizer_t = Dollar_t()
        # root
        self.root = Tk()
        self.root.title(self.WINDOW_TITLE)
        # left frame
        left_frame = Frame(self.root)
        left_frame.grid(row=1, column=1)
        # canvas
        self.canvas = Canvas(left_frame, bg='white', width=350, height=330)
        self.canvas.pack()
        self.canvas.bind('<B1-Motion>', self.paint)
        self.canvas.bind('<ButtonRelease-1>', self.reset)
        # label
        self.label_text = StringVar()
        self.label_text.set('Write the number from 0 to 9')
        self.label = Label(left_frame, textvariable=self.label_text)
        self.label.pack()
        # start
        self.root.mainloop()


    def paint(self, event):
        point = (event.x, event.y)
        if self.old_point != (None, None):
            self.canvas.create_line(self.old_point, point, width=self.PEN_SIZE)
        else:
            self.canvas.delete('all')
        self.points.append(point)
        self.old_point = point

    def reset(self, event):
        self.old_point = (None, None)
        points = self.points
        if (len(self.points) < self.MIN_N_POINTS):
            self.label_text.set(self.NOT_ENOUGH_POINTS_MESSAGE)
            return
        gesture_name, confidence = self.recognizer.get_gesture(self.points)
        self.points = points
        gesture_name_t, confidence_t = self.recognizer_t.get_gesture(self.points)
        self.label_text.set(f'Samplesize:16,Result: {gesture_name}, Confidence: {confidence:.4f} \n Samplesize:128,Result: {gesture_name_t}, Confidence: {confidence_t:.4f}')
        self.points = []
    
Paint()
