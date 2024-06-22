import argparse
import os
import shutil
import zipfile
import PyPDF2
from langchain_community.document_loaders import PyPDFDirectoryLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from embedding_func import get_embedding_function
from langchain_community.vectorstores import Chroma
import gdown

CHROMA_PATH = "./chroma"
DATA_PATH = "./data/mds"
PDF_PATH = "./data/pdfs"

def main():

    # Check if the database should be cleared (using the --clear flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("✨ Clearing Database")
        clear_database()

    get_data()
    unzip_file()
    convert_pdfs_in_directory('./data/pdfs/')

    # Create (or update) the data store.
    documents = load_documents()
    print(f'{len(documents)} documents created.')

    chunks = split_documents(documents)
    print(f'Split {len(documents)} documents into {len(chunks)} chunks.')
    add_to_chroma(chunks)

def get_data():
    print(f'👉 Download zip file.')

    # Create the subfolder if it doesn't exist
    os.makedirs('./data', exist_ok=True)

    # Extract the file ID from the Google Drive link
    file_id = '1wisPh0Dq87zD1M4-QTbbdIDAZBhmbozC'
    
    # Create the URL for gdown to download the file
    download_url = f'https://drive.google.com/uc?id={file_id}'
    
    # Download the file
    gdown.download(download_url, './data/pdfs.zip', quiet=False)
    print(f'Downloaded file to ./data/pdfs.zip')

def unzip_file(zip_path = './data/pdfs.zip'):
    # Extract the base name of the zip file without the extension
    folder_name = os.path.splitext(os.path.basename(zip_path))[0]
    
    # Create a path for the new subfolder
    subfolder_path = os.path.dirname(zip_path)
    
    # Create the subfolder if it doesn't exist
    os.makedirs(subfolder_path, exist_ok=True)
    
    # Unzip the contents into the subfolder
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(subfolder_path)
    
    # Path to the __MACOSX folder
    macosx_path = os.path.join(subfolder_path, '__MACOSX')
    
    # Remove the __MACOSX folder if it exists
    if os.path.exists(macosx_path):
        shutil.rmtree(macosx_path)
    
    print(f'👉 Unzipped {zip_path}')
    if os.path.exists(macosx_path):
        print(f'Removed __MACOSX folder')

def pdf_to_md(pdf_file, md_file):
    with open(pdf_file, 'rb') as f:
        pdf_reader = PyPDF2.PdfReader(f)
        with open(md_file, 'w', encoding='utf-8') as md:
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                # Write page content to Markdown file
                md.write(text + '\n\n')

def convert_pdfs_in_directory(directory):
    print(f"👉 Converting PDFs to Markdown files.")
    os.makedirs(DATA_PATH, exist_ok=True)

    for filename in os.listdir(directory):
        if filename.endswith('.pdf'):
            pdf_file = os.path.join(directory, filename)
            md_file = os.path.join('./data/mds/', f'{os.path.splitext(filename)[0]}.md')
            pdf_to_md(pdf_file, md_file)

def load_documents():
    # document_loader = PyPDFDirectoryLoader(DATA_PATH)
    document_loader = DirectoryLoader(DATA_PATH, glob = "*.md")

    return document_loader.load()

def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=500,
        length_function=len,
        add_start_index = True,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

def add_to_chroma(chunks):
    # Load the existing database.
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    )

    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        db.persist()
    else:
        print("✅ No new documents to add")


def calculate_chunk_ids(chunks):

    # This will create IDs like "data/monopoly.pdf:6:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks


def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)


if __name__ == "__main__":
    main()