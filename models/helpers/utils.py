####################################################################
# --------------- Utilities for building Transformers --------------
####################################################################
import numpy as np
import tensorflow as tf
import pretty_midi
import IPython
import librosa
#import note_seq
####################################################################


## -------------------------------------------------------------------
## Return angle for a particular position in the sequence to calculate
## positional encoding 
## -------------------------------------------------------------------
def get_angles(pos, i, d_model):
    angle_rates = 1 / np.power(10000, (2 * (i//2)) / np.float32(d_model))
    return pos * angle_rates
## -------------------------------------------------------------------


## -------------------------------------------------------------------
## Calculate positional encoding for a particular position
## -------------------------------------------------------------------
def positional_encoding(position, d_model):
    angle_rads = get_angles(np.arange(position)[:, np.newaxis],
                          np.arange(d_model)[np.newaxis, :],
                          d_model)
    # apply sin to even indices in the array; 2i
    angle_rads[:, 0::2] = np.sin(angle_rads[:, 0::2])
    # apply cos to odd indices in the array; 2i+1
    angle_rads[:, 1::2] = np.cos(angle_rads[:, 1::2])

    pos_encoding = angle_rads[np.newaxis, ...]
    return tf.cast(pos_encoding, dtype=tf.float32)
## -------------------------------------------------------------------


## -------------------------------------------------------------------
def create_padding_mask(seq):
    seq = tf.cast(tf.math.equal(seq, 0), tf.float32)
    # add extra dimensions to add the padding to the attention logits.
    return seq[:, tf.newaxis, tf.newaxis, :] #(batch_size, 1, 1, seq_len)  
## -------------------------------------------------------------------


## -------------------------------------------------------------------
def create_look_ahead_mask(size):
    mask = 1 - tf.linalg.band_part(tf.ones((size, size)), -1, 0)
    return mask  # (seq_len, seq_len)
## -------------------------------------------------------------------


## -------------------------------------------------------------------
## Calculate the attention weights.
## q, k, v must have matching leading dimensions.
## k, v must have matching penultimate dimension, i.e.: seq_len_k = seq_len_v.
## The mask has different shapes depending on its type(padding or look ahead) 
## but it must be broadcastable for addition.
## -------------------------------------------------------------------
def scaled_dot_product_attention(q, k, v, mask):
    """  
    Args:
        q: query shape == (..., seq_len_q, depth)
        k: key shape == (..., seq_len_k, depth)
        v: value shape == (..., seq_len_v, depth_v)
        mask: Float tensor with shape broadcastable 
            to (..., seq_len_q, seq_len_k). Defaults to None.
    
    Returns:
        output, attention_weights
    """

    matmul_qk = tf.matmul(q, k, transpose_b=True)  # (..., seq_len_q, seq_len_k)
  
    # scale matmul_qk
    dk = tf.cast(tf.shape(k)[-1], tf.float32)
    scaled_attention_logits = matmul_qk / tf.math.sqrt(dk)

    # add the mask to the scaled tensor.
    if mask is not None:
        scaled_attention_logits += (mask * -1e9)  

    # softmax is normalized on the last axis (seq_len_k) so that the scores
    # add up to 1.
    attention_weights = tf.nn.softmax(scaled_attention_logits, axis=-1)  # (..., seq_len_q, seq_len_k)

    output = tf.matmul(attention_weights, v)  # (..., seq_len_q, depth_v)

    return output, attention_weights
## -------------------------------------------------------------------


## -------------------------------------------------------------------
def point_wise_feed_forward_network(d_model, dff):
    return tf.keras.Sequential([
        tf.keras.layers.Dense(dff, activation='relu'),  # (batch_size, seq_len, dff)
        tf.keras.layers.Dense(d_model)  # (batch_size, seq_len, d_model)
    ])
## -------------------------------------------------------------------


## -------------------------------------------------------------------
def plot_piano_roll(pm, start_pitch, end_pitch, fs=100):
    # Use librosa's specshow function for displaying the piano roll
    librosa.display.specshow(pm.get_piano_roll(fs)[start_pitch:end_pitch],
                             hop_length=1, sr=fs, x_axis='time', y_axis='cqt_note',
                             fmin=pretty_midi.note_number_to_hz(start_pitch))
## -------------------------------------------------------------------


## -------------------------------------------------------------------
## Reconstruct MIDI data from list of tokenized MIDI Events
## -------------------------------------------------------------------
def reconstruct_and_play_audio(seq, processor, name='Untitled', program=1):
    print('----------------------------------------------------------')
    print(name + ':')

    full_midi = pretty_midi.PrettyMIDI()
    melody_instr = pretty_midi.Instrument(program=program)
    
    for note in processor.decode(seq):
        melody_instr.notes.append(note)
    full_midi.instruments.append(melody_instr)
    full_midi.write(
    plot_piano_roll(full_midi, 24, 84)
    #midi_2_wav = full_midi.synthesize()
    #IPython.display.display(IPython.display.Audio(midi_2_wav, rate=44100))
    print('Done reconstructing events into Piano Roll!')
    full_midi_ns = note_seq.midi_io.midi_file_to_note_sequence(filename)
    #note_seq.plot_sequence(full_midi_ns)
## -------------------------------------------------------------------