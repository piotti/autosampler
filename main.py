import tkinter as tk
from tkinter import *

from controller import Controller

import graph

FONT = ('TkDefaultFont', 20)


class Button(tk.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(font=FONT)

class Label(tk.Label):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(font=FONT)



class Window(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        master.title('Autosampler')
        master.protocol("WM_DELETE_WINDOW", self.close)


        # Motion Frame
        motion_frame = Frame(master)
        motion_frame.grid(row=0, column=0)
        up_btn = Button(motion_frame, text='\u2191')
        up_btn.grid(row=0, column=2)
        up_btn.bind('<ButtonPress-1>', self.start_jog_up)
        up_btn.bind('<ButtonRelease-1>', self.on_stop_jog)
        down_btn = Button(motion_frame, text='\u2193')
        down_btn.grid(row=4, column=2)
        down_btn.bind('<ButtonPress-1>', self.start_jog_down)
        down_btn.bind('<ButtonRelease-1>', self.on_stop_jog)
        right_btn = Button(motion_frame, text='\u2192')
        right_btn.grid(row=2, column=4)
        right_btn.bind('<ButtonPress-1>', self.start_jog_right)
        right_btn.bind('<ButtonRelease-1>', self.on_stop_jog)
        left_btn = Button(motion_frame, text='\u2190')
        left_btn.grid(row=2, column=0)
        left_btn.bind('<ButtonPress-1>', self.start_jog_left)
        left_btn.bind('<ButtonRelease-1>', self.on_stop_jog)

        Button(motion_frame, text='\u25a0', command=self.on_stop_jog).grid(row=2, column=2)

        Button(motion_frame, text='\u21a5', command=self.on_step_up).grid(row=1, column=2)
        Button(motion_frame, text='\u21a7', command=self.on_step_down).grid(row=3, column=2)
        Button(motion_frame, text='\u21a6', command=self.on_step_right).grid(row=2, column=3)
        Button(motion_frame, text='\u21a4', command=self.on_step_left).grid(row=2, column=1)

        # Position Frame
        pos_frame = Frame(master)
        pos_frame.grid(row=0, column=2)
        Label(pos_frame, text='col.:').grid(row=0, column=0)
        self.col_label = Label(pos_frame, text='0')
        self.col_label.grid(row=0, column=1)
        Label(pos_frame, text='row:').grid(row=1, column=0)
        self.row_label = Label(pos_frame, text='0')
        self.row_label.grid(row=1, column=1)


        # Valve Frame
        valve_frame = Frame(master)
        valve_frame.grid(row=0, column=1)
        self.collect_btn = Label(valve_frame, text="Collect", bg='gray', fg='white', width=8)
        self.collect_btn.bind('<ButtonPress-1>', self.on_collect_btn)
        self.collect_btn.pack(anchor=W)
        self.waste_btn = Label(valve_frame, text="Waste", bg='green3', fg='white', width=8)
        self.waste_btn.bind('<ButtonPress-1>', self.on_waste_btn)
        self.waste_btn.pack(anchor=W)


        # Graph Frame
        graph_frame = Frame(master)
        graph_frame.grid(row=1, column=0, columnspan=3)
        self.graph = graph.Graph(graph_frame)


        self.c = Controller(self.on_position_update)
        




    def start_jog_up(self, *e):
        print('jog up pressed')
        self.c.jog_up()
    def start_jog_down(self, *e):
        print('jog down pressed')
        self.c.jog_down()
    def start_jog_left(self, *e):
        print('jog left pressed')
        self.c.jog_left()
    def start_jog_right(self, *e):
        print('jog right pressed')
        self.c.jog_right()

    def on_stop_jog(self, *e):
        print('stopping jog')
        self.c.stop_jog()

    def on_step_up(self):
        print('step up pressed')
        self.c.step_up()
    def on_step_down(self):
        print('step down pressed')
        self.c.step_down()
    def on_step_left(self):
        print('step left pressed')
        self.c.step_left()
    def on_step_right(self):
        print('step right pressed')
        self.c.step_right()


    def set_valve_state(self, collecting):
        colors = {True: 'green3', False: 'gray'}
        self.collect_btn.configure(bg=colors[collecting])
        self.waste_btn.configure(bg=colors[not collecting])

    def on_collect_btn(self, *e):
        self.c.valve_collect()
        self.set_valve_state(True)

    def on_waste_btn(self, *e):
        self.c.valve_waste()
        self.set_valve_state(False)

    def on_position_update(self, c, r):
        self.col_label['text'] = '%.2f' % c
        self.row_label['text'] = '%.2f' % r



    def close(self):
        print('Closing...')
        self.c.close()
        self.master.destroy()







if __name__=='__main__':

    root = tk.Tk()
    app = Window(root)
    ani = graph.animation.FuncAnimation(graph.f, graph.animate, interval=1000)
    app.mainloop()
