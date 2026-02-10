# Installation & Setup

This guide assumes:

- The Vision 60 robot runs the Flask+ROS2 backend (e.g., `move10.py`).
- A separate laptop/PC runs the voice listener (`VoiceControl4.py`).

## Robot (Vision 60) setup

### 1) System dependencies (one time)

```bash
sudo apt update
sudo apt install -y espeak alsa-utils
```

### 2) Run the backend

```bash
# source ROS 2










































































- If you hear no audio or transcription is failing, verify microphone permissions and `pyaudio` installation.- The listener automatically “primes” the robot before the first movement command.## Notes```python3 VoiceControl4.py```bash### 6) Run the listener```  -d '{"topic":"/command/setAction","command":{"action":"walk"}}'  -H 'Content-Type: application/json' \curl -X POST http://<ROBOT_IP>:5002/command \  -d '{"topic":"/command/setControlMode"}'  -H 'Content-Type: application/json' \curl -X POST http://<ROBOT_IP>:5002/command \```bash### 5) Prime robot to the correct mode (one time)```curl http://<ROBOT_IP>:5002/status```bash### 4) Connectivity check```FLASK_API = "http://<ROBOT_IP>:5002"```pythonEdit `VoiceControl4.py` and set:### 3) Configure the robot IP```# python3 -m pip install pyttsx3# optional: enable laptop TTSpython3 -m pip install openai-whisper torch pyaudio requestspython3 -m pip install --upgrade pip```bash### 2) Python dependencies (one time)```brew install ffmpeg portaudio```bashmacOS:```sudo apt install -y ffmpeg portaudio19-dev python3-devsudo apt update```bashLinux:### 1) System dependencies (one time)## Listener (laptop/PC) setup```espeak "Vision sixty speaking test"```bash### 3) Optional: test TTS on the robot```python3 move10.pycd ~/flask_ros2os2s