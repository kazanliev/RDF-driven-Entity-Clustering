from nltk.tokenize import word_tokenize, sent_tokenize


def count_words_and_sentences(filename):
    """
    Return number of words and sentences in the specified file
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            text = file.read()

        words = word_tokenize(text)
        sentences = sent_tokenize(text)

        word_count = len(words)
        sentence_count = len(sentences)

        return word_count, sentence_count

    except FileNotFoundError:
        print(f"Error: The file {filename} does not exist.")
        return None
    
def count_lines_in_ttl(file_path):
    """
    Counts all lines in a tutrtle file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            line_count = sum(1 for line in file)
        return line_count
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
        return None
    
def save_statistics(input_file, rebel_triples, dbpedia_triples, combined_triples, combined_entities, scores, output_file):
    """
    After running the pipeline, extract a summary containing: number of triples (DBpedia, REBEL and combined),
    number of entities. Also, scores and number of clusters produced by every combination of similarity measure,
    linkage method and clustering score.

    Args:
        input_file (str): input text file for the pipeline (the source text)
        rebel_triples (str): path to the triples extracted with REBEL
        dbpedia_triples (str): path to the DBpedia triples
        combined_triples (str): path to the file containing both DBpedia and REBEL triples
        combined_entities (str): path to the file containing all extracted triples
        scores (dict): the Silhouette scores and number of corresponding clusters for each best rated clustering
        output_file (str): file destination for saving the info.
    """
    
    # Count words and sentences in the input file
    word_count, sentence_count = count_words_and_sentences(input_file)

    # Count lines (used for determining count of triples and entities)
    rebel_triples_count = count_lines_in_ttl(rebel_triples)
    dbpedia_triples_count = count_lines_in_ttl(dbpedia_triples)
    combined_triples_count = count_lines_in_ttl(combined_triples) 
    dbpedia_entities_count = count_lines_in_ttl(combined_entities) - 1

    # Content
    content = [
        f"Number of words in the input file: {word_count}",
        f"Number of sentences in the input file: {sentence_count}",
        f"Number of REBEL triples: {rebel_triples_count}",
        f"Number of DBpedia triples: {dbpedia_triples_count}",
        f"Number of combined triples: {combined_triples_count}",
        f"Number of DBpedia entities (w/o REBEL): {dbpedia_entities_count}",
    ]

    # Determine and save also the best rated linkage method (best rated clustering) for each similarity measure
    # by choosing the clustering (linkage) method which generated the max silhouette coefficient score
    for measure, methods in scores.items():
        max_score = float('-inf')
        best_params = None

        for method, coeffs in methods.items():
            for coeff, result in coeffs.items():
                content.append(f"Results for {measure}, {method}, {coeff}: Clusters - {result['num_clusters']}, Score - {result['score']}")
                if result['score'] > max_score:
                    max_score = result['score']
                    best_params = f"Best score for {measure}: {method}, {coeff}: Clusters - {result['num_clusters']}, Score - {max_score}"
        if best_params:
            content.append(best_params)

    # Save
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(content) + "\n")
    print(f"[INFO] Statistics for the input file {input_file} saved successfully to {output_file}.")
