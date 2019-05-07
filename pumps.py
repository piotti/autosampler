import threading
import serial
import traceback

import time

import queue

def prnt(msg):
    print(msg)


class PumpController:
    
    def __init__(self, callback=prnt, port='COM7'):
        self.ser = serial.Serial(port, baudrate=9600, timeout=1)
        if self.ser.isOpen():
           print('MForce: opened on %s' % port)
        else:
            print('MForce: could not open on %s' % port)
            return

        self.q = queue.Queue()

        self.running = True
        self.callback = callback
        threading.Thread(target=self.read).start()
        threading.Thread(target=self.send).start()


        time.sleep(0.1)
        self.send_gcode('g20')


    def send_gcode(self, gcode):
        self.send_msg(gcode)

    def config(self, key, val):
        self.send_msg('{"%s":%s}' % (str(key), str(val)))

        
    def send_msg(self, msg):
        # self.ser.write('\r' + msg + '\r')
        self.q.put(msg)


    def send(self):
        # Send messages waiting in queue
        # print self.q.qsize()
        while self.running:
            try:
                msg = self.q.get_nowait()
                # print 'sending', msg
                self.ser.write(str.encode('\r' + msg + '\r'))
        
            except queue.Empty:
                time.sleep(0.01)


    def read(self):
        while self.running:
            try:
                line = self.ser.readline()
                if line:
                    # print line
                    self.callback(line)
            except Exception as e:
                if not self.running:
                    return
                print('MForce read error:')
                traceback.print_exc()
        
    def close(self):
        self.running = False
        self.ser.close()
        if not self.ser.isOpen():
            print('MForce: serial port closed')
        else:
            print('MForce: could not close serial port')


if __name__ == '__main__':
    pc = PumpController()



