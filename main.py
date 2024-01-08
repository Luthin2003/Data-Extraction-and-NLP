from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import os
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')


# this is the function which is used to extract/scrape the data from website
def creating_file(url_id, url):
    source = requests.get(url).text
    soup = BeautifulSoup(source, 'lxml')

    flg = 0  # for checking error

    try:
        heading = soup.find("h1", class_=["entry-title", "tdb-title-text"]).text
    except Exception as e:
        flg = 1
        print(f"{url_id} heading problem: {e}")
        return

    try:
        article_text = ""
        for p in soup.find_all('p'):
            article_text += p.text
    except Exception as e:
        flg = 1
        print(f"{url_id} article text problem: {e}")
        return

    if flg == 0:
        with open(os.path.join("txtfiles" , f"{url_id}.txt"), 'w', encoding='utf-8') as file:
            file.write(heading + "\n" + article_text)


# this is a function which is used to call the creating_file function and provide the url for scrapping the data
def extract_from_excel(file_path="Input.xlsx"):
    df = pd.read_excel(file_path)

    col1 = df[["URL_ID", "URL"]].values.tolist();

    for data in col1:
        creating_file(data[0], data[1])


# this is function returns  positive_score,  negative_score , polarity_score ,subjectivity_score
def positive_negative():
    master_dir = "MasterDictionary"
    stopwords_dir = "StopWords"
    txt_dir = "txtfiles"

    pos = set()
    neg = set()

    for files in os.listdir(master_dir):
        if files == 'positive-words.txt':
            with open(os.path.join(master_dir, files), 'r', encoding='ISO-8859-1') as f:
                pos.update(f.read().splitlines())
        else:
            with open(os.path.join(master_dir, files), 'r', encoding='ISO-8859-1') as f:
                neg.update(f.read().splitlines())

    stop_words = set()

    for files in os.listdir(stopwords_dir):
        with open(os.path.join(stopwords_dir, files), 'r', encoding='ISO-8859-1') as f:
            stop_words.update(set(f.read().splitlines()))

    docs = []

    for files in os.listdir(txt_dir):
        with open(os.path.join(txt_dir, files), 'r', encoding='ISO-8859-1') as f:
            text = f.read()
            words = word_tokenize(text)

            newTxt = []

            for word in words:
                if word.lower() not in stop_words:
                    newTxt.append(word)

            docs.append(newTxt)

    positive_words = []
    negative_words = []
    positive_score = []
    negative_score = []
    polarity_score = []
    subjectivity_score = []

    for i in range(len(docs)):
        positive_words.append([word for word in docs[i] if word.lower() in pos])
        negative_words.append([word for word in docs[i] if word.lower() in neg])
        positive_score.append(len(positive_words[i]))
        negative_score.append(len(negative_words[i]))
        polarity_score.append(
            (positive_score[i] - negative_score[i]) / ((positive_score[i] + negative_score[i]) + 0.000001))
        subjectivity_score.append((positive_score[i] + negative_score[i]) / ((len(docs[i])) + 0.000001))

    return positive_score, negative_score, polarity_score, subjectivity_score


