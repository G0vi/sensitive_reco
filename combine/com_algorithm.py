from website.RegToSql import Reg2Sql
from sensitiveword.keyword_match import keyword_match, keyword_match_init_work


class ComAlgorithm:
    def __init__(self):
        self.reg2sql = Reg2Sql()
        self.rematch = self.reg2sql.rematch
        km_init = keyword_match_init_work()
        self.key_match = keyword_match(km_init.keyword_dict, km_init.keyword_sync)
        self.all_type = self.reg2sql.type2level.keys()
        self.acc_type = self.rematch.acc_type
        self.standardize_type()

    def standardize_type(self):
        for eve in self.all_type:
            if eve not in self.acc_type:
                self.acc_type[eve] = 2

    def make_sure(self, reg_result):
        for_sure = []
        not_sure = []
        for res_key in reg_result:
            res = reg_result[res_key]
            max_len = 0
            for eve in res[0]:
                cur_len = eve[2] - eve[1]
                if cur_len > max_len:
                    max_len = cur_len
            cur_id_list, cur_list = res[2], res[3]
            if res[4] == 1:
                for_sure.append((-max_len, max(map(lambda x: -self.reg2sql.type2level[x], cur_id_list)),
                                 cur_id_list, cur_list))
            else:
                # not_sure.append((max(map(lambda x: self.reg2sql.type2level[x], cur_id_list)), max_len,
                # cur_id_list, cur_list))
                assert len(cur_id_list) == len(cur_list)
                for i in range(len(cur_id_list)):
                    not_sure.append((cur_id_list[i], cur_list[i]))
        for_sure.sort()
        not_sure.sort()
        return for_sure, not_sure

    def match_pure_text(self, string):
        reg_result = self.rematch.match_text(string)
        for_sure, not_sure = self.make_sure(reg_result)
        if for_sure:
            return for_sure[0][2][0], for_sure[0][3][0], 3
        elif not_sure:
            return not_sure[0][2][0], not_sure[0][3][0], 1
        return None, None, 5

    def match_dict(self, input_dict):
        if isinstance(input_dict, dict):
            key = list(input_dict.keys())[0]
            value = input_dict[key]
            value = str(value)
        elif isinstance(input_dict, (list, tuple)) and len(input_dict) == 2:
            key, value = input_dict
            value = str(value)
        else:
            return None, None, 0

        if key:
            rule_data_type_id_list, rule_data_type_list = self.key_match.keyword_exact_match_all(key)
            init_arr = [0] * 1000
            for eve in rule_data_type_id_list:
                init_arr[int(eve)] = 1
            if not value:
                #
                return (rule_data_type_id_list[0], rule_data_type_list[0], 2) if rule_data_type_id_list else (None, None
                                                                                                              , 2)
            else:
                reg_result = self.rematch.match_text(value)
                for_sure, not_sure = self.make_sure(reg_result)
                if for_sure:
                    for eve in for_sure:
                        cur_id_list, cur_list = eve[2: 4]
                        for i in range(len(cur_id_list)):
                            if init_arr[cur_id_list[i]]:
                                return cur_id_list[i], cur_list[i], 6
                    return for_sure[0][2][0], for_sure[0][3][0], 5
                elif not_sure:
                    for i in range(len(rule_data_type_id_list)):
                        if (rule_data_type_id_list[i], rule_data_type_list[i]) in not_sure:
                            return rule_data_type_id_list[i], rule_data_type_list[i], 5
                # return (rule_data_type_id_list[0], rule_data_type_list[0]) if rule_data_type_id_list else (None, None)
                # return None, None
                for i in range(len(rule_data_type_id_list)):
                    if self.acc_type[rule_data_type_id_list[i]] == 2:
                        return rule_data_type_id_list[i], rule_data_type_list[i], 4
                return None, None, 4

        else:
            return self.match_pure_text(value)







