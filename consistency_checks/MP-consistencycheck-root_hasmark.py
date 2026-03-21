'''consistancy check to find the roots that have a child with the deprel mark'''

import os
import traceback
import csv
from collections import defaultdict, Counter
from conllu import parse_incr

class Token:
    def __init__(self, id_, form, lemma, upos, xpos, feats, head, deprel, deps, misc):
        self.id = id_
        self.form = form
        self.lemma = lemma
        self.upos = upos
        self.xpos = xpos
        self.feats = feats if feats is not None else {}  # feats is always a dictionary
        self.head = head
        self.deprel = deprel
        self.deps = deps
        self.misc = misc

    def __str__(self):
        return (f"Token(id={self.id}, form={self.form}, lemma={self.lemma}, "
                f"upos={self.upos}, xpos={self.xpos}, feats={self.feats}, "
                f"head={self.head}, deprel={self.deprel}, deps={self.deps}, "
                f"misc={self.misc})")

class Sentence:
    def __init__(self, sentence_id, tokens, metadata=None):
        self.sentence_id = sentence_id  # Unique ID for each sentence
        self.tokens = tokens  # List of Token objects
        self.metadata = metadata if metadata else {}  # Metadata includes sentence id, sentence text, translations, newpart

    def __str__(self):
        token_strs = ', '.join([str(token) for token in self.tokens])
        return f"Sentence(id={self.sentence_id}, tokens=[{token_strs}], metadata={self.metadata})"

    def get_tokens(self):
        return self.tokens

    def get_metadata(self):
        return self.metadata

def convert_tuple_id_to_float(id_tuple):
    """
    Convert a tuple (integer_before_point, decimal_position, integer_after_point)
    to a float number.
    """
    if isinstance(id_tuple, tuple) and len(id_tuple) == 3:
        integer_part = id_tuple[0]
        decimal_part = id_tuple[2]
        id_num = f"{integer_part}.{decimal_part}"  # Create float number as string
        return float(id_num)
    return float(id_tuple)  # In case it's already a float or int

def process_conllu_file(file_path):
    sentences = []  # List to store all Sentence objects
    try:
        with open(file_path, 'r', encoding='utf-8') as data_file:
            for idx, sentence in enumerate(parse_incr(data_file), 1):
                tokens_list = []
                metadata = sentence.metadata  # Extract metadata

                # Process each token in the sentence
                for token_data in sentence:
                    token_id = token_data['id']
                    if isinstance(token_id, tuple):
                        token_id = convert_tuple_id_to_float(token_id)

                    token = Token(
                        id_=token_id,
                        form=token_data['form'],
                        lemma=token_data['lemma'],
                        upos=token_data['upos'],
                        xpos=token_data['xpos'],
                        feats=token_data.get('feats', {}),
                        head=token_data['head'],
                        deprel=token_data['deprel'],
                        deps=token_data['deps'],
                        misc=token_data['misc']
                    )
                    tokens_list.append(token)

                # Create Sentence object with its tokens and metadata
                sentence_obj = Sentence(sentence_id=idx, tokens=tokens_list, metadata=metadata)
                sentences.append(sentence_obj)
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        traceback.print_exc()

    return sentences

def process_folder(folder_path):
    all_sentences = []  # List to store all sentences across multiple files
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".conllu"):
                file_path = os.path.join(root, file)
                sentences = process_conllu_file(file_path)
                all_sentences.extend(sentences)
    return all_sentences

def load_sentences_from_folder(folder_path):
    """
    This function processes all .conllu files in a folder and returns:
    - A list of all Sentence objects
    - A flat list of all Token objects
    """
    sentences = process_folder(folder_path)
    all_tokens = [token for sentence in sentences for token in sentence.get_tokens()]  # Flatten all tokens from all sentences
    return sentences, all_tokens


def print_mark_dependents_of_roots_in_all_sentences(sentences):
    """
    Prints the forms of the tokens that are dependents of the root and have the deprel 'mark'
    for all sentences and their respective roots. Also prints the 'newpart' attribute (metadata)
    of the sentence if it exists.
    
    Parameters:
    - sentences: A list of Sentence objects
    """
    for sentence in sentences:
        # Find the root token (token with deprel='root')
        root_token = next((token for token in sentence.get_tokens() if token.deprel == 'root'), None)
        
        if root_token:
            # Collect the forms of the dependents of the root with deprel='mark'
            mark_dependents = [
                token.form for token in sentence.get_tokens()
                if token.head == root_token.id and token.deprel == 'mark'
            ]
            
            # Collect the "new part" from the sentence metadata (assuming 'newpart' key exists in metadata)
            new_part = sentence.get_metadata().get('newpart', 'No newpart attribute')  # Safe access to 'newpart'
            sent_id =sentence.get_metadata().get('sent_id', 'No id attribute')
            # Print the forms of the mark dependents and the new part (metadata)
            if mark_dependents:
                print(f"Sentence with root token ID {root_token.id} ('{root_token.form}'), mark dependent: {mark_dependents}, sent id: {sent_id}, newpar {new_part}")

def main_with_sequence_analysis():
    # Load sentences from folder
    folder_path = 'C:\\Users\\rahaa\\Dropbox\\MPCD\\conllu'
    sentences, tokens = load_sentences_from_folder(folder_path)

    # Print the forms of the dependents of the root with deprel='mark' for all sentences
    print_mark_dependents_of_roots_in_all_sentences(sentences)

    print(f"\nTotal sentences found: {len(sentences)}")
    print(f"Total tokens found: {len(tokens)}")

if __name__ == "__main__":
    main_with_sequence_analysis()
