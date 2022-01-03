import sys
sys.path.append('..')
from combine.all_condition import ComDetector
from rematch.loadRules.basic_rules import rules

detector = ComDetector(rules)
text = open('../rematch/textfile/text1', 'r').read()

ans = detector.detect_text(text)
print(ans[0])
print(ans[1])
