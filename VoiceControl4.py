#VoiceControl4.py 

# import whisper from OpenAI for speech recognition
import whisper
import pyaudio
import wave
import requests
import re

# ===== config =====
FLASK_API = "http://192.168.168.105:5002"  # Vision 60 IP
ENABLE_TTS = False  # listener speaking (optional)

if ENABLE_TTS:
    import pyttsx3
    tts_engine = pyttsx3.init()
    def speak_local(msg: str):
        tts_engine.say(msg); tts_engine.runAndWait()
else:
    def speak_local(msg: str): pass

model = whisper.load_model("base")  # tiny/base/small/medium/large

def record_audio(filename="command.wav", duration=3):
    """Record audio from the host device microphone and save to a WAV file."""
    import pyaudio, wave
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
    print("Listening....")
    frames = [stream.read(1024) for _ in range(int(44100/1024*duration))]
    stream.stop_stream(); stream.close()
    sample_width = p.get_sample_size(pyaudio.paInt16)
    p.terminate()
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(sample_width)
        wf.setframerate(44100)
        wf.writeframes(b"".join(frames))
    print("Audio recorded and saved as", filename)

# ---- duration parsing (numbers & number-words) ----
NUM_WORDS = {
    "zero":0, "one":1, "two":2, "three":3, "four":4, "five":5, "six":6, "seven":7, "eight":8, "nine":9,
    "ten":10, "eleven":11, "twelve":12, "thirteen":13, "fourteen":14, "fifteen":15, "sixteen":16, "seventeen":17,
    "eighteen":18, "nineteen":19, "twenty":20, "thirty":30, "forty":40, "fifty":50, "sixty":60, "seventy":70,
    "eighty":80, "ninety":90, "hundred":100
}
def words_to_int(words):
    # very simple English number parser (up to 199-ish, good for durations)
    total = 0
    parts = words.strip().split()
    i = 0
    while i < len(parts):
        w = parts[i]
        if w in NUM_WORDS:
            val = NUM_WORDS[w]
            # support “twenty five”
            if i+1 < len(parts) and parts[i+1] in NUM_WORDS and NUM_WORDS[parts[i+1]] < 10 and val >= 20:
                val += NUM_WORDS[parts[i+1]]
                i += 1
            total += val
        i += 1
    return total if total > 0 else None

def parse_duration(text: str, default_seconds=1):
    t = text.lower()
    # digits: “for 3 seconds”, “3 sec”, “for 10 s”
    m = re.search(r'\bfor\s+(\d+)\s*(seconds|second|sec|s)\b', t)
    if not m:
        m = re.search(r'\b(\d+)\s*(seconds|second|sec|s)\b', t)
    if m:
        return max(1, int(m.group(1)))

    # number words: “for five seconds”, “five seconds”
    # capture up to two words to catch “twenty five”
    m2 = re.search(r'\bfor\s+([a-z]+(?:\s+[a-z]+)?)\s*(seconds|second|sec|s)\b', t)
    if not m2:
        m2 = re.search(r'\b([a-z]+(?:\s+[a-z]+)?)\s*(seconds|second|sec|s)\b', t)
    if m2:
        val = words_to_int(m2.group(1))
        if val:
            return max(1, val)

    return default_seconds

# ---- intent parsing ----
def parse_intent(text: str):
    """
    Returns dict like:
      { "type": "move", "topic": "/command/move_forward", "duration": 3 }
      { "type": "action", "topic": "/command/setAction", "action": "sit" }
      { "type": "mode", "topic": "/command/setControlMode" }
      { "type": "stop", "topic": "/command/stop" }
      or None if not recognized
    """
    t = text.lower().strip()

    # stop cancels duration need
    if "stop" in t:
        return {"type": "stop", "topic": "/command/stop"}

    # actions: sit / stand / walk
    if "sit" in t:
        return {"type": "action", "topic": "/command/setAction", "action": "sit"}
    if "stand" in t:
        return {"type": "action", "topic": "/command/setAction", "action": "stand"}
    if "walk" in t and ("start" in t or "mode" in t or "action" in t or "walk" == t):
        # “walk mode”, “start walking”, “walk action”
        return {"type": "action", "topic": "/command/setAction", "action": "walk"}

    # mode: manual
    if "manual mode" in t or "enter manual" in t or "go manual" in t:
        return {"type": "mode", "topic": "/command/setControlMode"}

    # movement + optional duration
    duration = parse_duration(t, default_seconds=1)
    if "forward" in t:
        return {"type": "move", "topic": "/command/move_forward", "duration": duration}
    if "backward" in t or "back" in t:
        return {"type": "move", "topic": "/command/move_backward", "duration": duration}
    if "turn left" in t or ("left" in t and "turn" in t):
        return {"type": "move", "topic": "/command/turn_left", "duration": duration}
    if "turn right" in t or ("right" in t and "turn" in t):
        return {"type": "move", "topic": "/command/turn_right", "duration": duration}
    # fallback for “left/right” without “turn”
    if "left" in t:
        return {"type": "move", "topic": "/command/turn_left", "duration": duration}
    if "right" in t:
        return {"type": "move", "topic": "/command/turn_right", "duration": duration}

    return None

# ---- HTTP helpers ----
def post_json(path, body):
    url = f"{FLASK_API}{path}"
    return requests.post(url, json=body, timeout=5)

def send_move(topic: str, duration=1):
    payload = {"topic": topic, "command": {"duration": int(duration)}}
    r = post_json("/command", payload)
    print("HTTP", r.status_code, "→", r.text)

def send_action(action: str):
    payload = {"topic": "/command/setAction", "command": {"action": action}}
    r = post_json("/command", payload)
    print("HTTP", r.status_code, "→", r.text)

def send_manual_mode():
    payload = {"topic": "/command/setControlMode"}
    r = post_json("/command", payload)
    print("HTTP", r.status_code, "→", r.text)

# prime once before first movement
_PRIMED = False
def prime_robot_if_needed():
    global _PRIMED
    if not _PRIMED:
        print("Priming robot: manual mode + walk action...")
        try:
            send_manual_mode()
            send_action("walk")
        finally:
            _PRIMED = True

def main():
    while True:
        record_audio()
        result = model.transcribe("command.wav")
        said = result.get("text", "").strip()
        print("You said:", said)

        intent = parse_intent(said)
        if not intent:
            print("No valid command recognized.")
            speak_local("Command not recognized.")
            continue

        print("Intent:", intent)

        if intent["type"] == "stop":
            send_move("/command/stop", duration=1)
            continue

        if intent["type"] == "mode":
            send_manual_mode()
            continue

        if intent["type"] == "action":
            send_action(intent["action"])
            continue

        if intent["type"] == "move":
            prime_robot_if_needed()
            send_move(intent["topic"], duration=intent["duration"])
            continue

if __name__ == "__main__":
    main()

