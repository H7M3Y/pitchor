#!/usr/bin/env python3

import math
import statistics
import time
import numpy as np
import pyaudio
import aubio
from collections import deque

recent_notes = deque(maxlen=25)

def hz_to_note_and_octave(frequency, reference_frequency=440, reference_note=69):
    note = 12 * math.log2(frequency / reference_frequency) + reference_note
    octave = int(note // 12 - 1)
    note_in_octave = int(note % 12)
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    return store(F"{notes[note_in_octave]}{octave}")

buffer, btime = [], 0.2
last_time = 0
def store(note):
    global buffer, last_time
    buffer.append(note); ct = time.time()
    if(ct - last_time >= btime):
        n_last_time = math.floor(ct*5)/5
        missed = int(min(n_last_time - last_time, 5)//0.2) - 1
        for _ in range(0, missed):
            recent_notes.appendleft('Rest')
        recent_notes.appendleft(statistics.mode(buffer))
        buffer = []; last_time = n_last_time
    return note

def pitch_callback(frame, pitch_detector):
    # Convert the frame to a NumPy array of floats in the range [-1, 1]
    signal = np.frombuffer(frame, dtype=np.int16).astype(np.float32) / 32768.0

    # Use the pitch detection algorithm from aubio
    pitch_value = pitch_detector(signal)[0]*2

    # Filter out harmonics by considering only pitches within a certain range
    if 160 < pitch_value < 1800:
        # Print the detected pitch
        s = f"[#>_] {hz_to_note_and_octave(pitch_value)} : {pitch_value:.2f} Hz |"
        print(f"{s:24}{show(recent_notes)}   ", end='\r')

def show(deq):
    res, last = '', ''
    for i in deq:
        if i == 'Rest':
            res += ' x'
        elif i == last:
            res += ' -'
        else:
            res += ' ' + i
        last = i
    return res

def main():
    # Parameters
    chunk_size = 1024
    format = pyaudio.paInt16
    channels = 1
    sample_rate = 48000

    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # Open a stream
    stream = p.open(
        format=format,
        channels=channels,
        rate=sample_rate,
        input=True,
        frames_per_buffer=chunk_size
    )

    # Initialize the pitch detector from aubio with adjusted parameters
    pitch_detector = aubio.pitch("yin", 2048, 1024, sample_rate)
    pitch_detector.set_unit("Hz")
    pitch_detector.set_silence(-40)

    print("Listening for real-time pitch detection...")

    try:
        global last_time
        last_time = time.time()
        while True:
            # Read audio data from the stream
            frame = stream.read(chunk_size)
            pitch_callback(frame, pitch_detector)

    except KeyboardInterrupt:
        print("Program terminated by user.")

    finally:
        # Close the stream and PyAudio
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main()
