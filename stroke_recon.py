import cv2
import numpy as np
import sys

UP = 0
DOWN = 1

class StrokeRecon:
    CANVAS_SIZE = 84
    SCALE = 3
    def __init__(self, input_file):
        cv2.namedWindow('render')
        self.input_filename = input_file

        with open(self.input_filename, 'r') as in_f:
            self.lines = in_f.readlines()

        self.index = -1
        self.reset()

    def reset(self):
        self.canvas = np.full((self.CANVAS_SIZE, self.CANVAS_SIZE,3), 255, dtype='uint8')
        

    def recon(self):
        line = self.lines[self.index]
        data = line.strip('\n').split(';')
        print(line, data)
        boundary = tuple(int(x) for x in data[0].split(','))
        self.last_pos = boundary[:2]
        for d in data[1:-1]:
            print(d)
            d = d.split(',')
            stroke = (int(d[0]), int(d[1]))
            pen = int(d[2])
            pos = (self.last_pos[0] + stroke[0], self.last_pos[1] + stroke[1] )
            self.draw_stroke(pos, pen)
            self.last_pos = pos

    def draw_stroke(self, pos, pen_state):
        color = (255,0,0) if pen_state==1 else (0,0,255)
        cv2.line(self.canvas, self.last_pos, pos, color, 1)

    def render(self):
        img = self.canvas.copy()
        img = cv2.resize(img, (self.CANVAS_SIZE*self.SCALE, self.CANVAS_SIZE*self.SCALE))
        cv2.imshow('render', img)
    
    def next(self):
        self.index+=1
        self.reset()
        self.recon()


    def __del__(self):
        cv2.destroyAllWindows()

if __name__=='__main__':
    out_file = 'out.txt'
    if len(sys.argv) > 1:
        in_file = sys.argv[1]

    sr = StrokeRecon(in_file)

    while True:
        sr.render()
        c = cv2.waitKey(0)
        if c == ord('x'):
            sr.next()
            break
        elif c==32:
            sr.next()
