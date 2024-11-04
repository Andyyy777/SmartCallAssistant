from datetime import datetime
import os
import wave
import numpy as np
import sounddevice as sd

class AudioRecorder:
    def __init__(self, samplerate=44100, channels=2):
        self.samplerate = samplerate
        self.channels = channels
        self.recording = False
        self.paused = False
        self.frames = []

    def callback(self, indata, frames, time, status):
        if status:
            print(status)
        if self.recording and not self.paused:
            self.frames.append(indata.copy())

    def choose_device(self):
        devices = sd.query_devices()
        suitable_devices = []
        for device_index, device in enumerate(devices):
            if device['max_input_channels'] >= self.channels:
                try:
                    sd.check_input_settings(device=device_index, samplerate=self.samplerate, channels=self.channels)
                    suitable_devices.append((device_index, device['name']))
                except Exception as e:
                    print(f"Skipping device {device_index} - {device['name']}: {e}")
        if suitable_devices:
            print(f"Selected device: {suitable_devices[0][1]} (Index: {suitable_devices[0][0]})")
            return suitable_devices[0][0]
        print("No suitable device found.")
        return None

    def start_recording(self):
        if not self.recording:
            device = self.choose_device()
            if device is None:
                print("No suitable recording device available.")
                return
            try:
                self.stream = sd.InputStream(device=device, samplerate=self.samplerate, channels=self.channels, callback=self.callback)
                self.stream.start()
                self.recording = True
                self.paused = False
                self.frames = []
                print("Recording started...")
            except Exception as e:
                print(f"Failed to start recording: {e}")

    def pause_recording(self):
        if self.recording and not self.paused:
            self.paused = True
            print("Recording paused.")

    def resume_recording(self):
        if self.recording and self.paused:
            self.paused = False
            print("Recording resumed.")

    def stop_recording(self):
        if not self.recording:
            print("Recording was not started.")
            return "No recording to stop."
        self.recording = False
        self.paused = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            print("Recording stopped.")
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path = self.save_recording(filename=timestamp)
        return path

    def ensure_directory_exists(self, directory_path):
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            print(f"Created directory: {directory_path}")
        else:
            print(f"Directory already exists: {directory_path}")

    def save_recording(self, filename='output'):
        if not self.frames:
            print("No recording data to save.")
            return "Error: No data to save."
        # Convert the list of numpy arrays into a single numpy array
        audio_data = np.concatenate(self.frames, axis=0)
        # Normalize data to 16-bit format
        audio_data = np.int16((audio_data / np.max(np.abs(audio_data))) * 32767)
        # Open a WAV file for writing
        self.ensure_directory_exists("data/")
        try:
            path = "data/"+filename+'.wav'
            with wave.open(path, 'w') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(self.samplerate)
                wf.writeframes(audio_data.tobytes())
        except Exception as e:
            print(e)
            return "Error"
        print(f"Recording saved to {path}")
        return path