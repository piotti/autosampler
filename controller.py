# from mforce import PumpController
from tinyg import TinyG
from gantry import GantryController

class FakeTg:
    def __getattr__(self, attr):
        def f(*args, **kwargs):
            return None
        return f


class Controller:

    def __init__(self, gantry_cb):
        # self.pumps = PumpController()
        self.tg = TinyG()
        self.gantry = GantryController(self.tg, gantry_cb)

  

    # Gantry System
    def jog_up(self):
        self.gantry.jog_up()
    def jog_down(self):
        self.gantry.jog_down()
    def jog_left(self):
        self.gantry.jog_left()
    def jog_right(self):
        self.gantry.jog_right()
    def stop_jog(self):
        self.gantry.stop_jog()
    def step_up(self):
        self.gantry.step_up()
    def step_down(self):
        self.gantry.step_down()
    def step_left(self):
        self.gantry.step_left()
    def step_right(self):
        self.gantry.step_right()


    # Valve
    def valve_collect(self):
        self.tg.send_gcode('m8')
    def valve_waste(self):
        self.tg.send_gcode('m7')
        


    def close(self):
        pass
        # self.pumps.close()
        self.gantry.close()


