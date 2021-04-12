import json
import re
from nltk import word_tokenize
from collections import defaultdict, Counter
import nltk
import numpy as np
import pickle

with open("dump_small.jsonln", 'r') as file:
    data = [json.loads(line) for line in file]

def limpa_ref(texto):
    pattern = r"""<ref>.*?</ref>"""
    repl = r""
    matcher = re.compile(pattern, re.VERBOSE)
    return matcher.sub(repl, texto)

def limpa_aspas(texto):
    pattern = r"""(['"]+)(.*?)\1"""
    repl = r"\2"
    matcher = re.compile(pattern, re.VERBOSE)
    return matcher.sub(repl, texto)

def limpa_url(texto):
    # Regex obtida de https://www.geeksforgeeks.org/python-check-url-string/
    pattern = r"""
        (?i)  # Ignore case.
        \b  # Inicio de palavra.
        (?:
            https?://
        |
            www
            \d{0,3}
            [.]
        |
            [a-z0-9.\-]+
            [.]
            [a-z]{2,4}
            /
        )
        (?:
            [^\s()<>]+
        |
            \(
            (?:
                [^\s()<>]+
            |
                \(
                [^\s()<>]+
                \)
            )*
            \)
        )+
        (?:
            \(
            (?:
                [^\s()<>]+
            |
                \(
                [^\s()<>]+
                \)
            )*
            \)
        |
            [^\s`!()\[\]{};:'\".,<>?«»“”‘’]
        )
    """
    repl = ''
    matcher = re.compile(pattern, re.VERBOSE)
    return matcher.sub(repl, texto)

def limpa_templates(texto):
    conta = 0
    spans_proibidos = []
    for item in re.finditer(r'{{|}}', texto):
        if item[0] == '{{':
            if conta == 0:
                inicio = item.span()[0]
            conta += 1
        else:
            conta -= 1
            if conta == 0:
                fim = item.span()[1]
                spans_proibidos.append((inicio, fim))
    texto_limpo = ''
    inicio = 0
    for span in spans_proibidos:
        fim, novo_inicio = span
        texto_limpo += texto[inicio:fim]
        inicio = novo_inicio
    texto_limpo += texto[inicio:]
    return texto_limpo

def limpa_wikilinks(texto):
    pattern = r'''
        \[\[
        (?:
            [^|]*?\|
        )*?
        (
            [^|]*?
        )
        \]\]
    '''
    repl = r'\1'
    matcher = re.compile(pattern, re.VERBOSE)
    return matcher.sub(repl, texto)

def limpa_cat(texto):
    pattern = r"""\[\[Categoria:.*?\]\]"""
    repl = r""
    matcher = re.compile(pattern)
    return matcher.sub(repl, texto)

def minusculas(tokens):
    return [token.lower() for token in tokens]

def remove_digitos(tokens):
    matcher = re.compile('[^\d]*')
    return [token for token in tokens if matcher.fullmatch(token)]

def pega_palavras(tokens):
    matcher = re.compile('[a-záéíóúçâêôãõà]+(?:-[a-záéíóúçâêôãõà]+)*')
    return [token for token in tokens if matcher.fullmatch(token)]

def remove_stopwords(tokens):
    stopwords = nltk.corpus.stopwords.words('portuguese')
    return [token for token in tokens if token not in stopwords]
    
def limpa_texto(texto):
    texto = limpa_aspas(texto)
    texto = limpa_ref(texto)
    texto = limpa_url(texto)
    texto = limpa_templates(texto)
    texto = limpa_wikilinks(texto)
    texto = limpa_cat(texto)
    return texto

def limpa_tokens(tokens):
    tokens = minusculas(tokens)
    tokens = remove_digitos(tokens)
    tokens = pega_palavras(tokens)
    return tokens

all_words = []

for item in data:
    texto = item['body']
    texto = limpa_texto(texto)
    tokens = word_tokenize(texto)
    tokens = limpa_tokens(tokens)
    tokens = remove_stopwords(tokens)
    all_words += tokens

all_words_clean = limpa_tokens(all_words)
word_counts = defaultdict(int)
for w in all_words_clean:
    word_counts[w] += 1

word_counts = Counter(all_words_clean)
word_counts_list = list(word_counts.items())
word_counts_list_sorted = dict(sorted(word_counts_list, key=lambda x: (-x[1], x[0]))[:3000])

with open("vocab","wb+") as f:
    pickle.dump(word_counts_list_sorted, f)
