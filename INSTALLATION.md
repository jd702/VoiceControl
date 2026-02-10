# Installation & Setup
# Installation & Setup

This guide assumes:

- The Vision 60 robot runs the Flask+ROS2 backend ([move14.py](move14.py)).
- A separate laptop/PC runs the voice listener ([VoiceControl4.py](VoiceControl4.py)).

## Robot (Vision 60) setup

### 1) System dependencies (one time)

```bash
sudo apt update
sudo apt install -y espeak alsa-utils
```

### 2) Python dependencies (one time)

```bash
python3 -m pip install --upgrade pip
python3 -m pip install flask flask-cors prometheus-client requests numpy opencv-python pyproj
# optional: only if you enable LZ4 compression
# python3 -m pip install lz4
```

Notes:

- `rclpy`, `cv_bridge`, and ROS2 message packages come from your ROS2 install.
- `hilbert` is a local module required by [move14.py](move14.py). Ensure it is available on the robot’s PYTHONPATH.

### 3) Run the backend

```bash
# source ROS 2
ros2s

cd ~/flask_ros2
python3 move14.py
```

### 4) Optional: test TTS on the robot

```bash
espeak "Vision sixty speaking test"
```

## Listener (laptop/PC) setup

### 1) System dependencies (one time)

Linux:

```bash
sudo apt update
sudo apt install -y ffmpeg portaudio19-dev python3-dev
```

macOS:

```bash
brew install ffmpeg portaudio
```

### 2) Python dependencies (one time)

```bash
python3 -m pip install --upgrade pip
python3 -m pip install openai-whisper torch pyaudio requests
# optional: enable laptop TTS
# python3 -m pip install pyttsx3
```

### 3) Configure the robot IP

Edit [VoiceControl4.py](VoiceControl4.py) and set:

```python
FLASK_API = "http://<ROBOT_IP>:5002"
```

### 4) Connectivity check

```bash
curl http://<ROBOT_IP>:5002/status
```

### 5) Prime robot to the correct mode (one time)

```bash
curl -X POST http://<ROBOT_IP>:5002/command \
	-H 'Content-Type: application/json' \
	-d '{"topic":"/command/setControlMode"}'

curl -X POST http://<ROBOT_IP>:5002/command \
	-H 'Content-Type: application/json' \
	-d '{"topic":"/command/setAction","command":{"action":"walk"}}'
```

### 6) Run the listener

```bash
python3 VoiceControl4.py
```

## Notes

- The listener automatically primes the robot before the first movement command.
- If you hear no audio or transcription is failing, verify microphone permissions and `pyaudio` installation.