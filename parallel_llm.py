import concurrent.futures
import time
from concurrent.futures import ThreadPoolExecutor
from question_format import Question
from utils import shuffle_choices
import google.generativeai as genai
from threading import Lock
import ffmpeg
import math
import os
import gc

lock = Lock()
def process_doc(doc, language_input, llm, shared_list):
    """Process the document and generate questions using the LLM model."""
    try:
        response = llm.invoke({"context": doc, "language": language_input})["result"]["questions"]
        response = shuffle_choices(response)
        for question in response:
            try:
                Question(**question)
                with lock:
                    shared_list.append(question)
            except Exception as e:
                print("One of the questions is not in required format.", e)
    except Exception as e:
        print("Error occurred while Testing Model questions.", e)


def parallel_process(data, data_name, language_input, llm, p_bar):
    """Process the document and generate questions using the LLM model in parallel."""
    shared_list = []

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_doc, doc, language_input, llm, shared_list) for doc in data]


        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            p_bar.progress(value=i / len(data), text=f"Questions Loading for Data: {data_name}: {i}/{len(data)}")
    return shared_list

############################################################################################################

def split_audio(audio, llm_s, start, split_duration, i, prompt, stt_list, split):
    """Split the audio and extract text from it using the LLM model."""
    output_path = f"audio_chunk_{i + 1}.mp3"
    if os.path.exists(output_path):
        os.remove(output_path)
        print(f"Removed existing audio chunk {i + 1}.")
    try:
        if split:
            (
                ffmpeg
                .input(audio, ss=start, t=split_duration)
                .output(output_path)
                .run()
            )
            gc.collect()
            print(f"Audio chunk {i + 1} created.")
            audio_file = genai.upload_file(path=output_path)
            print(f"Audio chunk {i + 1} uploaded.")
        else:
            audio_file = genai.upload_file(path=audio)
        try:
            print(f"Trying to send {i + 1} audio to flash.")
            response = llm_s["flash"].generate_content([audio_file, prompt])
            with lock:
                stt_list.append(str(response.text))
        except:
            print("Error occurred while sending audio to flash.")
            print("Trying to send audio to pro model.")
            response = llm_s["pro"].generate_content([audio_file, prompt])
            with lock:
                stt_list.append(str(response.text))
    except Exception as e:
        print(f"Error occurred while splitting audio: {e}")
        stt_list.append(" ")
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)

def split_audio_parallel(audio, llm_s, split_duration, loader_status, prompt):
    """Split the audio and extract text from it using the LLM model in parallel."""
    stt_list = []
    probe = ffmpeg.probe(audio)
    duration = float(probe['format']['duration'])
    num_chunks = math.ceil(duration / split_duration)

    if duration > split_duration:
        start_times = [i * split_duration for i in range(num_chunks)]
        loader_status.info(f"🔪 Splitting audio into {num_chunks} chunks.")
        time.sleep(1)
        loader_status.info("🙏 Please wait while the audio is being split.")
        split = True
    else:
        split = False
        start_times = [0]

    loader_status.info(f"🔊 Extracting text from audio. Started processing {num_chunks} chunks.")
    with ThreadPoolExecutor(max_workers=2) as executor: # 2 workers to avoid overloading the live streamlit, otherwise it will crash
        futures = [executor.submit(split_audio, audio, llm_s, start, split_duration, i, prompt, stt_list, split) for i, start in enumerate(start_times)]

        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            loader_status.progress(value=i / num_chunks, text=f"🔊 Extracting text from audio: {i}/{num_chunks}")

    return stt_list