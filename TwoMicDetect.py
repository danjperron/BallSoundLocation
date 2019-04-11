#!/usr/bin/python3
from ctypes import *
from contextlib import contextmanager
import struct
import pyaudio
import wave
import sys


# demonstration pour utiliser deux microphones pour detecter
# la localisation du ballon avec le bruit lors de l'impact.
# Daniel Perron  Avril 2019.
#
#
#  La vitesse du son dans l'air depend beaucoup de la temperature il serait don$
#  vitesse du son  et de corriger C.
#  C pour la vitesse du son dans l'air (m/s)
#  343 m/s 20C
#  v = 331m/s + 0.6m/s/C * T
# modification pour 1 d
C = 343.0
#
#
#  ce code est pour une resolution sur un axe, Beaucoup plus simple
#
#
# Soit un micro A et B
# soit un point d'impact C entre A et B
#
#
#  et que la distance  AB = AC + CD
#
#  Nous savons que lors de l'impact le delais entre
#  les deux micros sera la difference entre les segments AC et CB
#
#  donc      DX =  delais en seconde * C (vitesse du son)
#  ce qui donne   DX = CB - AC
#
#ref: audio
# https://engineersportal.com/blog/2018/8/23/recording-audio-on-the-raspberry-pi-with-python-and-a-usb-microphone


#distance entre mic et mic2 (m)

DistMic1ToMic2 = 2.4


#niveau de detection des micros
Threshold = 100
Mic1GotPulse = 0
Mic2GotPulse = 0
#counter de chaque  sample de 44100Hz
Counter =0
Flush = 0

#initialisation audio

form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 2 # 2 channel
samp_rate = 44100 # 44.1kHz sampling rate
chunk = 4096 # 2^12 samples for buffer
record_secs = 100 # seconds to record
dev_index = 2 # device index found by p.get_device_info_by_index(ii)





#fonction pour determiner  le claquement du ballon sur les deux micros

def checkForTrigger(data):
  global Counter
  global Mic1GotPulse
  global Mic2GotPulse
  global Threshold

  #convert binary to 16 bits

  s_data = struct.unpack('h'*(len(data)//2),data)
  for i in range(0,len(data)//2,2) :
    mic1  = abs(s_data[i])
    mic2  = abs(s_data[i+1])

    if Mic1GotPulse == 0 :
      if mic1 > Threshold:
        Mic1GotPulse= Counter

    if Mic2GotPulse == 0 :
      if mic2 > Threshold:
        Mic2GotPulse= Counter
    Counter+=1

  if (Mic1GotPulse>0) and (Mic2GotPulse>0) :
      return True
  return False




#get ridd of warning error from pyaudio

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)





with noalsaerr():
    audio = pyaudio.PyAudio()
    # create pyaudio stream
    stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                    input_device_index = dev_index,input = True, \
                    frames_per_buffer=chunk)



# loop through stream and append audio chunks to frame array
for ii in range(0,int((samp_rate/chunk)*record_secs)):

    data = stream.read(chunk)
    if Flush > 0:
       Flush-=1
    else:
       if Counter == 0:
         print("pret pour le ballon !  ",end="")
         sys.stdout.flush()
       if  checkForTrigger(data):
         #ok we got pulse let's display the time
         #print("mic1 count :", Mic1GotPulse)
         #print("mic2 count :", Mic2GotPulse)

         #conversion du compteur en delais
         t1 = Mic1GotPulse / samp_rate
         t2 = Mic2GotPulse / samp_rate

         impact = (DistMic1ToMic2 - (t2-t1) * C) / 2.0

         print("impact {:.2f}m".format(impact))
         Flush = 3
         Mic1GotPulse=0
         Mic2GotPulse=0
         Counter=0



# stop the stream, close it, and terminate the pyaudio instantiation
stream.stop_stream()
stream.close()
audio.terminate()

print("Done")


# save the audio frames as .wav file
#wavefile = wave.open(wav_output_filename,'wb')
#wavefile.setnchannels(chans)
#wavefile.setsampwidth(audio.get_sample_size(form_1))
#wavefile.setframerate(samp_rate)
#wavefile.writeframes(b''.join(frames))
#wavefile.close()






