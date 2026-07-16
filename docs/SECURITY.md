# Security Guidance

- Configure the robot URL with `VOICE_FLASK_API`; never commit the real host address.
- Do not add API keys, passwords, tokens, private backend files, recordings, or environment files to Git.
- Whisper runs locally and does not need an OpenAI API key.
- Treat all transcribed speech as untrusted input. Keep the parser allowlisted and validate commands again on the robot backend.
- Protect the robot API with network restrictions, authentication, authorization, rate limits, and independent E-stop controls.
- Review recordings before sharing; audio may contain personal or location-sensitive information.
- Rotate any secret that was previously committed, even if it was later deleted.
