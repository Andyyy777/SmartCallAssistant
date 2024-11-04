from openai import OpenAI
class AIAssistant:
    def __init__(self):
        print("init ai assistant")
        try:
            self.client = OpenAI()
        except Exception as e:
            print("error", e)

    def process(self, path):
        # connect to open ai whisper model upload the wav recording stored at path to convert to text, 
        # then call gpt-4o-mini to summarize the text into recording summarization

        print('triggered')
        # Use Whisper model to transcribe audio
        with open(path, 'rb') as audio_file:
            try:
                transcription_response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            except Exception as e:
                print(e)
            transcription_text = transcription_response['text']
            print("Transcription:", transcription_text)

        # Summarize the transcribed text with GPT-4
        summary_response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an assistant that summarizes text."},
                {"role": "user", "content": f"Summarize this text: {transcription_text}"}
            ]
        )
        summary = summary_response['choices'][0]['message']['content']
        print("Summary:", summary) 
        return summary