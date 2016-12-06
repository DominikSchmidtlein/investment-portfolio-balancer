import json

class ConfigFileHandler:
	def __init__(self, filename):
		self.filename = filename

	def load(self):
		with open(self.filename, "r") as f:
			return json.load(f)

	def save(self, config):
		with open(self.filename, "w") as f:
			f.write(config)
