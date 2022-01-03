import sys
sys.path.append('..')
from rematch.reg_detector import RegDetector
from rematch.loadRules.basic_rules import rules


reg_detector = RegDetector(rules)


# 用text的数据测试
def my_test_file(file_path, times):
    text_file = open(file_path, 'r').read()
    from time import time
    start = time()
    ans = {}
    for i in range(times):
        # ner_process(text_file)
        ans = reg_detector.match_text(text_file, need_ner=1)
    end = time()
    for eve in ans:
        print(eve, ans[eve])
    print((end - start) / times)


# path_file = '../rematch/textfile/text1'
# my_test_file(path_file, 30)
print(reg_detector.match_text('张三丰是北航的硕士', need_ner=1))
# my_test_file('../rematch/textfile/text1', 1)
