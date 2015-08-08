import random, os, logging
from sys import argv, exit
from time import time, sleep

from core.MPy.api import MPServerAPI
from core.MPy.vars import DEFAULT_TELEPHONE_GPIO, UNPLAYABLE_FILES

PROMPTS = {
	'choose_hear_or_record' : "choose_hear_or_record.mp3",
	'record_absolution' : "record_absolution.mp3",
	'record_confession' : "record_confession.mp3",
	'choose_record_absolution' : "choose_record_absolution.mp3",
	'no_confessions_yet' : "no_confessions_yet.mp3"
}

KEY_MAP = {
	'choose_hear_or_record' : [3, 4],
	'choose_record_absolution' : [3, 4]
}

class EchoPriest(MPServerAPI):
	def __init__(self):
		MPServerAPI.__init__(self, DEFAULT_TELEPHONE_GPIO)
		logging.basicConfig(filename=self.conf['d_files']['module']['log'], level=logging.DEBUG)

	def choose_hear_or_record(self):
		c = 'choose_hear_or_record'
		logging.info(c)

		choice = self.prompt(os.path.join("prompts", PROMPTS[c]), KEY_MAP[c])
		
		if choice == KEY_MAP[c][0]:
			return self.hear_confession()
		elif choice == KEY_MAP[c][1]:
			return self.record_confession()

		return False

	def hear_confession(self):
		logging.info("hear_confession")

		for _, _, files in os.walk(os.path.join(self.conf['media_dir'], "confessions")):
			files = [file for file in files if file not in UNPLAYABLE_FILES]

			if len(files) == 1:
				random_confession = files[0]
			elif len(files) == 0:
				if self.say(os.path.join("prompts", PROMPTS['no_confessions_yet'])):
					return self.choose_hear_or_record()
			else:
				random_confession = files[random.randint(0, len(files) - 1)]
			
			break

		if self.say(os.path.join("confessions", random_confession)):
			c = 'choose_record_absolution'
			logging.info(c)

			choice = self.prompt(os.path.join("prompts", PROMPTS[c]), KEY_MAP[c])

			if choice == KEY_MAP[c][0]:
				return self.record_absolution(random_confession)

			return self.choose_hear_or_record()

		return False

	def record_confession(self):
		logging.info("record_confession")

		if self.record(os.path.join("prompts", PROMPTS['record_confession']), \
			dst=os.path.join("confessions", "confession_%d.wav" % time())):
			
			return self.choose_hear_or_record()

		return False

	def record_absolution(self, confession):
		logging.info("record_absolution")

		if self.record(os.path.join("prompts", PROMPTS['record_absolution']), \
			dst=os.path.join("absolutions", confession.replace(".wav", "_%d.wav" % time()))):

			return self.choose_hear_or_record()
		
		return False

	def run_script(self):
		super(EchoPriest, self).run_script()
		self.choose_hear_or_record()

if __name__ == "__main__":
	res = False
	ep = EchoPriest()

	if argv[1] in ['--stop', '--restart']:
		res = ep.stop()
		sleep(5)

	if argv[1] in ['--start', '--restart']:
		res = ep.start()

	exit(0 if res else -1)
