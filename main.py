import pickle
import nltk

with open("vocab", "rb") as f:
    vocab = pickle.load(f)

LOWERCASE = [chr(x) for x in range(ord('a'), ord('z') + 1)]
UPPERCASE = [chr(x) for x in range(ord('A'), ord('Z') + 1)]
LOWERCASE_OTHERS = ['ç', 'á', 'â', ]  # etc.
UPPERCASE_OTHERS = [x.upper() for x in LOWERCASE_OTHERS]
LETTERS = LOWERCASE + UPPERCASE + LOWERCASE_OTHERS + UPPERCASE_OTHERS

def edit1(text):
    words = []
    
    # Fase 1: as remoçoes.
    for p in range(len(text)):
        new_word = text[:p] + text[p + 1:]
        if len(new_word) > 0:
            words.append(new_word)
        
    # Fase 2: as adições.
    for p in range(len(text) + 1):
        for c in LETTERS:
            new_word = text[:p] + c + text[p:]
            words.append(new_word)
    
    # Fase 3: as substituições.
    for p in range(len(text)):
        orig_c = text[p]
        for c in LETTERS:
            if orig_c != c:
                new_word = text[:p] + c + text[p + 1:]
                words.append(new_word)
    
    return set(words)

def edit2(text):
    words1 = edit1(text)
    words2 = set()
    for w in words1:
        candidate_words2 = edit1(w)
        candidate_words2 -= words1
        words2.update(candidate_words2)
    words2 -= set([text])
    return words2

def P(word, vocab): 
    try:
        return vocab[word] / sum(vocab.values())
    except KeyError:
        return 0
        
def candidates(word, vocab):
    if word in vocab:
        candidatos = [word]
    else:
        candidatos = []
    candidatos += \
        [w for w in edit1(word) if w in vocab] \
        + [w for w in edit2(word) if w in vocab] \
        + [word]
    return candidatos

def correction(word, vocab):
    max_p = max(candidates(word, vocab), key=lambda w: P(w,vocab))
    return max_p

def correct_text(text, vocab):
    text_final = ""
    stopwords = frozenset(nltk.corpus.stopwords.words('portuguese'))
    for p in text.split(" "):
        if p in stopwords:
            text_final += p + " "
        else:
            text_final += correction(p, vocab) + " "
    return text_final[:-1]

while True:
    print(correct_text(input(),vocab))