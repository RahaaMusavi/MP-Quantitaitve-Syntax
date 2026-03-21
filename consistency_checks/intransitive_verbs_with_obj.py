def find_intransitive_sentences_with_newpart(sentences: List[Sentence]) -> List[Sentence]:
    """
    Find sentences that have the metadata 'newpart', 
    contain an intransitive verb (Subcat 'Intr'), and have at least one object as a dependent.
    """
    filtered_sentences = []  # List to store the filtered sentences

    for sentence in sentences:
        # Check if the sentence metadata has 'newpart'
        if 'newpart' in sentence.metadata:
            for token in sentence.get_tokens():
                # Check if token is a verb and has Subcat 'Intr'
                if token.upos == 'VERB' and token.feats.get('Subcat') == 'Intr':
                    # Now check if any of its dependents are objects
                    has_object_dependent = any(
                        dep_token.deprel in {'obj', 'ccomp'} and dep_token.head == token.id
                        for dep_token in sentence.get_tokens()
                    )

                    # If we found an object dependent, add the sentence to the results
                    if has_object_dependent:
                        tup = (token.lemma, sentence.metadata)
                        filtered_sentences.append(tup)
                        break  # No need to check other tokens, move to the next sentence

    return filtered_sentences

# Get all unique sentences with Newpart, Intr verbs, and objects
filtered_sentences = find_intransitive_sentences_with_newpart(sentences)

# Print the resulting sentences
for tup in filtered_sentences:
    lemma = tup[0]  # token.lemma
    newpart = tup[1].get('newpart', 'N/A')  # sentence.metadata['newpart'], defaulting to 'N/A' if missing
    sentence_text =tup[1].get ('text', 'N/A')
    sentence_id =tup[1].get ('sent_id', 'N/A')
    print(f"Lemma: {lemma}, Newpart: {newpart}, sentence_id: {sentence_id}, Sentence: {sentence_text}")
