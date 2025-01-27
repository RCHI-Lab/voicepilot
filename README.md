Code for paper: [VoicePilot: Harnessing LLMs as Speech Interfaces for Physically Assistive Robots](https://dl.acm.org/doi/10.1145/3654777.3676401)

Authors: Akhil Padmanabha*, Jessie Yuan*, Janavi Gupta, Zulekha Karachiwalla, Carmel Majidi, Henny Admoni, Zackory Erickson

Hardware: 
-
- [Obi feeding robot](https://meetobi.com/)
- Laptop
- External USB-connected mic (optional)

Instructions to set up interface: 
-
Setup environment, clone repo, and install required dependencies:
```
conda create -n obienv python=3.12
conda activate obienv
git clone https://github.com/RCHI-Lab/voicepilot.git
brew install portaudio ffmpeg bash
pip install -r requirements.txt
```

Instructions to use interface: 
- 
1. Fill the bowls with the desired foods.
2. Open two different terminal windows on the laptop
3. In the first window, run `python3 /path/to/voicepilot/obi-main.py`
4. In the second window, run `python3 /path/to/voicepilot/obi-chatgpt-voice.py`
5. Say "Hey Obi" into the mic and wait for the beep. After the beep, speak your command to the robot.
6. Let the robot carry out this instruction. The words "Ready for another command" will play to indicate that the robot is done excecuting the previous command and ready for a new one. 
