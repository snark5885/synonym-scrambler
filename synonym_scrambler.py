import random
import argparse
import spacy
import nltk
nltk.download('wordnet', quiet=True)
from nltk.corpus import wordnet
import inflect
from wordfreq import word_frequency

# Load spaCy English model
nlp = spacy.load('en_core_web_sm')

from wordfreq import word_frequency

def scrambled_text(text, replacement_rate=1):
    """Scramble text by replacing nouns, verbs, adjectives, and adverbs with contextually similar words."""
    doc = nlp(text)
    replaceable_words = [
        token for token in doc 
        if token.pos_ in ['NOUN', 'VERB', 'ADJ', 'ADV'] and len(token.text) > 2
    ]
    
    num_replacements = max(1, int(len(replaceable_words) * replacement_rate))
    words_to_replace = random.sample(replaceable_words, num_replacements)
    
    replacements = {}
    
    for token in words_to_replace:
        synonyms = find_contextual_synonyms(token)
        context_filtered_synonyms = []
        
        for synonym in synonyms:
            try:
                syn_token = nlp(synonym)[0]
                
                # Check morphological compatibility
                if not match_morphology(token, syn_token):
                    continue
                
                # Apply additional filtering
                if (not syn_token.has_vector or 
                    len(synonym) > 15 or 
                    not synonym.isalpha() or
                    word_frequency(synonym, 'en') < 1e-6):
                    continue
                
                similarity = token.similarity(syn_token)
                if similarity > 0.3:
                    context_filtered_synonyms.append((synonym, similarity))
            except:
                continue
        
        if context_filtered_synonyms:
            best_synonym = sorted(context_filtered_synonyms, key=lambda x: x[1], reverse=True)[0][0]
            
            # Try to match original word's form (e.g., pluralization)
            if token.pos_ == 'NOUN':
                singular = p.singular_noun(token.text)
                if singular:  # token is plural
                    best_synonym = p.plural(best_synonym)
            
            # Store the replacement
            replacements[token.text] = best_synonym
    
    # Create the output text by replacing words
    output_tokens = []
    for token in doc:
        if token.text in replacements:
            output_tokens.append(replacements[token.text])
        else:
            output_tokens.append(token.text)
    
    return ' '.join(output_tokens)



def find_contextual_synonyms(token):
    """Find synonyms using WordNet, filtered by part of speech."""
    pos_map = {
        'NOUN': wordnet.NOUN,
        'VERB': wordnet.VERB,
        'ADJ': wordnet.ADJ,
        'ADV': wordnet.ADV
    }
    
    wordnet_pos = pos_map.get(token.pos_, None)
    if wordnet_pos is None:
        return []
    
    synsets = wordnet.synsets(token.text, pos=wordnet_pos)
    
    synonyms = []
    for synset in synsets:
        for lemma in synset.lemmas():
            synonym = lemma.name().replace('_', ' ')
            if synonym.lower() != token.text.lower() and synonym not in synonyms:
                synonyms.append(synonym)
    
    return synonyms[:5]

p = inflect.engine()

def match_morphology(original_token, synonym_token):
    """
    Check if a synonym matches the morphological features of the original token.
    """
    # Compare number (singular/plural)
    orig_number = original_token.morph.get("Number")
    syn_number = synonym_token.morph.get("Number")
    if orig_number and syn_number and orig_number != syn_number:
        return False
    
    # Compare verb form and tense
    orig_tense = original_token.morph.get("Tense")
    orig_verbform = original_token.morph.get("VerbForm")
    syn_tense = synonym_token.morph.get("Tense")
    syn_verbform = synonym_token.morph.get("VerbForm")
    
    if orig_tense and syn_tense and orig_tense != syn_tense:
        return False
    
    if orig_verbform and syn_verbform and orig_verbform != syn_verbform:
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Scramble text by replacing words with synonyms.')
    parser.add_argument('input_file', type=str, help='Path to the input text file')
    parser.add_argument('--output', '-o', type=str, help='Path to the output text file (optional)')
    parser.add_argument('--rate', '-r', type=float, default=1, help='Replacement rate (default: 1)')
    
    args = parser.parse_args()
    
    # Read input text
    try:
        with open(args.input_file, 'r', encoding='utf-8') as file:
            input_text = file.read()
    except FileNotFoundError:
        print(f"Error: File {args.input_file} not found.")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Scramble the text
    scrambled_text_result = scrambled_text(input_text, replacement_rate=args.rate)
    
    # Output handling
    if args.output:
        # Write to output file
        try:
            with open(args.output, 'w', encoding='utf-8') as file:
                file.write(scrambled_text_result)
            print(f"Scrambled text written to {args.output}")
        except Exception as e:
            print(f"Error writing output file: {e}")
    else:
        # Print to console
        print("Scrambled Text:")
        print(scrambled_text_result)

if __name__ == '__main__':
    main()
