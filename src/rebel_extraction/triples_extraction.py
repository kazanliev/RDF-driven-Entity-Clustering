from transformers import pipeline
import os
import glob
from src.classes.rdf_graph import RDFGraph

# Initialize the transformers triple extraction pipeline
triplet_extractor = pipeline('text2text-generation', model='Babelscape/rebel-large', tokenizer='Babelscape/rebel-large')

def extract_triplets(text):
    """
    Extract relational triples from a text chunk using the REBEL model.
    Source: https://huggingface.co/Babelscape/rebel-large
    """
    triplets = []
    relation, subject, relation, object_ = '', '', '', ''
    text = text.strip()
    current = 'x'
    for token in text.replace("<s>", "").replace("<pad>", "").replace("</s>", "").split():
        if token == "<triplet>":
            current = 't'
            if relation != '':
                triplets.append({'head': subject.strip(), 'type': relation.strip(),'tail': object_.strip()})
                relation = ''
            subject = ''
        elif token == "<subj>":
            current = 's'
            if relation != '':
                triplets.append({'head': subject.strip(), 'type': relation.strip(),'tail': object_.strip()})
            object_ = ''
        elif token == "<obj>":
            current = 'o'
            relation = ''
        else:
            if current == 't':
                subject += ' ' + token
            elif current == 's':
                object_ += ' ' + token
            elif current == 'o':
                relation += ' ' + token
    if subject != '' and relation != '' and object_ != '':
        triplets.append({'head': subject.strip(), 'type': relation.strip(),'tail': object_.strip()})
    return triplets


def process_triples_extraction_REBEL(text_chunks_file_base, output_file, base_name):
    """
    Exctract triples from every text chunk in the specified input folder.

    Args:
        text_chunks_file_base (str): input folder containing the input text in chunks
    """

    #Save a list with sorted file paths from the folder
    input_files = sorted(
        glob.glob(
            os.path.join(text_chunks_file_base, f'{base_name}_chunk_*.txt')
        ), 
        key=lambda name: int(name.split('_')[-1].split('.')[0])
    )

    total_number_of_chunks = len(input_files)
    
    # initialize an RDF graph to store the triples
    g = RDFGraph()

    num_chunk = 0
    for file_path in input_files:
        with open(file_path, 'r', encoding='utf-8') as file:
            input_text = file.read()

        # Some of the text chunks may exceed the token limit. We decided to not break the pipeline when this happens (but let the user know).
        try:
            # Tokenizer must be used manually (https://huggingface.co/Babelscape/rebel-large)
            extracted_text = triplet_extractor.tokenizer.batch_decode([triplet_extractor(input_text, return_tensors=True, return_text=False)[0]["generated_token_ids"]])
            triplets = extract_triplets(extracted_text[0])
            g.add_multiple_triples((triple['head'], triple['type'], triple['tail']) for triple in triplets)
            num_chunk+=1
            print(f"[INFO] Text chunk {num_chunk}/{total_number_of_chunks} processed.")
        except Exception as e:
            num_chunk+=1
            print(f"[ERROR] Text chunk {num_chunk}/{total_number_of_chunks} (try decreasing the max. num sentences per text chunk): {e}")
            continue
    # save the extracted triples
    g.save_to_turtle(output_file)
    print(f"[INFO] Extracted triples from '{text_chunks_file_base}' and saved in '{output_file}'.")

        
    
    