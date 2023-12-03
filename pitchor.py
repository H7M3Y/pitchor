#!/bin/python
import math
import time
import pyaudio
import aubio
import numpy as np
import statistics
import argparse
from collections import deque

parser = argparse.ArgumentParser(description='Simple but practical real-time music note detector')
parser.add_argument('-s', "--size", default=1024, help='the number of samples collected at a delta time.')
parser.add_argument('-r', "--rate", default=44100, help='microphone sampling rate')
parser.add_argument('-d', "--delta", default=0.2, help='time duration of a single detection (unit: s. the same below)')
parser.add_argument('-R', '--remain', default=3.2, help='time that the detected notes remain')
parser.add_argument('-l', '--lowest', default=110, help='lower bound of detection')
parser.add_argument('-u', '--uppest', default=1760, help='upper bound of detection')
a = parser.parse_args()

size = int(a.size)
rate = int(a.rate)
delta = float(a.delta)
remain = float(a.remain)
lb, ub = float(a.lowest), float(a.uppest)

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
    valid = [n for n in buf if n != 'Rest']
    if len(valid) < len(buf)/2:
        return
    n = statistics.mode(valid)
    missed = int(min(ct-lmt, remain)//delta)-2
    for _ in range(0, missed):
        fall.appendleft('Rest')
    fall.appendleft(n); lmt = lt

def toNote(pitch):
    note = 12 * math.log2(pitch / 440) + 69.5
    octave = int(note // 12) - 1
    note_in_octave = int(note % 12)
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    res = f"{notes[note_in_octave]}{octave}"
    store(res)
    return res

def pitch_det(source):
    signal = np.frombuffer(source, dtype=np.int16).astype(np.float32)
    pitch = detor(signal)[0]
    if lb < pitch < ub:
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
