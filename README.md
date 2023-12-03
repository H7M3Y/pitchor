# note-detector
Simple but practical real-time music note detector with an aesthetical oneline appearance:

```
[#>_] G#3 : 208.70 Hz |  G#3 D4 - G3 D4 G4 D5 x D5 - - C5 x x C5 - - D5 x x D5 G3 - D5 x       
```

## Usage
```
usage: pitchor [-h] [-s SIZE] [-r RATE] [-d DELTA] [-R REMAIN] [-l LOWEST] [-u UPPEST]

Simple but practical real-time music note detector

options:
  -h, --help            show this help message and exit
  -s SIZE, --size SIZE  the number of samples collected at a delta time.
  -r RATE, --rate RATE  microphone sampling rate
  -d DELTA, --delta DELTA
                        time duration of a single detection (unit: s. the same below)
  -R REMAIN, --remain REMAIN
                        time that the detected notes remain
  -l LOWEST, --lowest LOWEST
                        lower bound of detection
  -u UPPEST, --uppest UPPEST
                        upper bound of detection
```

## Require
libraries: numpy, pyaudio, aubio

Also a microphone :)

## Roadmap
- [x] Get pitch
- [x] Convert to note
- [x] Solve precision issue
- [x] Solve ambient noise issue
- [x] Add an waterfall layout and a buffer to stabilize vibrate notes, which make this script truly practical
- [x] beautify its appearance
- [x] Solve the `Rest` issue
- [ ] Outputs to file
- [x] Custom arguments
