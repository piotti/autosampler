import socket
import traceback
import time
import threading

import queue


def steps_sec_to_uL_min(steps_per_sec):
    # uL/min = (steps/sec) * (60 sec/min) / (51200 steps/stroke) * (40 uL/stroke)
    return steps_per_sec * 60. / 51200. * 40

def uL_min_to_steps_sec(ul_per_minute):
    # steps/sec = (uL/min) * (51200 steps/stroke) / (60 sec/min) / (40 uL/stroke)
    return ul_per_minute * 51200. / 60. / 40.

def uL_to_steps(uL):
    # steps = uL * (51200 steps/stroke) * (1 stroke / 40 uL)
    return uL * 51200. / 40.

def steps_to_uL(steps):
    # uL = steps * (40 uL / stroke) * (1 stroke / 51200 steps)
    return steps * 40. / 51200.


class PumpController:
    def __init__(self, callback, ip='10.19.84.50', port=4001):
        self.ip = ip
        self.port=port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((ip, port))

        self.s.settimeout(1)

        self.q = queue.Queue()

        self.running = True

        self.callback = callback
        self.t = threading.Thread(target=self.read)
        self.t.start()

        threading.Thread(target=self.send).start()


    def send(self):
        # Send messages waiting in queue
        # print self.q.qsize()
        while self.running:
            try:
                msg = self.q.get_nowait()
                msg = unicode(msg)
                # print 'sending', msg
                self.s.sendall(msg)

            except queue.Empty:
                pass

            time.sleep(0.3)



    def read(self):

        while self.running:
            msg=''
            try:
                msg= self.s.recv(32).decode('utf-8')
            except socket.timeout, e:
                err = e.args[0]
                # this next if/else is a bit redundant, but illustrates how the
                # timeout exception is setup
                if err == 'timed out':
                    # print 'timeout'
                    continue
                else:
                    print e
                    sys.exit(1)
            except socket.error, e:
                    # Something else happened, handle error, exit, etc.
                    print e
                    exit()
            except Exception:
                try:
                    msg = self.s.recv(32)
                except Exception:
                    traceback.print_exc()

            if msg.strip():
                self.callback(msg)
            time.sleep(.25)

    def send_msg(self, msg):
        # msg = unicode(msg)
        # self.s.sendall(msg)
        # print 'queuing', msg
        # print self.q.qsize()

        self.q.put(msg)

    def checkVer(self, addr=''):
        addr = str(addr)
        self.send_msg('\n%sPR VR\r\n' % addr)

    def cmd(self, addr, msg):
        self.send_msg('\n%s%s\r\n' % (addr, msg))


    def setAddr(self, addr, current=''):
        self.send_msg('\n%sDN %s\r' % (current, str(addr)))
        self.send_msg('\n%sS\r\n' % addr)

    def setParty(self, addr, party):
        self.send_msg('\r%sPY %d\r\n' % (addr, int(party)))
    
    def setAlignment(self, addr):
        self.send_msg('\n%sS1=1,0,0\r\n' % addr)

        #Set Q8 var to a specific random value for later reference
        self.cmd(addr, 'VA Q8=%d' % CODES[addr])

        # Set up program which senses when alignment has finished
        self.cmd(addr, 'PG 100')
        self.cmd(addr, 'LB M2')
        self.cmd(addr, 'HM 1')
        self.cmd(addr, 'H')
        # print out said specific random value
        self.cmd(addr, 'PR Q8')
        self.cmd(addr, 'E')
        self.cmd(addr, 'PG')

    def setStop(self, addr):
        self.send_msg('\n%sS2=5,0,0\r\n' % addr)

    def setFlowDual(self, rate, uL):
        '''
        rate: flow rate in uL/min
        uL: volume in uL
        '''
        if rate < 0:
            rate = rate * -1
            if uL < 0:
                uL = uL * -1
        else:
            uL = uL * -1

        sps = uL_min_to_steps_sec(rate)
        steps = uL_to_steps(uL)

        self.send_msg('\n*VM=%d\r\n' % sps)
        self.send_msg('\n*MR %d\r\n' % steps)

    def setFlowSingle(self, addr, rate, uL):
        '''
        rate: flow rate in uL/min
        uL: volume in uL
        '''
        if rate < 0:
            rate = rate * -1
            if uL < 0:
                uL = uL * -1
        else:
            uL = uL * -1

        sps = uL_min_to_steps_sec(rate)
        steps = uL_to_steps(uL)

        # timeDelay = float(strokes*40*60/4000)
        # print timeDelay
        # factor = rate
        # self.send_msg('\n%sSL=%d\n' % (addr, int(factor)))
        # time.sleep(timeDelay)
        # factor = 0
        # self.send_msg('\n%sSL=%d\n' % (addr, int(factor)))
        self.send_msg('\n%sVM=%d\r\n' % (addr, sps))
        self.send_msg('\n%sMR %d\r\n' % (addr, steps))

    def align(self, addr, check=False):
        '''
        if check == True, then the pump will run the program defined in setAlignment which prints the position after
        the homing is complete.
        '''
        self.send_msg('\n%sVM=25000\r\n' %  addr)
        if check:
            self.cmd(addr, 'EX M2')
        else:
            self.send_msg('\n%sHM 1\r\n' %  addr)

    def align_dual(self):
        self.send_msg('\n*VM=25000\r\n')
        self.send_msg('\n*HM 1\r\n')

    def stopFlow(self, addr):
        self.setFlow(addr, 0, 1)

    def save(self, addr):
        self.send_msg('\n%sS\r\n' % addr)
    
    def close(self):
        self.running = False
        try:
            self.s.shutdown(1)
            self.s.close()
        except Exception:
            print('error disconnecting from mforce')
            pass



if __name__ == '__main__':
    pass

    # def on_print(msg):
    #     print msg
    #     print 'stripped:', msg.split('\n')[1].strip()
    #     if msg.split('\n')[1].strip() == str(CODES['a']):
    #         print 'AAAA'
    #     if msg.split('\n')[1].strip() == str(CODES['b']):
    #         print 'BBBB'
    #     print str(CODES['a']) in msg
    #     print str(CODES['b']) in msg

    # pc = PumpController(on_print, None)

    # while True:
    #     txt = raw_input('>>')
    #     if txt == 'exit':
    #         print 'Closing...'
    #         pc.close()
    #         exit()
    #     if txt[:2] == 'pc':
    #         exec(txt)
    #     else:
    #         pc.send_msg('\n%s\r\n' % txt)

