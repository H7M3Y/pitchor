#!/bin/python
import math
import time
import pyaudio
import aubio
import numpy as np
import statistics
from collections import deque
from itertools import filterfalse

size = 1024
rate = 44100
delta = 0.2
remain = 3.2

fall = deque(maxlen=int(remain*(1/delta))); p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=rate, input=True)
detor = aubio.pitch("yin", size, size, rate)
detor.set_silence(-50)
print("Listening for real-time pitch detection...")

buf = []; lt = time.time(); lmt=lt
def store(s):
    global buf, lt
    buf.append(s); ct = time.time()
    if ct - lt > delta:
        update(ct)
        buf = []; lt = math.floor(ct*(1/delta))/(1/delta)

def update(ct):
    global buf, lmt
    valid = filterfalse(lambda x: x != 'Rest', buf)
    if len(valid) < len(buf)/2:
        return
    n = statistics.mode(valid)
    missed = int(min(ct-lmt, remain)//delta)-2
    for _ in range(0, missed):
        fall.appendleft('Rest')
    fall.appendleft(n); lmt = lt

def toNote(pitch):
    note = 12 * math.log2(pitch / 440) + 69
    octave = int(note // 12) - 1
    note_in_octave = int(note % 12)
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    res = f"{notes[note_in_octave]}{octave}"
    store(res)
    return res

def pitch_det(source):
    signal = np.frombuffer(source, dtype=np.int16).astype(np.float32)
    pitch = detor(signal)[0]
    if 110 < pitch < 1760:
        s =  f"[#>_] {toNote(pitch)} : {pitch:.2f} Hz | "
        s = f"{s:25}{show(fall)}"
        print(s + ' '*(pitch_det.last_s_len-len(s)), end='\r')
        pitch_det.last_s_len = len(s)
    else:
        store('Rest')
pitch_det.last_s_len = 0

def show(d):
    res = ''; prev = ''
    for i in d:
        if i == 'Rest':
            res += 'x '
        elif i == prev:
            res += '- '
        else:
            res += i + ' '
        prev = i
    return res

try:
    while True:
        pitch_det(stream.read(size))
except KeyboardInterrupt:
    print(end='\r')
    print("[xxx]\nProgram terminated by user.")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
