import re


class ReMatch:
    def __init__(self, rule_obs: list):
        self.rule_obs = rule_obs.copy()  # 列表，每个元素是一个dict，包含每一行正则表达式的k-v对
        self.rule_num = len(rule_obs)  # 规则数量
        self.normalize()

    def normalize(self) -> None:  # 将正则表达式规范化处理，去除首尾的空白符，并将整体加上"()"，并将编译好的结果存入self.rules
        for eve in self.rule_obs:
            # if eve['is_enabled'] != 1:
            #    continue
            if 'regex' in eve:
                cur = eve['regex'].strip()
            else:
                cur = eve['regexp'].strip()
            start = 0
            end = len(cur)
            if cur[start] == '^':
                start += 1
            if cur[end - 1] == '$':
                end -= 1
            cur = '(' + cur[start: end] + ')'

            try:
                com_cur = re.compile(cur)
            except:
                com_cur = None
            eve['rule'] = com_cur

    def print_rule(self, rule_ids=None):
        print_all = 1 if rule_ids is None else 0
        for eve in self.rule_obs:
            if print_all:
                print(eve)
            elif eve['id'] in rule_ids:
                print(eve)

    def match_text(self, text: str, list_id=None, need_ner=1) -> dict:  # 根据输入的文本输出匹配结果

        results = {}  # 存放初步的匹配结果
        start2end = {}  # 存放在文本中包含某个坐标的最长匹配串的末位置
        end2start = {}  # 存放在文本中包含某个坐标的最长匹配串的初位置
        # 上面两个字典的意义在于避免出现结果的集合中，某个结果A是B的子串，如：210185194312213425被识别为身份证号，18519431221识别为手机号
        match_all = True if list_id is None else False

        for eve in self.rule_obs:
            rule_id, rule, is_combined_data, description, id_list, score = (eve['id'], eve['rule'],
                                                                            eve['is_combined_data'], eve['description'],
                                                                            eve['202_id'], eve['score'])
            flag = 1 if (need_ner and 'nlp_func' in eve) else 0
            if not rule and not flag:
                continue
            if not match_all and rule_id not in list_id:
                continue
            cur_ans = []
            if not flag:
                cur_iter = rule.finditer(text)
            else:
                cur_iter = eve['nlp_func'](text)
            need_verify = 1 if 'verify' in eve else 0
            for it in cur_iter:
                if not flag:
                    group = it.group()
                    start = it.start()
                    end = it.end()
                else:
                    group, start, end = it
                if need_verify:
                    verify_res = eve['verify'](group)
                    if not verify_res:
                        continue
                    else:
                        start += verify_res[0]
                        end -= verify_res[1]
                        group = group[verify_res[0]: verify_res[1] + len(group)]
                if start in start2end and end < start2end[start]:
                    continue
                if end in end2start and start > end2start[end]:
                    continue  # 如果已经属于已知的某个匹配结果的子串，跳过

                if (start not in start2end or end > start2end[start]) and is_combined_data != 1:
                    for i in range(start, end):
                        if i not in start2end or end > start2end[i]:
                            start2end[i] = end

                if (end not in end2start or start < end2start[end]) and is_combined_data != 1:
                    for i in range(end, start, -1):
                        if i not in end2start or start < end2start[i]:
                            end2start[i] = start  # 将整个(start, end)区间更新最长匹配串的初末位置

                cur_ans.append((group, start, end))  # 加入当前规则的结果集内
            if cur_ans:
                results[rule_id] = (cur_ans, description, id_list, score)

        final_results = {}  # 最后返回的结果集，将results中非最长匹配结果去掉
        for rule_id in results:
            cur_ans = []
            (wait_ans, description, id_list, score) = results[rule_id]
            for eve in wait_ans:
                group, start, end = eve
                if (start not in start2end or end not in end2start) or (
                        start2end[start] <= end and end2start[end] >= start):
                    cur_ans.append(eve)
            if cur_ans:
                final_results[rule_id] = (cur_ans, description, id_list, score)
        return final_results
