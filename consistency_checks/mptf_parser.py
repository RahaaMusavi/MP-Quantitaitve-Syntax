# mptf_parser.py

import os
import pandas as pd
from tqdm.notebook import tqdm
from conllu import parse
from conllu.parser import DEFAULT_FIELD_PARSERS
from collections.abc import Mapping


# --- Class Definitions ---

class Token:
    """Represents a single token with support for all 10 CoNLL-U fields and parsed MISC."""
    def __init__(self, token_data):
        try:
            original_id = token_data.get('id')
            self.id = int(float(original_id)) if original_id is not None else None
        except (ValueError, TypeError):
            self.id = token_data.get('id')

        self.form = token_data.get('form')
        self.lemma = token_data.get('lemma')
        self.upos = token_data.get('upos')
        self.xpos = token_data.get('xpos')
        self.feats = token_data.get('feats')
        self.sense = token_data.get('sense')

        try:
            original_head = token_data.get('head')
            self.head = int(float(original_head)) if original_head is not None else None
        except (ValueError, TypeError):
            self.head = token_data.get('head')

        self.deprel = token_data.get('deprel')
        self.deps = token_data.get('deps')
        self.misc = token_data.get('misc')
        self.misc_dict = self._parse_misc(self.misc)

    def _parse_misc(self, misc_field):
        if not misc_field or misc_field == "_":
            return {}
        if isinstance(misc_field, Mapping):
            return dict(misc_field)  # Convert to plain dict just in case
        return dict(item.split("=", 1) for item in misc_field.split("|") if "=" in item)


class Sentence:
    def __init__(self, sentence_token_list, source_filename):
        self.metadata = sentence_token_list.metadata
        self.sentence_id = self.metadata.get('sent_id')
        self.file_name = source_filename
        self._tokens = [Token(t) for t in sentence_token_list]

    def get_tokens(self):
        return self._tokens

# --- Internal Helper Functions ---

def _sanitize_field(text):
    if text is None:
        return "_"
    s = str(text).replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
    return s.strip() if s.strip() else "_"

def _detect_misc_fields(df):
    """Returns list of non-CoNLL-U fields to store in MISC."""
    core_fields = {
        'id', 'transcription', 'lemma', 'postag', 'postfeatures',
        'head', 'deprel', 'deps', 'sense'
    }
    return [col for col in df.columns if col.lower() not in core_fields]

def _convert_csv_to_conllu(csv_file_path, output_dir):
    """Reads a single CSV/TSV/Excel file and converts it to CoNLL-U format."""
    try:
        ext = os.path.splitext(csv_file_path)[1].lower()
        if ext in ['.xlsx', '.xls']:
            df = pd.read_excel(csv_file_path, dtype=str, keep_default_na=False, engine='openpyxl')
        else:
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                sample = f.read(2048)
                sep = '\t' if sample.count('\t') >= sample.count(',') else ','
            df = pd.read_csv(csv_file_path, sep=sep, dtype=str, keep_default_na=False, encoding='utf-8', engine='python', on_bad_lines='skip')

        base_name = os.path.splitext(os.path.basename(csv_file_path))[0]
        output_file_path = os.path.join(output_dir, f"{base_name}.conllu")
        misc_fields = _detect_misc_fields(df)

        with open(output_file_path, 'w', encoding='utf-8') as f:
            current_sentence_tokens = []
            sentence_id_counter = 1

            for _, row in df.iterrows():
                id_val = str(row.get('id', '')).strip()
                lemma_val = str(row.get('lemma', '')).strip()
                is_sentence_boundary = (id_val in ['', '_']) and (lemma_val in ['', '_'])

                if is_sentence_boundary:
                    if current_sentence_tokens:
                        f.write(f"# sent_id = {sentence_id_counter}\n")
                        f.write("# text = " + " ".join(token[1] for token in current_sentence_tokens) + "\n")
                        for token_line in current_sentence_tokens:
                            f.write("\t".join(token_line) + "\n")
                        f.write("\n")
                        current_sentence_tokens = []
                        sentence_id_counter += 1
                else:
                    # Build base token line
                    conllu_token = [
                        _sanitize_field(row.get('id')),
                        _sanitize_field(row.get('transcription')),
                        _sanitize_field(row.get('lemma')),
                        _sanitize_field(row.get('postag')),
                        "_",  # XPOS
                        _sanitize_field(row.get('postfeatures')),
                        _sanitize_field(row.get('head')),
                        _sanitize_field(row.get('deprel')),
                        _sanitize_field(row.get('deps')),
                        "_"  # Placeholder for MISC
                    ]

                    # Build MISC string if metadata exists
                    misc_items = []
                    for field in misc_fields:
                        val = _sanitize_field(row.get(field))
                        if val != "_":
                            misc_items.append(f"{field}={val}")
                    conllu_token[9] = "|".join(misc_items) if misc_items else "_"

                    current_sentence_tokens.append(conllu_token)

            if current_sentence_tokens:
                f.write(f"# sent_id = {sentence_id_counter}\n")
                f.write("# text = " + " ".join(token[1] for token in current_sentence_tokens) + "\n")
                for token_line in current_sentence_tokens:
                    f.write("\t".join(token_line) + "\n")
                f.write("\n")
    except Exception as e:
        print(f"     - ERROR processing {os.path.basename(csv_file_path)}. Reason: {e}")

