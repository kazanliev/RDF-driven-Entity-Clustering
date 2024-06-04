import os
import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
from nltk.tokenize import sent_tokenize


def chunk_text_file(input_file_path, output_file_base, max_sentences_per_chunk=15, sentence_overlap_size=1):
    """
    Helper function to prepare the text for triple extraction with REBEL. Text chunking is necessary to token limit exceedance.

    Args:
        input_file_path (str): input text file
        output_file_base (str): destination folder for the text chunks
        max_sentences_per_chunk (int, optional): lower max number of sentences would save memory and also 
        prevent exceeding the token limit. The default value of 15 works almost all of the time.
        sentence_overlap_size (int, optional): useful for better coreference 
        resolution 
    """
    
    #we use base_name for naming the chunks
    base_name = os.path.splitext(os.path.basename(input_file_path))[0]
    if not os.path.exists(output_file_base):
        os.makedirs(output_file_base)
    with open(input_file_path, 'r', encoding='utf8') as file:
        text = file.read()
    
    #Extract sentences and determine the number of text chunks 
    sentences = sent_tokenize(text)
    total_sentences = len(sentences)
    number_of_chunks = (total_sentences + max_sentences_per_chunk - 1 - sentence_overlap_size) // (max_sentences_per_chunk - sentence_overlap_size)

    # Process and save each chunk
    for i in range(number_of_chunks):
        start_idx = i * (max_sentences_per_chunk - sentence_overlap_size)
        end_idx = min(start_idx + max_sentences_per_chunk, total_sentences)
        chunk_sentences = sentences[start_idx:end_idx]
        chunk_text = ' '.join(chunk_sentences)
        output_file_path = os.path.join(output_file_base, f"{base_name}_chunk_{i + 1}.txt")
        with open(output_file_path, 'w', encoding='utf8') as output_file:
            output_file.write(chunk_text)

    print(f"[INFO] Processed {number_of_chunks} chunks from '{input_file_path}' and saved in '{output_file_base}'.")

