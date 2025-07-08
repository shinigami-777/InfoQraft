# 📚 InfoQraft: Multimodal Q/A Generator with LLMs

InfoQraft is a **Streamlit-based, multimodal AI system** that automatically extracts content from various media types (PDF, DOCX, PPTX, MP3, MP4, images, URLs, etc.) and generates **intelligent questions and answers** using **large language models**. It also supports evaluation and feedback, making it useful for ed-tech, content review, and AI education tools.

### 🚀 Features

- 🧠 **LLM-Powered Question Generation** (Model- gemini-1.5-flash)
- 📄 **Multi-format Input Support**: PDF, DOCX, PPTX, EPUB, TXT, ENEX, MP3, MP4, images, URLs, and more
- ✨ **Beautiful, customizable Streamlit UI**
- 📊 **Evaluation mode** with feedback present
- 📂 Upload or paste content directly

 ### 🛠️ **Technologies Used**
- **LangChain, LangGraph, LangChain-Core, LangChain-Google-GenAI, LangChain-Community, LangChain-Text-Splitters**: For processing natural language and managing multimodal input data.
- **Pydantic**: To structure data and ensure model consistency.
- **Streamlit**: Builds the user interface, providing an interactive environment for answering questions.
- **PDF & Document Processing**: Libraries such as `pypdf`, `python-pptx`, `docx2txt`, and `unstructured[pdf]` handle various document formats.
- **Video & Audio Processing**: `moviepy`, `youtube-transcript-api`, and `yt_dlp` assist in processing multimedia content.

### 📦 Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/shinigami-777/InfoQraft.git
   ```
2. Navigate into the project directory:
   ```bash
   cd InfoQraft
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your own Gemini API key. Inside [secrets.toml](https://github.com/shinigami-777/InfoQraft/blob/main/src/.streamlit/secrets.toml) put:
    ```bash
    GOOGLE_API_KEY= "yourrealAPIKey"
    ```
5. Run the Streamlit application:
    ```bash
    streamlit run src/app.py
    ```

Navigate to http://localhost:8501/ to use the app.
### 🖼️ App UI Preview
> Generate your quiz
![look](https://github.com/shinigami-777/InfoQraft/blob/main/media/UIlook.png)

> Attend the questions
![questions](https://github.com/shinigami-777/InfoQraft/blob/main/media/questionslook.png)

> Get feedback and retake to get better
![retake](https://github.com/shinigami-777/InfoQraft/blob/main/media/retaketest.png)
