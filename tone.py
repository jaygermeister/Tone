#-------------------------------------------------------------------------------
# Name:        module1
# Purpose: This is a command line volume and tone control application that will read a WAV file and play it with adjusted tone, or write a new WAV file with the adjusted tone and volume
#
# Requirements:
    # --volume setting, a non-negative float in the range 0.0-10.0. Each full volume step is 3 dB with 0dB being teh default volume setting of 9.0. A volume setting of less than 0.1 is treated as "0 volume i.e. no sound at all"

    # --bass, --mid, --treble; Tone setting, a non-negative float in the range 0.0-10.0. Each full step is 3 dB, with 0dB being default volume setting of 5.0. A tone setting of less than 0.1 is treated as no tone.

    # --out; name of an output WAV file. This will suppress playback and write the output into the given WAV file in the same format as the input

    # This program must take a provisional argument naming the input WAV file

    # The program must use the library routine supplied in the class materials in hw-tone-resources to read and write wav files, play wav files and process the CLI arguments
#
# Author:      Jayger
#
# Created:     13/05/2023
# Copyright:   (c) Jayger 2023
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import argparse
import numpy as np
import libtone
from libtone import read_wav
from scipy.signal import butter, lfilter

# Size of output buffer in frames. Less than 1024 is not
# recommended, as most audio interfaces will choke
# horribly.
BUFFER_SIZE = 2048

def apply_volume(data, volume):
    """
    Adjusts the volume of the audio data.

    Args:
        data (ndarray): Audio data as a numpy array.
        volume (float): Volume multiplier (0.0..10.0 or higher).

    Returns:
        ndarray: Adjusted audio data as a numpy array.
    """
    return data * volume

def apply_tone(data, rate, bass_gain, mid_gain, treble_gain):
    # Filter cutoff frequencies (Hz)
    bass_cutoff = 200
    mid_cutoff = 2000
    treble_cutoff = 4000

    # Filter order
    filter_order = 2

    # Normalize gain values to a maximum of 10
    gain_norm = 10.0 / max(bass_gain, mid_gain, treble_gain)
    bass_gain *= gain_norm
    mid_gain *= gain_norm
    treble_gain *= gain_norm

    # Calculate filter coefficients
    b_bass, a_bass = butter(filter_order, bass_cutoff / (rate / 2), 'low')
    b_mid, a_mid = butter(filter_order, [bass_cutoff / (rate / 2), mid_cutoff / (rate / 2)], 'band')
    b_treble, a_treble = butter(filter_order, treble_cutoff / (rate / 2), 'high')

    # Apply filters to the data
    data = lfilter(b_bass * bass_gain, a_bass, data)
    data = lfilter(b_mid * mid_gain, a_mid, data)
    data = lfilter(b_treble * treble_gain, a_treble, data)

    # Clip the output to prevent distortion
    data = np.clip(data, -1, 1)

    return data

def write_wav(filename, rate, data):
    # Define your WAV file writer function here
    pass

def play_audio(rate, data):
    # Define your real-time audio playback function here
    pass

# Argprse module support for CLI is built around instance of argparse.ArgumentParser. It's a container for argument specifications and has options thawt apply the parser as whole
def main():

    parser = argparse.ArgumentParser(description='Adjust tone and volume of a WAV file.')   # The first step in using the argparse is creating an ArgumentParser object. The ArgumentParser object will hold all the information necessary to parse the command line into Python data types.

    # additional arguments for CLI input to take input on the CLI and turn them into objects. This is stored and used when parse_args is called.

    parser.add_argument('input_file', type=str, help='Input WAV filename')   # parser.add_argument() attaches individual argument specifications to the parser.


    parser.add_argument('--out', type=str, help='write to WAV file instead of playing')
    parser.add_argument('--volume', type=float, default=9.0, help='volume in 3dB units (default 9 = 0dB, 0 = 0 output)')
    parser.add_argument('--bass', type=float, default=5.0, help='bass emphasis in 3dB units (default 5 = 0dB, 0 = 0 output)')
    parser.add_argument('--mid', type=float, default=5.0, help='midrange emphasis in 3dB units (default 5 = 0dB, 0 = 0 output)')
    parser.add_argument('--treble', type=float, default=5.0, help='treble emphasis in 3dB units (default 5 = 0dB, 0 = 0 output)')

    args = parser.parse_args()  # this will inspect the CLI, convert each argument to the appropriate type, and invoke the appropriate action.

    input_filename = args.input_file
    output_filename = args.out

    # Read the input WAV file
    rate, data = read_wav(input_filename)

    # Apply the tone and volume adjustments
    data = apply_volume(data, args.volume)
    data = apply_tone(data, rate, args.bass, args.mid, args.treble)

    # Write the output WAV file, if requested
    if output_filename:
        libtone.write_wav(output_filename, rate, data)
    else:
        # Play the output audio in real time
        libtone.play_audio(rate, data)


if __name__ == '__main__':
    main()
