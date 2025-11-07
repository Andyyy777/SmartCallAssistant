from datetime import datetime
import os
import wave
import numpy as np
import sounddevice as sd
from scipy.signal import resample_poly
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

class AudioRecorder:
    def __init__(self, samplerate=44100, channels=1):
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
        print("Available devices:", devices)
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
        # Collapse stereo to mono so Whisper gets a single channel signal.
        if audio_data.ndim > 1 and audio_data.shape[1] > 1:
            audio_data = audio_data.mean(axis=1)

        audio_data = self._trim_silence(audio_data)

        # Resample to 16 kHz for Whisper unless it is already there.
        target_rate = 16000
        if self.samplerate != target_rate:
            audio_data = resample_poly(audio_data, target_rate, self.samplerate)
        else:
            target_rate = self.samplerate

        # Normalize after all processing so we keep the max dynamic range.
        peak = np.max(np.abs(audio_data)) or 1.0
        audio_data = np.clip(audio_data / peak, -1.0, 1.0)
        audio_data = np.int16(audio_data * 32767)
        # Open a WAV file for writing
        target_rate = 16000
        self.ensure_directory_exists("data/")
        try:
            path = "data/"+filename+'.wav'
            with wave.open(path, 'w') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(target_rate)
                wf.writeframes(audio_data.tobytes())
        except Exception as e:
            print(e)
            return "Error"
        print(f"Recording saved to {path}")
        return path

    def _trim_silence(self, data, threshold=0.01):
        """Trim leading / trailing silence based on a small amplitude threshold."""
        mask = np.abs(data) > threshold
        if not np.any(mask):
            # all silence; fall through so user knows it’s empty
            return data
        first, last = np.where(mask)[0][[0, -1]]
        return data[first:last + 1]
    
    def chunk_audio(self, wav_path, chunk_seconds=30, overlap=2):
        """Split long WAVs into overlapping chunks and return the temp file paths in order."""
        with wave.open(wav_path, "rb") as wf:
            samplerate = wf.getframerate()
            channels = wf.getnchannels()
            num_frames = wf.getnframes()
            audio = np.frombuffer(wf.readframes(num_frames), dtype=np.int16)

        if channels > 1:
            audio = audio.reshape(-1, channels).mean(axis=1).astype(np.int16)

        chunk_size = chunk_seconds * samplerate
        hop = max(chunk_size - overlap * samplerate, 1)
        chunk_paths = []
        temp_dir = Path(tempfile.mkdtemp(prefix="chunks_", dir=PROJECT_ROOT / "tmp"))

        for chunk_idx, start in enumerate(range(0, len(audio), hop)):
            end = min(start + chunk_size, len(audio))
            chunk = audio[start:end]
            chunk_path = temp_dir / f"chunk_{chunk_idx:04d}.wav"
            with wave.open(str(chunk_path), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(samplerate)
                wf.writeframes(chunk.tobytes())
            chunk_paths.append((str(chunk_path), start / samplerate))

            if end == len(audio):
                break
        print(f"Created {len(chunk_paths)} chunks in {temp_dir}")
        return chunk_paths
