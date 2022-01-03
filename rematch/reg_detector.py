from .reMatch.ReMatch import ReMatch
from nlp.ner_functions import ner_baby
import torch


class RegDetector:
    def __init__(self, cur_rules):
        self.rules = cur_rules
        self.rematch = None
        self.gen_rematches()

    def gen_rematches(self):
        self.rematch = ReMatch(self.rules)

    def match_text(self, text, list_id=None, need_ner=1):
        if need_ner:
            if ner_baby.act_model is None:
                ner_baby.load_model()
            torch.manual_seed(2021)
            ner_baby.ner_process(text)
        return self.rematch.match_text(text, list_id=list_id, need_ner=need_ner)