def _process_directory(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    files_to_process = [
        f for f in os.listdir(input_dir)
        if f.lower().endswith(('.csv', '.tsv', '.xlsx', '.xls')) and not f.startswith('~$')
    ]
    for filename in tqdm(files_to_process, desc="Converting source files"):
        file_path = os.path.join(input_dir, filename)
        _convert_csv_to_conllu(file_path, output_dir)
    print("\nSource file conversion complete!")

def _load_corpus_from_conllu(conllu_dir):
    custom_field_parsers = DEFAULT_FIELD_PARSERS.copy()
    custom_field_parsers['id'] = lambda line, i: line[i]
    custom_field_parsers['head'] = lambda line, i: line[i]

    all_corpus_sentences_list = []
    conllu_files = [f for f in os.listdir(conllu_dir) if f.lower().endswith('.conllu')]

    for filename in tqdm(conllu_files, desc="Loading and Parsing CoNLL-U files"):
        file_path = os.path.join(conllu_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read()

        lines = data.splitlines()
        clean_lines = [line for line in lines if line.startswith('#') or line.strip() == "" or line.count('\t') == 9]
        clean_data = "\n".join(clean_lines) + "\n"
        sentences = parse(clean_data, field_parsers=custom_field_parsers)

        for s in sentences:
            all_corpus_sentences_list.append(Sentence(s, filename))

    print(f"\nSuccessfully loaded {len(all_corpus_sentences_list)} sentences.")
    return all_corpus_sentences_list

# --- Public API Function ---

def parse_corpus(input_folder, output_folder):
    """
    Parses MPTF corpus files (.csv, .tsv, .xlsx, .xls) and returns list of Sentence objects.
    Automatically handles both basic and syntactically annotated files.
    """
    print("--- Starting Corpus Parsing Pipeline ---")
    print(f"Step 1: Converting files from '{input_folder}'")
    _process_directory(input_folder, output_folder)

    print(f"\nStep 2: Loading processed files from '{output_folder}'")
    corpus = _load_corpus_from_conllu(output_folder)

    print("\n--- Pipeline Complete ---")
    return corpus

# --- Corpus Wrapper Class ---

class Corpus:
    """
    Wrapper for parsing and storing the corpus as a list of Sentence objects.
    Usage:
        from mptf_parser import Corpus
        corpus = Corpus(input_dir, output_dir)
    """
    def __init__(self, input_dir, output_dir):
        self.sentences = parse_corpus(input_dir, output_dir)

    def get_sentences(self):
        return self.sentences

    def get_tokens(self):
        return [token for sentence in self.sentences for token in sentence.get_tokens()]
