from gtts import gTTS
from pathlib import Path
import subprocess
import shutil


# ============================================================
# LEADFLOW DEMO SALES CALL
# ============================================================

dialogues = [
    ("Sales Executive", 
     "Hi Rahul, this is Kunal from NexaSoft. "
     "I'm following up regarding your inquiry about our enterprise "
     "software platform. Is this a good time to speak?"),

    ("Customer",
     "Yes, sure. We are currently evaluating a few solutions for our company."),

    ("Sales Executive",
     "Great. Could you tell me a little more about what you're looking for?"),

    ("Customer",
     "We are looking for something that can be used by around 100 employees. "
     "The main thing for us is centralized management and reporting. "
     "We also need integration with our existing systems."),

    ("Sales Executive",
     "Understood. Our enterprise plan supports that kind of deployment, "
     "including user management, reporting and API integrations. "
     "Approximately when are you looking to implement the solution?"),

    ("Customer",
     "Ideally within the next two weeks. We have already shortlisted "
     "two vendors, so we want to make a decision fairly soon."),

    ("Sales Executive",
     "That's helpful. Is there anything specific that you would like "
     "us to address before making the decision?"),

    ("Customer",
     "Pricing is probably the biggest concern. We need to make sure "
     "it fits within our budget. We'd also like to understand how long "
     "implementation would take."),

    ("Sales Executive",
     "Absolutely. I can send you the enterprise pricing proposal "
     "and implementation timeline. We can also arrange a short "
     "product demonstration for your team."),

    ("Customer",
     "Yes, that would be useful. Please send the quotation first, "
     "and we can schedule the demo after reviewing it."),

    ("Sales Executive",
     "Perfect. I'll send the quotation and implementation details today. "
     "I'll follow up with you in two days to discuss it."),

    ("Customer",
     "Sounds good. Thank you."),

    ("Sales Executive",
     "Thank you, Rahul. Have a great day.")
]


# ============================================================
# GENERATE INDIVIDUAL AUDIO CLIPS
# ============================================================

output_dir = Path("leadflow_audio")
output_dir.mkdir(exist_ok=True)

clips = []

for i, (speaker, dialogue) in enumerate(dialogues):

    filename = output_dir / f"clip_{i:02d}.mp3"

    # Use different English TTS variants for the two speakers.
    # This isn't true voice cloning, but makes the demo easier
    # to distinguish.
    if speaker == "Sales Executive":
        tld = "co.uk"
    else:
        tld = "com"

    print(f"Generating {speaker}: {dialogue}")

    tts = gTTS(
        text=dialogue,
        lang="en",
        tld=tld,
        slow=False
    )

    tts.save(str(filename))
    clips.append(filename)


# ============================================================
# COMBINE ALL CLIPS
# ============================================================

ffmpeg = shutil.which("ffmpeg")

if ffmpeg is None:
    print("\nFFmpeg was not found.")
    print("Individual clips have been generated in:")
    print(output_dir)
    print("\nInstall FFmpeg and run the script again to create one file.")
else:

    concat_file = output_dir / "concat.txt"

    with open(concat_file, "w") as f:
        for clip in clips:
            f.write(f"file '{clip.resolve()}'\n")

    output_file = Path("leadflow_demo_call.mp3")

    command = [
        ffmpeg,
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(output_file)
    ]

    subprocess.run(command, check=True)

    print("\n========================================")
    print("LeadFlow demo call generated successfully!")
    print("========================================")
    print(f"Audio file: {output_file.resolve()}")