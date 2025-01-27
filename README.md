Code for paper: [VoicePilot: Harnessing LLMs as Speech Interfaces for Physically Assistive Robots](https://dl.acm.org/doi/10.1145/3654777.3676401)

Authors: Akhil Padmanabha*, Jessie Yuan*, Janavi Gupta, Zulekha Karachiwalla, Carmel Majidi, Henny Admoni, Zackory Erickson

Hardware: 
-
- [Obi feeding robot](https://meetobi.com/)
- Laptop with MacOS
- External USB-connected mic (optional)

Instructions to set up interface: 
-
Setup environment, clone repo, and install required dependencies:
```
conda create -n obienv python=3.12
conda activate obienv
git clone https://github.com/RCHI-Lab/voicepilot.git
cd voicepilot
brew install portaudio ffmpeg
pip install -r requirements.txt
```

Instructions to use interface: 
- 
1. Optional: run `python3 /path/to/voicepilot/mouth-pos-setup.py` and follow the instuctions displayed to set a custom feeding position.
2. Fill the bowls with the desired foods and ensure the robot and mic are plugged into the laptop via USB.
3. Open two different terminal windows on the laptop. 
4. In the first window, run:
```
conda activate obienv
python3 /path/to/voicepilot/obi-main.py
```
5. In the second window, run:
```
conda activate obienv
python3 /path/to/voicepilot/obi-chatgpt-voice.py
```
6. Say "Hey Obi" into the mic and wait for the beep. After the beep, speak your command to the robot.
7. Let the robot carry out this instruction. The words "Ready for another command" will play to indicate that the robot is done excecuting the previous command and ready for a new one.
8. To quit, Ctrl + C *only* in the terminal in which `obi-chatgpt-voice.py` is running; this will kill both scripts.

Instructional video for users: [link](https://youtu.be/-VOWMa4Iptc).
Reference sheet for users: 
