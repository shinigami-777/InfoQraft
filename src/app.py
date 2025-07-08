import streamlit as st
from utils import check_file_type
import uuid
from graph import LLMs
from question_format import TestModel
from all_loaders import Loaders
import tempfile
import os
import base64

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img_base64 = get_base64_image("media/bkg.jpeg")

# injecting the background image after converting it to base 64
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    .block-container {{
        background-color: rgba(79, 186, 232, 0.50);
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }}
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="InfoQraft", page_icon="👓")

os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

# Step 1: Data Entry Card
st.title("InfoQraft: Test your preparation.")
tab1, tab2, tab3 = st.tabs(["Data Entry", "Question Generation", "Question Review"])

data_types_dict = {"pdf":"pdf","mp3":"audio","wav":"audio","enex":"enex","mp4":"mp4","docx":"docx","png":"image","jpg":"image","pptx":"pptx","epub":"epub","txt":"txt"}

if "data" not in st.session_state:
    st.session_state.data = {}
    st.session_state.key_id = uuid.uuid4()
    st.session_state.question_list = []

if 'question_index' not in st.session_state:
    st.session_state.question_index = 0
    st.session_state.correct_count = 0
    st.session_state.show_questions = False

def show_question():
    """Shows the active question and checks the answer."""
    question = st.session_state.question_list[st.session_state.question_index]
    st.write(f"Question {st.session_state.question_index + 1}: {question['question']}")

    # Getting a response from the user
    choice = st.radio("Options:", question['choices'])

    # Check the answer
    if st.button("Submit"):
        if choice is not None:
            # Correct answer check
            selected_answer_index = question['choices'].index(choice)
            if question['answers'][selected_answer_index]:
                st.success("Correct!")
                st.session_state.correct_count += 1
            else:
                st.error("Wrong :(")
            st.write("Explaination:", question['explain'])

def next_question():
    st.session_state.question_index += 1

def take_again():
    st.session_state.question_index = 0
    st.session_state.correct_count = 0

def show_results():
    with tab3:
        st.write(f"Total number of questions: {len(st.session_state.question_list)}")
        st.write(f"Number of correct answers: {st.session_state.correct_count}")

def clean_components():
    st.session_state.key_id = uuid.uuid4()

def define_llm(data, data_type):
    loader = Loaders(data)
    data = loader.set_loaders(data_type)
    llm = LLMs()
    p_bar = st.progress(0)
    len_data = len(data[:4])
    for i, doc in enumerate(data[:4],1):
        p_bar.progress(i/len_data)
        try:
            # We run the model and get the answer
            response = llm.question_maker({"context": doc, "language": "English"})
            TestModel(**response)
            st.session_state.question_list.append(response)
        except:
            pass
    st.session_state.question_list = [question for questions in st.session_state.question_list for question in questions["test"]["questions"]]

def load_components(key_id):
    file_upload.file_uploader("Upload File", type=["pdf","txt","mp3","wav","enex","mp4","docx","png","jpg","pptx","epub"],
                                     accept_multiple_files=True, key=str(key_id)+"files")
    url_upload.text_input("URL",
                               placeholder="https://xyz.com", key=str(key_id)+"url")
    youtube_upload.text_input("Youtube URL", placeholder="https://www.youtube.com/watch?v=rickroll", key=str(key_id)+"youtube")
    wikipedia_search.text_input("Wikipedia Search", placeholder="World War II", key=str(key_id)+"wiki")
    text_input.text_area("Direct Text Input", placeholder="AI can do blah blah blah.", key=str(key_id)+"text")
with tab1:
    st.subheader("Enter Data")
    file_upload = st.empty()
    url_upload = st.empty()
    youtube_upload = st.empty()
    wikipedia_search = st.empty()
    text_input = st.empty()
    col1, col2 = st.columns(2)
    with col1:
        st.button("Clean Form", use_container_width=True, type="secondary", on_click=clean_components)
    with col2:
        submit_data = st.button("Load Data", use_container_width=True, type="primary")
    st.write(st.session_state.key_id)
    load_components(st.session_state.key_id)


    if submit_data:
        uploads = st.session_state.get(str(st.session_state.key_id) + "files")
        if uploads:
            st.session_state.data["files"] = uploads
            for file in uploads:
                if not check_file_type(file):
                    st.error("Invalid file type, or manipulated extension. Please upload a valid file.")
                    break
                else:
                    data_extension = file.name.split('.')[-1].lower()
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{data_extension}") as temp_file:
                        temp_file.write(file.getvalue())
                        temp_file.flush()
                        temp_file_path = temp_file.name

                    data_type = data_types_dict[data_extension]
                    define_llm(temp_file_path, data_type)

        if url_upload:
            st.session_state.data["url"] = st.session_state.get(str(st.session_state.key_id) + "url")
        if youtube_upload:
            st.session_state.data["youtube"] = st.session_state.get(str(st.session_state.key_id) + "youtube")
        if wikipedia_search:
            st.session_state.data["wiki"] = st.session_state.get(str(st.session_state.key_id) + "wiki")
        if text_input:
            st.session_state.data["text"] = st.session_state.get(str(st.session_state.key_id) + "text")

        st.session_state.show_questions = True
p_bar = st.empty()
with tab2:
    if st.session_state.show_questions & (st.session_state.question_index + 1 <= len(st.session_state.question_list)):
        show_question()
    if st.session_state.question_index + 1 <= len(st.session_state.question_list):
        st.button("Next Question", on_click=next_question)
    else:
        st.write("Congratulations You Have Completed The Test !!")
        col3, col4 = st.columns(2)
        with col3:
            st.button("Retake Test", on_click=take_again, use_container_width=True)
        with col4:
            st.button("Show Results", on_click=show_results, use_container_width=True)