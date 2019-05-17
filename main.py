import tkinter as tk
from tkinter import *

from controller import Controller

import graph

import process

# 1.5 ML dead vol

FONT = ('TkDefaultFont', 16)


class Button(tk.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.configure(font=FONT)

class Label(tk.Label):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.configure(font=FONT)



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

        Button(motion_frame, text='Zero', command=self.on_zero).grid(row=3, column=0, columnspan=2)

        self.x_input = Entry(motion_frame, width=2)
        self.x_input.grid(row=3, column=3)
        self.y_input = Entry(motion_frame, width=2)
        self.y_input.grid(row=3, column=4)
        Button(motion_frame, text='Goto', command=self.on_goto).grid(row=4, column=3, columnspan=2)

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

        # Pump Frame
        pump_frame = Frame(master)
        pump_frame.grid(row=1, column=0)
        self.pump_a_fr = Entry(pump_frame, width=3)
        self.pump_a_fr.grid(row=0, column=0)
        Button(pump_frame, text='FR A', command=self.on_set_fr_a).grid(row=0, column=1)
        Button(pump_frame, text='Stop', command=self.on_stop_pump_a).grid(row=0, column=2)
        self.pump_b_fr = Entry(pump_frame, width=3)
        self.pump_b_fr.grid(row=1, column=0)
        Button(pump_frame, text='FR B', command=self.on_set_fr_b).grid(row=1, column=1)
        Button(pump_frame, text='Stop', command=self.on_stop_pump_b).grid(row=1, column=2)



        # Process Frame
        process_frame = Frame(master)
        process_frame.grid(row=1, column=2)
        Button(process_frame, text='Start Process', command=self.on_start_process).grid(row=0, column=0)
        Button(process_frame, text='Stop Process', command=self.on_stop_process).grid(row=1, column=0)


        # Graph Frame
        # graph_frame = Frame(master)
        # graph_frame.grid(row=2, column=0, columnspan=3)
        # self.graph = graph.Graph(graph_frame)


        self.c = Controller(self.on_position_update)



        # Create process
        self.p = process.IntervalStep(self.c, 30)
        




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

    def on_zero(self):
        self.c.zero_xy()

    def parse_entry_field(self, field, typ):
        x = field.get()
        if not x.strip():
            x = 0
            field.delete(0,END)
            field.insert(0, '0')
        else:
            x = typ(x)
        return x

    def on_goto(self):
        x = self.parse_entry_field(self.x_input, float)
        y = self.parse_entry_field(self.y_input, float)
        self.c.on_goto(x, y)

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

    def on_set_fr_a(self):
        fr = self.parse_entry_field(self.pump_a_fr, float)
        self.c.setFlow('', fr, 625.4)

    def on_set_fr_b(self):
        fr = self.parse_entry_field(self.pump_b_fr, float)
        print("pump b not connected")
        # self.c.setFlow('', fr, 10000)

    def on_stop_pump_a(self):
        self.c.setFlow('', 0, 625.4)

    def on_stop_pump_b(self):
        print("pump b not connected")






    def on_start_process(self):
        self.p.start()

    def on_stop_process(self):
        self.p.stop()



    def close(self):
        print('Closing...')
        self.p.stop()
        self.c.close()
        self.master.destroy()







if __name__=='__main__':

    root = tk.Tk()
    app = Window(root)
    # ani = graph.animation.FuncAnimation(graph.f, graph.animate, interval=1000)
    app.mainloop()
