import cv2
import numpy as np
import sys

UP = 0
DOWN = 1

class StrokeRecorder:
    def __init__(self, output_file):
        cv2.namedWindow('render')
        cv2.setMouseCallback('render', self.on_mouse)
        self.strokes = []
        self.out_filename = output_file
        self.out_file = open(self.out_filename, "w")
        self.reset()

    def reset(self):
        self.pos = (-1,-1)
        self.last_pos = (-1,-1)
        self.pen_state = -1
        self.canvas = np.full((84,84,3), 255, dtype='uint8')

        # strokes
        self.strokes.clear()

    def on_mouse(self, event, x, y, flags, param):
        x = x//3
        y = y//3
        if event == cv2.EVENT_MOUSEMOVE:
            self.pos = (x,y)
        elif event == cv2.EVENT_LBUTTONDOWN:
            if self.pen_state==-1:
                self.pen_state = 0
                self.last_pos = (x,y)
            else:
                self.draw_stroke((x,y), 1)
                self.last_pos = (x,y)
                self.strokes.append((x, y, 1))

        elif event == cv2.EVENT_RBUTTONDOWN:
            self.draw_stroke((x,y), 0)
            self.last_pos = (x,y)
            self.strokes.append((x, y, 0))

    def draw_stroke(self, pos, pen_state):
        color = (255,0,0) if pen_state==1 else (0,0,255)
        cv2.line(self.canvas, self.last_pos, pos, color, 1)

    def render(self):
        img = self.canvas.copy()
        cv2.line(img, self.last_pos, self.pos, (0,255,0), 1)
        img = cv2.resize(img, (84*3, 84*3))
        cv2.imshow('render', img)
    
    def next(self):
        self.out_file = open(self.out_filename, "a")
        for x,y,p in self.strokes:
            string = "{},{},{};".format(x,y,p)
            print(string)
            self.out_file.write(string)
        self.out_file.write('\n')
        self.out_file.close()

        self.reset()

    def __del__(self):
        cv2.destroyAllWindows()
        self.out_file.close()

if __name__=='__main__':
    out_file = 'out.txt'
    if len(sys.argv) > 1:
        out_file = sys.argv[1]

    sr = StrokeRecorder(out_file)

    while True:
        sr.render()
        c = cv2.waitKey(100)
        if c == ord('x'):
            sr.next()
            break
        elif c==32:
            sr.next()
