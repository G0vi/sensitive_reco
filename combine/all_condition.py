from rematch.reg_detector import RegDetector
from sensitiveword.keyword_match import keyword_match, keyword_match_init_work
from rematch.loadRules.map_in_202 import id2dt
from rematch.loadRules.second_rules import loose_rules
import json
import re
from nlp_client.ner_client import cutter


def standardize(words, result):
    ans = []
    table = []
    for i in result:
        cur, description = result[i][0: 2]
        for eve in cur:
            ans.append((eve[1], eve[2], description))
            table.append([eve[0], eve[1], eve[2], description])
    ans.sort()
    length = len(ans)
    if not length:
        return words, []
    use = [list(ans[0])]
    i = 1
    last = ans[0][0:2]
    while i < length:
        if ans[i][0] == last[0]:
            if ans[i][1] == last[1]:
                use[-1][2] += '/' + ans[i][2]
        else:
            if ans[i][0] >= last[1]:
                use.append(list(ans[i]))
                last = ans[i][0: 2]

            else:
                if ans[i][1] <= last[1]:
                    use.pop()
                    last = use[-1][0:2]
                    continue
                else:
                    use.append([last[1], ans[i][1], ans[i][2]])
                last = ans[i][0: 2]
        i += 1
    final = ''
    i = 0
    length = len(use)
    length1 = len(words)
    ind = 0
    while i < length1:
        if ind >= length:
            final += words[i:]
            break
        if i == use[ind][0]:
            final += '<' + use[ind][2] + '>'
            i = use[ind][1]
            ind += 1
        else:
            final += words[i]
            i += 1
    return final, table


def find_index(rule_result, id_list, left, right):
    length = len(rule_result)
    top = 0
    bottom = length - 1
    middle = (top + bottom) // 2
    if rule_result[top][0] > right or rule_result[bottom][0] < left:
        return -1
    while not (rule_result[middle][0] >= left and (rule_result[middle - 1][0] < left or middle == 0)):
        if rule_result[middle][0] < left:
            top = middle + 1
        else:
            bottom = middle - 1
        middle = (top + bottom) // 2
        # print(middle, top, bottom, left, right, rule_result[middle][0], rule_result[middle - 1][0], rule_result)
    start = middle
    top = start
    bottom = length - 1
    middle = (top + bottom) // 2
    while not (rule_result[middle][0] <= right and (middle == length - 1 or rule_result[middle + 1][0] > right)):
        if rule_result[middle][0] > right:
            bottom = middle - 1
        else:
            top = middle + 1
        middle = (top + bottom) // 2
        # print(top, bottom, middle, length, rule_result[middle][0], right, rule_result[middle + 1][0])
    end = middle + 1
    for i in range(start, end):
        cur = rule_result[i][1]
        for eve_id in cur:
            if eve_id in id_list:
                return i
    return -1


