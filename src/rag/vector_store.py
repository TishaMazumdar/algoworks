from typing import List, Optional, Dict, Any
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import os
import json

def split_documents(
    documents: List[Document],
    chunk_size: int = 1500,
    chunk_overlap: int = 500
) -> List[Document]:
    """
    Splits the input documents into smaller chunks for embedding.
    Preserves metadata across chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    split_docs = splitter.split_documents(documents)
    
    # Update chunk indices after splitting
    for i, doc in enumerate(split_docs):
        doc.metadata["chunk_index"] = i
        doc.metadata["total_chunks"] = len(split_docs)
    
    return split_docs

def build_vectorstore(documents: List[Document], persist_directory: str) -> Chroma:
    """
    Build vector store with enhanced metadata tracking.
    """
    # Ensure directory exists
    os.makedirs(persist_directory, exist_ok=True)
    
    # Split documents while preserving metadata
    split_docs = split_documents(documents)
    
    # Create embeddings
    embedding_model = OllamaEmbeddings(model="mistral")
    
    # Create vector store
    try:
        vectorstore = Chroma.from_documents(
            documents=split_docs,
            embedding=embedding_model,
            persist_directory=persist_directory
        )
        
        # Save file metadata for easier management
        save_file_metadata(persist_directory, documents)
        
        return vectorstore
        
    except Exception as e:
        print(f"Error building vectorstore: {e}")
        raise e

def add_documents_to_vectorstore(
    vectorstore: Chroma, 
    documents: List[Document]
) -> None:
    """
    Add new documents to existing vector store.
    """
    try:
        split_docs = split_documents(documents)
        vectorstore.add_documents(split_docs)
        
        # Update metadata file
        persist_directory = vectorstore._persist_directory
        save_file_metadata(persist_directory, documents, append=True)
        
    except Exception as e:
        print(f"Error adding documents to vectorstore: {e}")
        raise e

def delete_documents_by_file_id(
    persist_directory: str, 
    file_id: str
) -> tuple[bool, str]:
    """
    Delete all embeddings for a specific file using its file_id.
    Returns (success, filename) tuple.
    """
    try:
        vectorstore = load_vectorstore(persist_directory)
        
        # Get all documents with this file_id
        results = vectorstore.get(where={"file_id": file_id})
        
        if results and results['ids']:
            # Get filename from metadata before deleting
            filename = None
            if results['metadatas'] and len(results['metadatas']) > 0:
                filename = results['metadatas'][0].get('filename')
            
            # Delete documents by their IDs
            vectorstore.delete(ids=results['ids'])
            
            # Update metadata file
            remove_file_from_metadata(persist_directory, file_id)
            
            print(f"Deleted {len(results['ids'])} chunks for file_id: {file_id}")
            return True, filename
        else:
            print(f"No documents found for file_id: {file_id}")
            return False, None
            
    except Exception as e:
        print(f"Error deleting documents for file_id {file_id}: {e}")
        return False, None

def delete_documents_by_filename(
    persist_directory: str, 
    filename: str, 
    user_id: str
) -> bool:
    """
    Delete all embeddings for a specific filename and user.
    """
    try:
        vectorstore = load_vectorstore(persist_directory)
        
        # Get all documents with this filename and user_id
        results = vectorstore.get(where={
            "$and": [
                {"filename": filename},
                {"user_id": user_id}
            ]
        })
        
        if results and results['ids']:
            vectorstore.delete(ids=results['ids'])
            print(f"Deleted {len(results['ids'])} chunks for file: {filename}")
            return True
        else:
            print(f"No documents found for file: {filename}")
            return False
            
    except Exception as e:
        print(f"Error deleting documents for file {filename}: {e}")
        return False

def get_user_files(persist_directory: str, user_id: str) -> List[Dict[str, Any]]:
    """
    Get list of all files uploaded by a specific user.
    """
    try:
        vectorstore = load_vectorstore(persist_directory)
        
        # Get all documents for this user
        results = vectorstore.get(where={"user_id": user_id})
        
        if not results or not results['metadatas']:
            return []
        
        # Group by file_id to get unique files
        files_dict = {}
        for metadata in results['metadatas']:
            file_id = metadata.get('file_id')
            if file_id and file_id not in files_dict:
                files_dict[file_id] = {
                    'file_id': file_id,
                    'filename': metadata.get('filename'),
                    'file_type': metadata.get('file_type'),
                    'upload_timestamp': metadata.get('upload_timestamp'),
                    'chunk_count': 0
                }
            if file_id:
                files_dict[file_id]['chunk_count'] += 1
        
        return list(files_dict.values())
        
    except Exception as e:
        print(f"Error getting user files: {e}")
        return []

def save_file_metadata(persist_directory: str, documents: List[Document], append: bool = False):
    """
    Save file metadata to a JSON file for easier management.
    """
    metadata_file = os.path.join(persist_directory, "file_metadata.json")
    
    # Extract unique file metadata
    files_metadata = {}
    for doc in documents:
        file_id = doc.metadata.get('file_id')
        if file_id and file_id not in files_metadata:
            files_metadata[file_id] = {
                'file_id': file_id,
                'filename': doc.metadata.get('filename'),
                'file_path': doc.metadata.get('source'),
                'file_type': doc.metadata.get('file_type'),
                'user_id': doc.metadata.get('user_id'),
                'upload_timestamp': doc.metadata.get('upload_timestamp')
            }
    
    if append and os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            existing_data = json.load(f)
        existing_data.update(files_metadata)
        files_metadata = existing_data
    
    with open(metadata_file, 'w') as f:
        json.dump(files_metadata, f, indent=2)

def remove_file_from_metadata(persist_directory: str, file_id: str):
    """
    Remove file metadata from the JSON file.
    """
    metadata_file = os.path.join(persist_directory, "file_metadata.json")
    
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, 'r') as f:
                data = json.load(f)
            
            if file_id in data:
                filename = data[file_id].get('filename', 'Unknown')
                del data[file_id]
                
                with open(metadata_file, 'w') as f:
                    json.dump(data, f, indent=2)
                    
                print(f"✅ Removed {filename} from metadata file")
            else:
                print(f"⚠️ File ID {file_id} not found in metadata")
                
        except Exception as e:
            print(f"❌ Error updating metadata file: {e}")

def load_vectorstore(
    persist_directory: str = "embeddings/",
    model_name: str = "mistral"
) -> Chroma:
    """
    Loads an existing Chroma vector store from disk.
    """
    embedding_model = OllamaEmbeddings(model=model_name)
    return Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding_model
    )

def search_with_metadata_filter(
    persist_directory: str,
    query: str,
    file_types: Optional[List[str]] = None,
    user_id: Optional[str] = None,
    file_ids: Optional[List[str]] = None,
    k: int = 4
) -> List[Document]:
    """
    Search vector store with metadata filtering for faster, targeted retrieval.
    """
    vectorstore = load_vectorstore(persist_directory)
    
    # Build filter conditions
    filter_conditions = []
    
    if user_id:
        filter_conditions.append({"user_id": user_id})
    
    if file_types:
        filter_conditions.append({"file_type": {"$in": file_types}})
    
    if file_ids:
        filter_conditions.append({"file_id": {"$in": file_ids}})
    
    # Combine filters with AND
    where_filter = None
    if filter_conditions:
        if len(filter_conditions) == 1:
            where_filter = filter_conditions[0]
        else:
            where_filter = {"$and": filter_conditions}
    
    # Perform similarity search with filter
    return vectorstore.similarity_search(
        query=query,
        k=k,
        filter=where_filter
    )