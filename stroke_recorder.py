import cv2
import numpy as np
import sys

UP = 0
DOWN = 1

class StrokeRecorder:
    CANVAS_SIZE = 84
    SCALE = 3
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
        self.canvas = np.full((self.CANVAS_SIZE, self.CANVAS_SIZE,3), 255, dtype='uint8')

        # strokes
        self.strokes.clear()

    def on_mouse(self, event, x_render, y_render, flags, param):
        x = x_render//self.SCALE
        y = y_render//self.SCALE

        if self.pen_state>-1:
            # x and y relative to the last position (checkpoint)
            delx = x - self.last_pos[0]
            dely = y - self.last_pos[1]

            # limit the diff to 5
            delx = max(-5, min(5, delx))
            dely = max(-5, min(5, dely))

            x = self.last_pos[0] + delx
            y = self.last_pos[1] + dely

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

        #draw boundary rectangle to limit the move
        x0 = self.last_pos[0] - 6
        y0 = self.last_pos[1] - 6
        x1 = self.last_pos[0] + 6
        y1 = self.last_pos[1] + 6
        cv2.rectangle(img, (x0,y0), (x1,y1), (125,125,125), 1)


        #draw line from last checkpoint
        cv2.line(img, self.last_pos, self.pos, (0,255,0), 1)
        img = cv2.resize(img, (self.CANVAS_SIZE*self.SCALE, self.CANVAS_SIZE*self.SCALE))
        cv2.imshow('render', img)
    
    def next(self):
        self.out_file = open(self.out_filename, "a")
        for x,y,p in self.strokes:
            string = "{},{},{};".format(x,y,p)
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