def match_rule_reg(rule_result, reg_result, text, score_line, close_index=18):
    text_size = len(text)
    rule_num = len(rule_result)
    rule_tag = [0] * rule_num
    second_result = {}
    start2end = {}
    end2start = {}
    for reg_id in reg_result:
        cur_ans, description, id_list, score = reg_result[reg_id]
        cur_list = []
        for eve in cur_ans:
            start, end = eve[1: 3]
            neighbor = find_index(rule_result, id_list, max(start - close_index, 0), min(end + close_index, text_size - 1))

            if neighbor >= 0:
                rule_tag[neighbor] += 1
                # print("OH yeah", neighbor)
            if neighbor >= 0 or score >= score_line:
                cur_list.append(eve)
                for i in range(start, end):
                    start2end[i] = end
                for i in range(end, start - 1, -1):
                    end2start[i] = start

        if cur_list:
            second_result[reg_id] = (cur_list, description, id_list)
    for i in range(rule_num):
        if not rule_tag[i]:
            index = rule_result[i][0]
            id_list = rule_result[i][1]
            rec_str = text[max(index - close_index, 0): min(index + close_index, text_size)]
            for eve_id in id_list:
                if eve_id in loose_rules:
                    cur_pattern = loose_rules[eve_id]
                    cur_iter = re.finditer(cur_pattern, rec_str)
                    reg_ans = []
                    for it in cur_iter:
                        group = it.group()
                        start = it.start()
                        end = it.end()
                        flag = 0
                        if start in start2end and end < start2end[start]:
                            continue
                        if end in end2start and start > end2start[end]:
                            continue  # 如果已经属于已知的某个匹配结果的子串，跳过
                        if start not in start2end or start2end[start] < end or end not in end2start or end2start[start] > start:
                            flag = 1
                            for j in range(start, end):
                                start2end[j] = max(start2end[j], end) if j in start2end else end
                            for j in range(end, start - 1, -1):
                                end2start[j] = min(end2start[j], start) if j in end2start else start
                        if flag:
                            reg_ans.append((group, start, end))
                    if eve_id + 300 not in second_result:
                        second_result[eve_id + 300] = (reg_ans, id2dt[eve_id][0], [eve_id])
                    else:
                        cur_result_list = second_result[eve_id + 300][0]
                        for eve_ans in reg_ans:
                            if eve_ans not in cur_result_list:
                                cur_result_list.append(eve_ans)
    final_result = {}
    for ans_id in second_result:
        cur_ans = []
        for eve in second_result[ans_id][0]:
            start, end = eve[1: 3]
            if start2end[start] >= end and end2start[end] <= start:
                cur_ans.append(eve)
        if cur_ans:
            final_result[ans_id] = (cur_ans, second_result[ans_id][1], second_result[ans_id][2])
    return final_result


class ComDetector:
    def __init__(self, rules):
        self.reg_detector = RegDetector(rules)
        km_init = keyword_match_init_work()
        self.key_detector = keyword_match(km_init.keyword_dict, km_init.keyword_sync)

    def detect_kv(self, kv, score_line=0.5):
        if not isinstance(kv, dict):
            return None
        keys = list(kv.keys())
        if len(keys) < 1:
            return [], []
        key = keys[0]
        value = kv[key]
        if key:
            return self.key_detector.keyword_exact_match_all(key)
        rec_table = [0] * 500
        final_list = []
        dt_list = []
        cur_reg_result = self.reg_detector.match_text(value)
        for rule_id in cur_reg_result:
            id_list, score = cur_reg_result[rule_id][2: 4]
            if score >= score_line:
                for eve_id in id_list:
                    if not rec_table[eve_id]:
                        rec_table[eve_id] = 1
                        final_list.append(eve_id)
                        dt_list.append(id2dt[eve_id][1])
        return final_list, dt_list

    def detect_json(self, json_str, score_line=0.5):
        try:
            dic = json.loads(json_str)
        except:
            return {}
        for key in dic:
            cur_kv = {key: dic[key]}
            dic[key] = self.detect_kv(cur_kv, score_line=score_line)
        return dic

    def detect_text(self, text, score_line=0.5, list_id=None, ner_en=1):
        first_reg_result = self.reg_detector.match_text(text, list_id=list_id, need_ner=ner_en)
        cut_words = cutter.cut(text)
        first_rule_result = []
        cur_start = 0
        length = len(text)
        for w in cut_words:
            cur_len = len(w)
            cur_index = cur_start
            while cur_start < length:
                if text[cur_start: cur_start + cur_len] == w:
                    cur_index = cur_start
                    cur_start += cur_len
                    break
                else:
                    cur_start += 1

            cur_rule_result = self.key_detector.keyword_exact_match_all(w)[0]  # 返回202 id list
            if cur_rule_result:
                first_rule_result.append((cur_index, cur_rule_result))
        # print(first_rule_result)
        ans = match_rule_reg(first_rule_result, first_reg_result, text, score_line, close_index=18)
        return standardize(text, ans)








