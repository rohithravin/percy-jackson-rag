# Building a RAG + LLM using Percy Jackson Books

## Background
Recent advancements in artificial intelligence, particularly in language models and retrieval-augmented generation (RAG), have opened new avenues for creating sophisticated applications. This project aims to leverage these technologies to create a powerful question-answering system using the world of Percy Jackson books. The system will use LangChain for orchestration, a Vector Database (Vector DB) for embeddings and retrieval, and the Ollama API with Llama3 for language modeling. Additionally, we will compare the performance and quality of responses and embeddings using two different retrieval mechanisms: ElasticSearch and a Vector Database.

## Objectives
- Create a RAG + LLM system that can answer questions based on the content of Percy Jackson books.

- Implement and integrate LangChain, Vector DB, and Ollama (using Llama3).


## Installation and Setup
First, we need to install Ollama. Ollama is an open-source project that serves as a powerful and user-friendly platform for running LLMs on your local machine. Download and install the application via the link [here](https://ollama.com/download). Once Ollama is installed (including the ollama cli, which is part of the installation stesp), in the terminal run the following commands.

```bash
ollama pull llama3
ollama pull nomic-embed-text
ollama serve
```

These set of commands will download the models we need to run our RAG and to start the ollama server.


## Setting up RAG
Second, in a separete terminal, we create a conda enviroment and install the required dependencies.
```bash
conda create --name percyjacksonrag python=3.8
conda activate percyjacksonrag
pip install -r requirements.txt
```

We then run `populate_db.py`. This script will download the Percy Jackson books and populate them into our Chroma vector db by using embeddings dervied from `nomic-embed-text`. This will take a while.

```bash
python populate_db.py --reset
```

Once this is done, everything it set up to run our RAG and ask our LLM questions about the world of Percy Jackson! All you have to do is run:

```bash
python app.py
```

Below is a demo video! 

[![Demo Video](https://img.youtube.com/vi/d46U_W_QdF4/0.jpg)](https://www.youtube.com/watch?v=d46U_W_QdF4)