import pyaudio, wave, datetime, whisper, openai, time
import ffmpeg
import pvporcupine
import struct
import math 
from pydub import AudioSegment
from pydub.playback import play
import simpleaudio as sa

import threading



openai.api_key = #OPENAI_API_KEY


porcupine = pvporcupine.create(
  access_key= #PORCUPINE_ACCESS_KEY,
  keyword_paths=['Hey-Obi_en_mac_v2_2_0.ppn'],
  sensitivities = [0.5]
)

participantid = input("Enter the participant's ID: ")
ct = datetime.datetime.now()
LOG_FILE_PATH = f"obi-logs/{participantid}_{ct}.txt"
TEMPERATURE = 0.1

pa = pyaudio.PyAudio()
channels = 1
sample_format = pyaudio.paInt16
fs = porcupine.sample_rate
mic_num = 0
audio_stream = pa.open(
                rate=fs,
                channels=channels,
                format=sample_format,
                input=True,
                frames_per_buffer=porcupine.frame_length,
                input_device_index=mic_num)

def sound_play_threading(sound):
  wave_obj = sa.WaveObject.from_wave_file(sound)
  play_obj = wave_obj.play()


def get_chatgpt_code(messages):
  begintime = time.time()
  completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-0613", 
    temperature=TEMPERATURE,
    messages=messages
  )
  elapsedtime = time.time() - begintime
  output = completion.choices[0].message.content
  messages.append({"role": "assistant", "content": output})
  with open(LOG_FILE_PATH, 'a') as f:
    f.write(f'ChatGPT Response Time: {elapsedtime}\nChatGPT: {output}\n\n\n')
  print("ChatGPT Response Time: " + str(elapsedtime))
  print("ChatGPT: " + output)
  mod_output = output.replace("import obirobot", "")
  if '```' in mod_output:
    mod_output = mod_output.split('```')[1]
    mod_output = mod_output.replace("python", "")
  with open('obi-code.txt', 'a') as f:
    f.write(mod_output)
  print()


def process_frames(frames):
  ct = datetime.datetime.now()
  RECORDING_FILE_PATH = f"voice-recordings/{ct}.wav"
  print('Finished recording.')
  sound_file = "sounds_wav/processing.wav"
  sound_play_threading(sound_file)
  #play(sound)

  transcription_begintime = time.time()
  # Save the recorded data as a WAV file
  wf = wave.open(RECORDING_FILE_PATH, 'wb')
  wf.setnchannels(channels)
  wf.setsampwidth(pa.get_sample_size(sample_format))
  wf.setframerate(fs)
  wf.writeframes(b''.join(frames))
  wf.close()

  model = whisper.load_model("base.en")
  result = model.transcribe(RECORDING_FILE_PATH, fp16=False)["text"]
  transcription_elapsedtime = time.time() - transcription_begintime
  print("Transcription Time: " + str(transcription_elapsedtime))
  print("You: " + result)
  print()
  return result

with open('obi-prompt.txt', 'r') as f:
  file_contents = f.read()
with open(LOG_FILE_PATH, 'w') as f:
  f.write(f'System: {file_contents} \n\nTemp: {TEMPERATURE} \n\n\n')
messages = [{"role": "system", "content": file_contents}]


recording = False
SHORT_NORMALIZE = (1.0/32768.0)
swidth = 2
def rms(frame):
    count = len(frame)/swidth
    format = "%dh"%(count)
    # short is 16 bit int
    shorts = struct.unpack( format, frame )

    sum_squares = 0.0
    for sample in shorts:
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n
    # compute the rms 
    rms = math.pow(sum_squares/count,0.5)
    return rms * 1000


if __name__ == "__main__":
  audio_stream.start_stream()
  mic_silence_value = 4 #TODO: change 
  print()
  print("Current set mic silence value:", mic_silence_value)
  current_mic_value = round(rms(audio_stream.read(1024)),2) 
  print("Current silence value (assuming no one talking):", current_mic_value)
  print()
  print()
  print("READY")


  try: 
    while True:
      data = audio_stream.read(porcupine.frame_length)
      pcm = struct.unpack_from("h" * porcupine.frame_length, data)
      keyword_index = porcupine.process(pcm)
      if keyword_index == 0:
        sound_file = "sounds_wav/heyobi-beep.wav"
        sound_play_threading(sound_file)
        data = audio_stream.read(1024)
        threshold = mic_silence_value*2
        print()
        print('detected obi')
        print("Silence Threshold:", threshold)
        print()        
        frames = []
        timeout_started = False
        timeout_start_time = time.time()
        threshold_timeout = 1.5 #second

        passed_initial_threshold = 0 #0 is false, 1 is true 
        passed_initial_threshold_start_time = 0 
        passed_initial_threshold_timeout = 0.2
        passed_initial_threshold_started = False

        while True:
          last_data = data
          data = audio_stream.read(1024)
          print("Noise Level:", round(rms(data),2), threshold)
          if rms(data) > threshold and passed_initial_threshold == 0 and passed_initial_threshold_started == False:
            passed_initial_threshold_start_time = time.time()
            #passed_initial_threshold = 1
            frames.append(last_data)
            frames.append(data)
            print("passed initial threshold")
            passed_initial_threshold_started = True
          elif passed_initial_threshold_started == True: 
            if rms(data) < threshold:
              frames = []
              passed_initial_threshold = 0
              passed_initial_threshold_started = False
            elif time.time()-passed_initial_threshold_start_time <  passed_initial_threshold_timeout:
              frames.append(data)
              print(time.time()-passed_initial_threshold_start_time)
            else:
              passed_initial_threshold = 1
              frames.append(data)
              print("passed initial threshold")
              passed_initial_threshold_started = False
          elif passed_initial_threshold == 1:
            if timeout_started == True and time.time()-timeout_start_time > threshold_timeout:
              frames.append(data)
              print("ended")
              break
            elif rms(data) < threshold and timeout_started == False:
              timeout_start_time = time.time()
              print("started")
              timeout_started = True
              frames.append(data)
            elif rms(data) < threshold and timeout_started == True:
              frames.append(data)
              print("Time Elapsed since Silence started:", time.time()-timeout_start_time)
            else:
              frames.append(data)
              timeout_start_time = time.time()
              timeout_started = False
          else:
            print("Waiting for person to speak")
        
        audio_stream.stop_stream()
        #audio_stream.close()
        chatgpt_input = process_frames(frames)
        with open(LOG_FILE_PATH, 'a') as f:
          f.write(f'User: {chatgpt_input}\n\n\n')
        messages.append({"role": "user", "content": chatgpt_input})
        get_chatgpt_code(messages)
        audio_stream.start_stream()

          
  except KeyboardInterrupt:
    with open('obi-code.txt', 'w') as f:
      f.write('SYSTEM_TERMINATE()')
    pass

  pa.terminate()