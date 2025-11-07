from openai import OpenAI
from ..audio_recorder.audio_recorder import AudioRecorder

class AIAssistant:
    def __init__(self):
        self.recorder = AudioRecorder()
        print("init ai assistant")
        try:
            self.client = OpenAI()
        except Exception as e:
            print("error", e)

    def process(self, path):
        # connect to open ai whisper model upload the wav recording stored at path to convert to text, 
        # then call gpt-4o-mini to summarize the text into recording summarization

        # Use Whisper model to transcribe audio
        try:
            chunks = self.recorder.chunk_audio(path, chunk_seconds=30, overlap=2)
            print(f"Processing {len(chunks)} chunks for transcription.")
            transcription_parts = []
            confidences = []

            for idx, (chunk_path, offset_seconds) in enumerate(chunks):
                with open(chunk_path, "rb") as audio_file:
                    resp = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        prompt=f"Medical intake call transcript – chunk {idx + 1}/{len(chunks)}",
                        response_format="verbose_json"
                    )
                transcription_parts.append(resp.text.strip())
                segments = []
                for seg in resp.segments:
                    absolute_start = seg.start + offset_seconds
                    absolute_end = seg.end + offset_seconds
                    segments.append({
                        "start": absolute_start,
                        "end": absolute_end,
                        "confidence": max(0.0, min(1.0, 1.0 + seg.avg_logprob)),
                        "text": seg.text,
                    })

                confidences.append(segments)
            transcription_text = " ".join(transcription_parts)
            print("Transcription:", transcription_text)
        except Exception as e:
            print(e)

        # Summarize the transcribed text with GPT-4
        try:
            summary_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": """
                     You are an assistant cleaning up medical conversation transcripts. The user provides:
                    - `segments`: an ordered list where each item has `confidence` (float in [0,1] or log-prob equivalent) and `text`.
                    - `combined_transcript`: the stitched conversation text.

                    Your tasks:
                    1. Remove duplicated or truncated phrases that might appear because of overlapping audio chunks.
                    2. Reformat each distinct utterance as `<Name: Content>`, inferring speaker labels from context when possible ("Patient", "Clinician" if unsure).
                    3. Maintain strict chronological order. Walk through the cleaned utterances in sequence and group only **consecutive** lines that have the same confidence value; when the confidence changes, start a new group, even if that value reappears later.
                    4. Produce a concise overall summary of the conversation, highlighting key requests, symptoms, and recommended actions.
                     
                    Example input:
                    {
                    "combined_transcript": "Doctor: Good morning. Patient: Hi Doctor, I have chest tightness. Doctor: Since when? Patient: Two days ago and it worsened last night. Doctor: Any shortness of breath? Patient: Yes, especially when climbing stairs. Doctor: We'll run an ECG and blood tests. Patient: Thank you.",
                    "segments": [
                        {"confidence": 0.94, "text": "Doctor: Good morning."},
                        {"confidence": 0.82, "text": "Patient: Hi Doctor, I have chest tightness."},
                        {"confidence": 0.82, "text": "Patient: Hi Doctor, I have chest tightness."},
                        {"confidence": 0.88, "text": "Doctor: Since when?"},
                        {"confidence": 0.79, "text": "Patient: Two days ago and it worsened last night."},
                        {"confidence": 0.75, "text": "Doctor: Any shortness of breath?"},
                        {"confidence": 0.75, "text": "Patient: Yes, especially when climbing stairs."},
                        {"confidence": 0.9,  "text": "Doctor: We'll run an ECG and blood tests."},
                        {"confidence": 0.9,  "text": "Patient: Thank you."}
                    ]
                    }
                    Example output:
                    {
                    "transcriptions_by_confidence": [
                        {
                        "confidence": 0.94,
                        "lines": ["Doctor: Good morning."]
                        },
                        {
                        "confidence": 0.82,
                        "lines": ["Patient: Hi Doctor, I have chest tightness."]
                        },
                        {
                        "confidence": 0.88,
                        "lines": ["Doctor: Since when?"]
                        },
                        {
                        "confidence": 0.79,
                        "lines": ["Patient: Two days ago and it worsened last night."]
                        },
                        {
                        "confidence": 0.75,
                        "lines": [
                            "Doctor: Any shortness of breath?",
                            "Patient: Yes, especially when climbing stairs."
                        ]
                        },
                        {
                        "confidence": 0.9,
                        "lines": [
                            "Doctor: We'll run an ECG and blood tests.",
                            "Patient: Thank you."
                        ]
                        }
                    ],
                    "summary": "Patient reports two-day history of chest tightness worsening overnight with exertional dyspnea. Doctor plans ECG and blood tests; patient agrees."
                    }
                     

                    Your response should be a JSON object structured as follows:
                    Return a JSON object with:
                    {
                    "transcriptions_by_confidence": [
                        {
                        "confidence": <value>,
                        "lines": ["Speaker: text", ...]
                        },
                        ...
                    ],
                    "summary": "..."
                    }
                     """},
                    {"role": "user", "content": f"Here is the conversation transcription: {transcription_text}\n\nSegments: {confidences}"}
                ]
            )
            summary = summary_response.choices[0].message.content
            print("Summary:", summary) 
            return summary
        except Exception as e:
            print("Error:", e)
            return "Error during processing: " + str(e)