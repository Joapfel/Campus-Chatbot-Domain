import os
import re
from tqdm import tqdm
from collections import OrderedDict


def clean_numbers(text) -> str:
    return re.sub('\\d+', '', text).strip()


def clean_non_words(text) -> str:
    return re.sub(u'^\\W+|\\W+$', '', text).strip()


if __name__ == "__main__":
    file_in = './adviser/resources/databases/topics.txt'
    file_out = './adviser/resources/databases/topics_cleaned.txt'
    print(os.getcwd())

    out = OrderedDict()
    with open(file_in, 'r', encoding='utf-8') as file:
        for line in tqdm(file):
            if len(line.strip().split('\t')) == 2:
                ngrams, count = line.strip().split('\t')
                ngrams = clean_numbers(ngrams)
                ngrams_cleaned = []
                for ngram in ngrams.split():
                    ngrams_cleaned.append(clean_non_words(ngram))

                ngrams_cleaned = ' '.join(ngrams_cleaned)
                if len(ngrams_cleaned) > 3:
                    if ngrams_cleaned not in out:
                        out[ngrams_cleaned] = int(count)
                    else:
                        out[ngrams_cleaned] += 1

    with open(file_out, 'w', encoding='utf-8') as file:
        for ngram, count in out.items():
            file.write(ngram + '\t' + str(count) + '\n')
