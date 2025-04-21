import torch
import whisperx
from dotenv import load_dotenv
import os
import time
import gc
import json

# Загружаем переменные окружения
load_dotenv()
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

#TODO: надо чётко увидеть где узкое место. ни один из показателей панели задача не забивается на 100%(кроме видеопамяти, если не юзать gc)
        # для этого нужно мониторить ресурсы видокарты. Ну то есть надо понять потолок в а)Предобработке на CPU; б)PCIe(передача на видеокарту); в)Видокарте; г)Считывание с диска;
        # это отчасти из любопыства. Для этого есть разные иструменты. в питоне, торче, NVIDIA Nsight

#TODO: можно ли запускать паралельно на одной и той же модели вычисления? То есть обрабатывать несколько аудиофайлов сразу? ну тип вдруг.

#TODO: можно ли в whisperX загонять промты, как в обычный whisper?


#Некоторые переменные, которые надо настроить.
#установи значения перед запуском:
language_code = "ru" # предпологается давать пользователю вручную выбирать эту переменную, чтобы не было ошибок при распазновании первых 30 секунд речи.
audio_path = "AUDIO_for_transcription/test8min.mp3"
min_speakers_count = 1
max_speakers_count = 3

#возможность сократить время обработки от параметров аудиофайла:
#TODO: Если спикер только один и пользователь об этом сообщает, то ни надо запускать Диаризацию 100%.
#TODO: Если спикер только один, то можно уточнить у пользователя по поводу Align(Align точно нужен для Диаризации, но для одного спикера - тут вопрос к user): 
#           если без Align: предложения по итогу компануются по порядку в группы по 25-30 секунд максимум(на это тратится меньше сил и ответ даётся в два раза быстрее.))
                #тут если нет диаризации, то можно gc выключить.(по сути можно на отдельную машину диаризацию вынести.)
#           если с Align: то у каждого предложения явно написо время начала и конца, но на это тратиться больше сил и времени обработки(x2)

#зависит от устройства:
device = "cuda"  # поменяй на "cpu", если у вас нет нормальной видеокарты.
use_gc = True # все три модели(странскрибации, разбиение по времени слова и разбиение по спикерам) не умещаются в 8GB GPU, поэтому надо отчищать.
#                   (либо найти другие параметры влияющие на загруженность памяти видеокарты и понизить их)

#можно не трогать:
whisper_model_name = "turbo"  # нет необходимости ставить large, так как точность у них крайне похожая, а время отличается в разы.
compute_type = "float16" # float32 дольше и требует больше мощности(видимо качество чуть лучше. но всё равно скорость решает).



start_time_transcription = time.time()
### Транскрибация.
# Загружаем основную модель
model = whisperx.load_model(whisper_arch=whisper_model_name, device=device, language=language_code, compute_type=compute_type)

# Делаем аудио одноканальным, приводим к нужным кГц
audio = whisperx.load_audio(audio_path)

# Транскрибация
#TODO: побаловаться с параметрами butch_size и тд.
transcription = model.transcribe(audio)
#print("\nТекст с таймкодами:", transcription["segments"])

execution_time_transcription = time.time() - start_time_transcription
print(f"END: Транскрибация : {execution_time_transcription:.4f} секунд")

# delete model if low on GPU resources
if(use_gc):
    gc.collect(); torch.cuda.empty_cache(); del model



start_time_align = time.time()
### Выравнивание по словам.
# Загружаем модель для выравнивания
align_model, metadata = whisperx.load_align_model(language_code=language_code, device=device)

# Выравниваем текст
aligned_transcription = whisperx.align(
    transcription["segments"], align_model, metadata, audio, device
)
#print("\nВыравненный текст:", aligned_transcription["segments"])

execution_time_align = time.time() - start_time_align
print(f"END: Выравнивание : {execution_time_align:.4f} секунд")

# delete model if low on GPU resources
if (use_gc):
    gc.collect(); torch.cuda.empty_cache(); del align_model



start_time_diarization = time.time()
### Диаризация.
# Загружаем модель для определения спикеров
diarize_model = whisperx.DiarizationPipeline(use_auth_token=HUGGINGFACE_TOKEN, device=device)

# Выполняем диаризацию (разделение на спикеров)
diarization = diarize_model(audio, min_speakers=min_speakers_count, max_speakers=max_speakers_count)

# Объединяем с транскрипцией
final_result = whisperx.assign_word_speakers(diarization, aligned_transcription)

execution_time_diarization = time.time() - start_time_diarization
print(f"END: Диаризация : {execution_time_diarization:.4f} секунд")

output_data = {
    "segments": final_result["segments"]
}

with open("TEXT_after_transcription/transcription_output.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=4)

print("Результаты сохранены в 'TEXT_after_transcription/transcription_output.json'")

# full_execution_time = time.time() - start_time_transcription
# print(f"Время выполнения с диаризацией: {full_execution_time:.4f} секунд")
# print(f"Время выполнения без диаризации: {execution_time_transcription:.4f} секунд")






# Сохранение результата в файл
# with open("transcription_output.txt", "w", encoding="utf-8") as f:
#     f.write("Текст с таймкодами:\n")
#     for segment in transcription["segments"]:
#         f.write(f"[{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['text']}\n")

#     f.write("\nВыравненный текст:\n")
#     for segment in aligned_transcription["segments"]:
#         f.write(f"[{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['text']}\n")
