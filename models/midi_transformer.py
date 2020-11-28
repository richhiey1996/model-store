## MIDI Transformer on Pop909 dataset

import tensorflow as tf
from helpers.layers import TransformerEncoder, TransformerDecoder

class MIDITransformer(tf.keras.Model):

	def __init__(self, config_path, model_path):
		self.config_path = config_path
		self.model_path = model_path

		with open('data.json') as json_file: 
    		self.configs = json.load(self.config_path)

		self.midi_encoder = TransformerXLEncoder(self.configs['encoder'])
		self.midi_decoder = TransformerXLDecoder(self.configs['encoder'])

	def __create_model__(self):
		input_midi = tf.keras.layers.Input()
		