# this functions return avg_sentence_length , Percentage_of_Complex_words, Fog_Index,complex_word_count ,avg_syllable_word_count
def analysis_readability():
    master_dir = "MasterDictionary"
    stopwords_dir = "StopWords"
    txt_dir = "txtfiles"
    avg_sentence_length = []
    Percentage_of_Complex_words = []
    Fog_Index = []
    complex_word_count = []
    avg_syllable_word_count = []

    stop_words = set(stopwords.words('english'))

    for file in os.listdir(txt_dir):
        with open(os.path.join(txt_dir, file), 'r', encoding='ISO-8859-1') as f:
            text = f.read()
            text = re.sub(r'[^\w\s.]', '', text)
            sentences = text.split('.')
            num_sentences = len(sentences)
            newTxt = []

            for word in text.split():
                if word.lower() not in stop_words:
                    newTxt.append(word)

            num_words = len(newTxt)
            complex_words = []
            for word in newTxt:
                vowels = 'aeiou'
                syllable_count_word = 0
                for letter in word:
                    if letter.lower() in vowels:
                        syllable_count_word += 1

                if syllable_count_word > 2:
                    complex_words.append(word)

            syllable_count = 0
            syllable_words = []

            for word in newTxt:
                if word.endswith('es'):
                    word = word[:-2]
                elif word.endswith('ed'):
                    word = word[:-2]

                vowels = 'aeiou'
                syllable_count_word = 0
                for letter in word:
                    if letter.lower() in vowels:
                        syllable_count_word += 1

                if syllable_count_word >= 1:
                    syllable_words.append(word)
                    syllable_count += syllable_count_word

            avg_sentence_len = num_words / num_sentences
            avg_syllable_item_count = syllable_count / len(syllable_words)
            Percent_Complex_words = len(complex_words) / num_words
            fog_item_index = 0.4 * (avg_sentence_len + Percent_Complex_words)

            avg_sentence_length.append(avg_sentence_len)
            Percentage_of_Complex_words.append(Percent_Complex_words)
            Fog_Index.append(fog_item_index)
            complex_word_count.append(len(complex_words))
            avg_syllable_word_count.append(avg_syllable_item_count)

    return avg_sentence_len, Percentage_of_Complex_words, Fog_Index, complex_word_count, avg_syllable_word_count


# this function is used to return word_count , average_word_length
def cleaned_words():
    txt_dir = "txtfiles"
    stop_words = set(stopwords.words('english'))

    word_count = []
    average_word_length = []

    for file in os.listdir(txt_dir):
        with open(os.path.join(txt_dir, file), 'r', encoding='ISO-8859-1') as f:
            text = f.read()
            text = re.sub(r'[^\w\s]', '', text)
            words = []
            for word in text.split():
                if word.lower() not in stop_words:
                    words.append(word)

            length = sum(len(word) for word in words)
            average_word_length_of_item = length / len(words)
            word_count.append(len(words))
            average_word_length.append(average_word_length_of_item)

    return word_count, average_word_length


# this function is used to return personal pronouns
def count_personal_pronouns():
    txt_dir = "txtfiles"
    stop_words = set(stopwords.words('english'))

    pp_count = []

    for file in os.listdir(txt_dir):
        with open(os.path.join(txt_dir, file), 'r', encoding='ISO-8859-1') as f:
            text = f.read()
            personal_pronouns = ["I", "we", "my", "ours", "us"]
            count = 0
            for pronoun in personal_pronouns:
                count += len(re.findall(r"\b" + pronoun + r"\b", text))
        pp_count.append(count)

    return pp_count


if __name__ == "__main__":

    # this call will scrape the data from the website
    # extract_from_excel()

    POSITIVE_SCORE, NEGATIVE_SCORE, POLARITY_SCORE, SUBJECTIVITY_SCORE = positive_negative()
    AVG_SENTENCE_LENGTH, PERCENTAGE_OF_COMPLEX_WORDS, FOG_INDEX, COMPLEX_WORD_COUNT, SYLLABLE_PER_WORD = analysis_readability()
    WORD_COUNT, AVG_WORD_LENGTH = cleaned_words()
    PERSONAL_PRONOUNS = count_personal_pronouns()
    AVG_NUMBER_OF_WORDS_PER_SENTENCE = AVG_SENTENCE_LENGTH

    output_df = pd.read_excel('Output_Data_Structure.xlsx')

    # this used to drop 49 (48 +1) and 36 (35 + 1) col
    output_df.drop([48, 35], axis=0, inplace=True)

    variables = [POSITIVE_SCORE,
                 NEGATIVE_SCORE,
                 POLARITY_SCORE,
                 SUBJECTIVITY_SCORE,
                 AVG_SENTENCE_LENGTH,
                 PERCENTAGE_OF_COMPLEX_WORDS,
                 FOG_INDEX,
                 AVG_NUMBER_OF_WORDS_PER_SENTENCE,
                 COMPLEX_WORD_COUNT,
                 WORD_COUNT,
                 SYLLABLE_PER_WORD,
                 PERSONAL_PRONOUNS,
                 AVG_WORD_LENGTH]

    for i, var in enumerate(variables):
        output_df.iloc[:, i + 2] = var

    output_df.to_excel('Output_Data_Structure.xlsx', index=False)
