import time
import json

FEED = 40 # in/min

INCH_PER_SPACE = 0.394

def xy_to_gxgy(x, y):
    '''
    Given Cartesian (x, y), return (x, y) position of gantry
    as (gx, gy) tuple.
    '''
    return (-0.5 * (x + y), 0.5 * (x - y))

def gxgy_to_xy(gx, gy):
    '''
    Given gantry coordinates (gx, gy), return (x, y) Cartesian coordinates
    as (x, y) tuple.
    '''
    return (gy - gx, -gx - gy)

def gxgy_to_cr(gx, gy):
    '''
    Given gantry coordinates (gx, gy), return column and row of tube grid
    as (c, r) tuple.
    '''
    # TODO: Account for extra spacing in between the four 96-well plates
    return gx/INCH_PER_SPACE, gy/INCH_PER_SPACE

def cr_to_gxgy(c, r):
    '''
    Given column and row of tube grid, return gantry coordinates
    as (gx, gy) tuple.
    '''
    # TODO: Account for extra spacing in between the four 96-well plates
    return c*INCH_PER_SPACE, r*INCH_PER_SPACE

def cr_to_xy(c, r):
    return gxgy_to_xy(*cr_to_gxgy(c, r))

def xy_to_cr(x, y):
    return gxgy_to_cr(*xy_to_gxgy(x, y))




class GantryController:

    def __init__(self, tg, callback):
        self.tg = tg
        tg.callback = self.msg_received
        self.callback = callback
        self.start_com()

    def start_com(self):
        # Get status report
        self.get_status()

        time.sleep(0.1)

        # Set to inches and zero
        self.tg.send_gcode('g20')
        self.tg.send_gcode('g28.3 x0 y0')
        self.x = 0
        self.y = 0
        self.c = 0
        self.r = 0

    def get_status(self):
        self.tg.config('sr', 'null')

    def move_to_xy(self, x, y, feed=FEED):
        self.tg.send_msg('g1 f%d x%.3f y%.3f' % (feed, x, y))

    def move_to_cr(self, c, r, feed=FEED):
        x, y = cr_to_xy(c, r)
        self.move_to_xy(x, y, feed=feed)

    def jog_up(self):
        dest_x = self.x + 100
        dest_y = self.y - 100
        self.move_to_xy(dest_x, dest_y)

    def jog_down(self):
        dest_x = self.x - 100
        dest_y = self.y + 100
        self.move_to_xy(dest_x, dest_y)

    def jog_left(self):
        dest_x = self.x + 100
        dest_y = self.y + 100
        self.move_to_xy(dest_x, dest_y)

    def jog_right(self):
        dest_x = self.x - 100
        dest_y = self.y - 100
        self.move_to_xy(dest_x, dest_y)

    def stop_jog(self):
        self.tg.send_msg('!%')

    def step_up(self):
        self.move_to_cr(self.c, self.r+1)

    def step_down(self):
        self.move_to_cr(self.c, self.r-1)

    def step_left(self):
        self.move_to_cr(self.c-1, self.r)

    def step_right(self):
        self.move_to_cr(self.c+1, self.r)

    def update_cr(self):
        self.c, self.r = xy_to_cr(self.x, self.y)


    def msg_received(self, msg):
        try:
            d = json.loads(msg)
            if 'r' in d and not 'sr' in d:
                d = d['r']
            if 'sr' in d:
                if 'posx' in d['sr']:
                    self.x = d['sr']['posx']
                    # self.callback('x', self.x)
                if 'posy' in d['sr']:
                    self.y = d['sr']['posy']
                    # self.callback('posy', self.y)
                if 'feed' in d['sr']:
                    # self.feed = d['sr']['feed']
                    # self.callback('feed', self.feed)
                    pass

                # reset c, r positions
                self.update_cr()
                self.callback(self.c, self.r)

                # detect end of homing
                # if d['sr'].get('stat', 0) == 3:
                #     if self.homing_x:
                #         self.tq.on_event('x home', None)
                #         self.homing_x = False
                #     if self.homing_y:
                #         self.homing_y = False
                #         self.tq.on_event('y home', None)
        except ValueError:
            pass

    def close(self):
        self.tg.close()



if __name__ == '__main__':
    from tinyg import TinyG
    gc = GantryController(TinyG(), lambda *x:print(*x))



