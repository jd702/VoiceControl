# Voice Control (Vision 60)

Speech‑driven control for the Vision 60 robot. A local listener records audio, uses OpenAI Whisper for speech recognition, parses intents, and sends HTTP commands to the robot’s Flask+ROS2 backend.

## What’s in this repo

- `VoiceControl4.py`: Microphone listener, Whisper transcription, intent parsing, HTTP commands.
- Backend API server (robot-side) is private and not included in this repo.
- `VoiceControlInstructions`: Legacy notes (superseded by this README + INSTALLATION).
- [docs/images/architecture.svg](docs/images/architecture.svg): System architecture diagram.
- [docs/images/endpoints.svg](docs/images/endpoints.svg): REST endpoint overview.

## Architecture

![Architecture](docs/images/architecture.svg)

Flow summary:

1) Mic audio → Whisper transcription on the laptop/PC
2) Intent parsing (move/turn/action/mode/stop)
3) HTTP POST to the robot backend
4) Robot executes command + streams telemetry

## API overview

![Endpoints](docs/images/endpoints.svg)

Key endpoints (robot backend):

- Commands: `POST /command`, `POST /mpc/goal`, `POST /command/send_local_goal`, `POST /command/send_goal`
- Status: `GET /status`, `GET /gps`, `GET /imu`, `GET /odom`
- Point clouds: `GET /pointcloud`, `GET /obstmap`, plus compressed variants
- Camera proxy: `GET /proxy_camera_feed/<camera>`, `GET /proxy_camera_snapshot/<camera>`
- Metrics: `GET /metrics`, `GET /pc_metrics`, `GET /pc_status`

## Quick start

1) Install dependencies on the robot and the listener machine (see [INSTALLATION.md](INSTALLATION.md)).
2) Update the robot IP in `VoiceControl4.py`:
   - `FLASK_API = "http://<ROBOT_IP>:5002"`
3) Start the Flask+ROS2 backend on the robot (private backend).
4) Run the listener on your laptop/PC:
   - `python3 VoiceControl4.py`

## Configuration

Edit [VoiceControl4.py](VoiceControl4.py):

- `FLASK_API`: Robot backend URL.
- `ENABLE_TTS`: If `True`, the laptop/PC speaks back using `pyttsx3`.
- `whisper.load_model("base")`: Change to `"tiny" | "base" | "small" | "medium" | "large"` based on speed vs accuracy.

Backend configuration is robot‑side and private. Keep sensitive values out of this repo.

## Voice commands

Examples that the parser understands:

- “forward for 3 seconds”
- “backward 2 seconds”
- “turn left for five seconds”
- “turn right”
- “sit”, “stand”, “walk”, “stop”
- “enter manual mode”

Notes:

- If no duration is given, a default of 1 second is used.
- The listener primes the robot (manual mode + walk action) before the first movement command.

## Troubleshooting

- Can’t reach the robot: run `curl http://<ROBOT_IP>:5002/status`.
- Audio capture errors: ensure `portaudio` is installed and your mic works.
- Slow transcription: try a smaller Whisper model (e.g., `"tiny"`).

## License

Add a license if you plan to distribute this repo.
