import time, board, busio, adafruit_midi, usb_midi
from log import log
from adafruit_midi.control_change import ControlChange
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.program_change import ProgramChange
from settings import liveFile


uart = busio.UART(board.GP0, board.GP1, baudrate=31250, timeout=0.001)  # init UART
midi_in_channel = 1
midi_out_channel = 1
midi0 = adafruit_midi.MIDI(
    midi_in=uart,
    midi_out=uart,
    in_channel=(midi_in_channel - 1),
    out_channel=(midi_out_channel - 1),
    debug=False,
    )

midi1 = adafruit_midi.MIDI(midi_out=usb_midi.ports[0],midi_in=usb_midi.ports[0], out_channel=0, in_channel=4)
midi = midi0
def setupMidi(mode):
    if mode.upper() == "MIDI":
        midi = midi0
    elif mode.upper() == "USB":
        midi = midi1

def sendCC(program, value):
    midi.send(ControlChange(program, value))

def sendPC(program):
    midi.send(ProgramChange(program))

# Check CC 3 For SOng Change
def checkSong(CurrentSong, mode):
    if mode == "Preset":
        songNo = CurrentSong
        midiIn = midi.receive()
        try:
            if midiIn.control is 3: 
                songNo = midiIn.value
        except Exception:
                    songNo = CurrentSong  
        return songNo
    if mode == "Live":
        songName = []
        try: song = CurrentSong[0]
        except Exception: song = ""
        try: bpm = CurrentSong[2]
        except Exception: bpm = 120
        try: key = CurrentSong[1]
        except Exception: key = ""
        try: currentPart = CurrentSong[3]
        except Exception: currentPart = ""
        try: nextPart = CurrentSong[3]
        except Exception: nextPart = ""
        midiIn = midi.receive()
        try:
            if (midiIn.note == 5) & (midiIn.velocity > 0):
                pass
        except Exception as e:
            if str(e) != "'NoneType' object has no attribute 'note'":
                log(str(e))
            return CurrentSong
        if midiIn.note == 1:
            velocity = midiIn.velocity
            while velocity == 127:
                midiIn = midi.receive()
                try:
                    if ((midiIn.note <= 3 or ((12 <= midiIn.note) & (midiIn.note <= 23))) & (midiIn.velocity > 0)): 
                        pass
                except Exception as e:
                    if str(e) != "'NoneType' object has no attribute 'note'":
                        log(str(e))
                    continue
                if midiIn.note == 0:
                    try:
                        song = ""
                        midiChar = chr(midiIn.velocity)
                        songName.append(midiChar)
                    except Exception as e:
                        if str(e) != "'NoteOff' object has no attribute 'velocity'":
                            log(str(e))
                        pass
                if midiIn.note == 3:
                    bpm = midiIn.velocity
                if midiIn.note == 2:
                    bpm += midiIn.velocity
                if (12 <= midiIn.note) & (midiIn.note <= 23):
                    if midiIn.note == 12: key = "C"
                    elif midiIn.note == 13: key = "C#"
                    elif midiIn.note == 14: key = "D"
                    elif midiIn.note == 15: key = "D#"
                    elif midiIn.note == 16: key = "E"
                    elif midiIn.note == 17: key = "F"
                    elif midiIn.note == 18: key = "F#"
                    elif midiIn.note == 19: key = "G"
                    elif midiIn.note == 20: key = "G#"
                    elif midiIn.note == 21: key = "A"
                    elif midiIn.note == 22: key = "A#"
                    elif midiIn.note == 23: key = "B"
                if midiIn.note == 5: currentPart = str(liveFile['parts'][midiIn.velocity-1])
                if midiIn.note == 4: currentPart = currentPart + ";" + str(midiIn.velocity)
                if midiIn.note == 8: nextPart = str(liveFile['parts'][midiIn.velocity-1])
                if midiIn.note == 7: nextPart = nextPart + ";" + str(midiIn.velocity)
                if midiIn.note == 1: velocity = midiIn.velocity
            for i in songName:
                song += i
        log(str(song))
        log(str(bpm))
        log(str(key))
        log(str(currentPart))
        log(str(nextPart))
        return song, key, bpm, currentPart, nextPart