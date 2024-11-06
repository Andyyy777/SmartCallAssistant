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

        # Use Whisper model to transcribe audio
        try:
            with open(path, 'rb') as audio_file:
                transcription_response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            transcription_text = transcription_response.text
            print("Transcription:", transcription_text)
        except Exception as e:
            print(e)

        # Summarize the transcribed text with GPT-4
        try:
            summary_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": """
                    You are an assistant tasked with transcribing conversations between a patient and a medical professional. For each line, separate the speaker and their words in the format Name: Content. Then, generate a summary for the entire conversation, focusing on the main points discussed.
                    Example conversation transcription: 'Hello, this is Officer Indy. How can I help you? Hi, this is Helen. I really need your help.'

                    Desired output:

                    1.Transcribed conversation:
                    Officer Indy: Hello, this is Officer Indy. How can I help you?
                    Helen: Hi, this is Helen. I really need your help.
                     
                    2.Summary:
                    Helen reached out to Officer Indy for assistance, expressing that she is in need of help. Officer Indy acknowledged the conversation and is ready to assist her."
                     """},
                    {"role": "user", "content": f"Here is the conversation transcription: {transcription_text}"}
                ]
            )
            summary = summary_response.choices[0].message.content
            print("Summary:", summary) 
        except Exception as e:
            print(e)
        return summary