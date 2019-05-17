import threading
import time

class Process:
	def __init__(self, c):
		self.c = c
		self.running = False

	# Override this method
	def mainloop(self): 
		print('No process defined')
		self.stop()

	def run(self):
		while self.running:
			self.mainloop()
		print('Process finished')

	def start(self):
		self.running = True
		threading.Thread(target=self.run).start()

	def stop(self):
		self.running = False




class IntervalStep(Process):
	def __init__(self, c, interval, width=8, shape='zigzag', start_dir=1):
		super().__init__(c)
		self.interval = interval

		if not shape == 'zigzag' or start_dir != 1:
			raise NotImplementedError

		self.width = width
		self.moving_right = True

		self.last_time = time.time()

	def mainloop(self):
		if time.time() > self.last_time + self.interval:
			print('loop')
			col = round(self.c.gantry.c)
			row = round(self.c.gantry.r)
			if self.moving_right:
				if col < self.width - 1:
					# continue moving right
					new_col = col + 1
					new_row = row
				else:
					# move up then switch directions
					new_col = col
					new_row = row + 1
					self.moving_right = False
			else:
				# moving left
				if col > 0:
					# keep moving left
					new_col = col - 1
					new_row = row
				else:
					# move up and switch directions
					new_col = col
					new_row = row + 1
					self.moving_right = True
			# move
			print(new_col, new_row)
			self.c.on_goto(new_col, new_row)
			self.last_time = time.time()


if __name__=='__main__':
	p = IntervalStep(None, 1)
	p.start()

