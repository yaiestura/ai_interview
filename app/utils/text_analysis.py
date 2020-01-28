from app import app
from homer.analyzer import Article
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
from flask import jsonify
from flask_login import current_user
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import textstat
import textract
import os
import re
import pprint


def words_frequency_distr(tokenized_words, directory):

    fdist = FreqDist(tokenized_words)
    plt.figure(figsize=(10, 7))
    plt.title('Fig.2 Motivational Letter Words Frequency Distribution')
    fdist.plot(25, cumulative=False)

    if not os.path.exists(directory):
        os.makedirs(directory)

    plt.savefig(os.path.join(directory, 'distribution.png'))
    plt.clf()


def sentences_sentiment_analysis(tokenized_text, directory):

    sia = SIA()
    results = []

    for sentence in tokenized_text:
        polarity_score = sia.polarity_scores(sentence)
        polarity_score['headline'] = sentence
        results.append(polarity_score)

    df = pd.DataFrame.from_records(results)

    df['label'] = 0
    df.loc[df['compound'] > 0.2, 'label'] = 1
    df.loc[df['compound'] < -0.2, 'label'] = -1

    fig, ax = plt.subplots(figsize=(10, 7))

    counts = df.label.value_counts(normalize=True) * 100

    sns.barplot(x=counts.index, y=counts, ax=ax)

    ax.set_xticklabels(['Negative', 'Neutral', 'Positive'])
    ax.set_ylabel("Percentage")

    plt.title('Fig.1 Motivational Letter Sentences Polarity Distribution')
    plt.savefig(os.path.join(directory, 'polarity.png'))
    plt.clf()

    return results


def sentiment_analysis(text):

    directory = os.path.join(
        os.path.dirname(app.instance_path), f'app/userdata/{current_user.uname}/text_analytics'
    )

    tokenized_text = sent_tokenize(text)
    tokenized_words = word_tokenize(text)

    words_frequency_distr(tokenized_words, directory)

    return sentences_sentiment_analysis(tokenized_text, directory)



def cv_analysis(cv_letter):

    text = textract.process(cv_letter).decode('utf-8')
    article = Article('Article name', 'Author', text)

    sentiment_data = sentiment_analysis(text)

    text_data = {
        'Reading time': str(article.reading_time) + ' mins',
        'Flesch Reading Ease': article.get_flesch_reading_score(),
        'Dale Chall Readability Score': article.get_dale_chall_reading_score(),
        'Paragraphs': article.total_paragraphs,
        'Avg sentences per paragraph': article.avg_sentences_per_para,
        'Total sentences in longest paragraph': article.len_of_longest_paragraph,
        'Sentences': article.total_sentences,
        'Avg words per sentence': article.avg_words_per_sentence,
        'Longest sentence': "%s..." % str(article.longest_sentence)[0:30],
        'Words in longest sentence': article.len_of_longest_sentence,
        'Words': article.total_words,
        '"and" frequency"': article.get_and_frequency(),
        'Compulsive Hedgers': len(article.get_compulsive_hedgers()),
        'Intensifiers': len(article.get_intensifiers()),
        'Vague words': len(article.get_vague_words()),
        '10 words with most syllables': article.ten_words_with_most_syllables(),
        '20 most repeated words': article.get_n_most_repeated_words(20),
        'The Flesch Reading Ease formula': textstat.flesch_reading_ease(text),
        'The SMOG Index': textstat.smog_index(text),
        'The Flesch-Kincaid Grade Level': textstat.flesch_kincaid_grade(text),
        'The Coleman-Liau Index': textstat.coleman_liau_index(text),
        'Automated Readability Index': textstat.automated_readability_index(text),
        'Dale-Chall Readability Score': textstat.dale_chall_readability_score(text),
        'Difficult words': textstat.difficult_words(text),
        'Linsear Write Formula': textstat.linsear_write_formula(text),
        'The Fog Scale (Gunning FOG Formula)': textstat.gunning_fog(text),
        'Readability Consensus based upon all the above tests': textstat.text_standard(text)
    };

    return sentiment_data, text_data
