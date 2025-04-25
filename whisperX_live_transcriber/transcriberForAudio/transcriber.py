import torch
import whisperx

# Параметры модели
language_code = "ru" 
device = "cuda" if torch.cuda.is_available() else "cpu"
whisper_model_name = "turbo" 
compute_type = "float32" 

# Путь к аудиофайлу
audio_file = "audio/test.mp3" 

model = whisperx.load_model(whisper_arch=whisper_model_name, device=device, language=language_code, compute_type=compute_type)

audio = whisperx.load_audio(audio_file)

result = model.transcribe(audio)

print(result["segments"])