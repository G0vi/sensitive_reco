import re

from nlp.bi_lstm_crf import NER, tag_to_ix, all_tags


def get_name(text):
    ner_baby.get_names()
    return ner_baby.names


def get_place(text):
    ner_baby.get_locs()
    return ner_baby.locs


def get_edu(text):
    ner_baby.get_educations()
    return ner_baby.educations


def get_title(text):
    ner_baby.get_titles()
    return ner_baby.titles


class NerAnswers:
    def __init__(self):
        self.act_model = None
        self.names = []
        self.locs = []
        self.races = []
        self.educations = []
        self.titles = []
        self.annotates = []
        self.cur_text = ''

    def clear(self):
        self.names = []
        self.locs = []
        self.races = []
        self.educations = []
        self.titles = []
        self.annotates = []
        self.cur_text = ''

    def ner_process(self, text: str):
        self.clear()
        self.cur_text = text
        pass_str = ['\t', '\n', ' ', '\r']
        for eve in pass_str:
            self.cur_text = self.cur_text.replace(eve, '。')
        # 分句处理准确率更高
        predict_texts = self.cur_text.split('。')
        for eve_text in predict_texts:
            if eve_text.strip():
                annotates = self.act_model.predict(eve_text)
                self.annotates.append((eve_text, annotates))
        return self.annotates

    def load_model(self):
        self.act_model = NER('../bert-base', tag_to_ix, all_tags, hidden_dim=50)
        self.act_model.load('../models/model_9')

    def get_class(self, class_name: str):
        answers = []
        for eve_pair in self.annotates:
            cur_text, cur_annotates = eve_pair
            assert len(cur_text) == len(cur_annotates)
            i = 0
            length = len(cur_text)
            while i < length:
                if cur_annotates[i] == 'B-' + class_name:
                    j = i + 1
                    while j < length and cur_annotates[j] != 'E-' + class_name:
                        j += 1

                    cur_group = cur_text[i: j + 1]
                    i = j + 1
                    to_real_ans = []
                    find_in_text = re.finditer(cur_group, self.cur_text)
                    for it in find_in_text:
                        to_real_ans.append((it.group(), it.start(), it.end()))
                    answers.extend(to_real_ans)
                else:
                    i += 1
        return answers

    def get_names(self):
        self.names = self.get_class('NAME')

    def get_locs(self):
        self.locs = self.get_class('LOC')

    def get_races(self):
        self.races = self.get_class('RACE')

    def get_titles(self):
        self.titles = self.get_class('TITLE')

    def get_educations(self):
        self.educations = self.get_class('EDU')


ner_baby = NerAnswers()
