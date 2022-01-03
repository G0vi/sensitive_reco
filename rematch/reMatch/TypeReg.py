import re


def rec_type(string, types=None):
    ans = []
    if types == 'float':
        pattern = '(?<![A-Za-z])\d+\.\d+(?![a-zA-Z])'
    elif types == 'int':
        pattern = '(?<![A-Za-z\.0-9])\d+(?!([a-zA-Z0-9]|\.\d))'
    elif types == 'date':
        pattern = "(?<!\d)((1[0-9]{3}|20(\d{2}))-(1[12]|0?[1-9])(-([12][0-9]|3[01]|0?[1-9]))?|(1[0-9]{3}|20(\d{2}))"\
                  "/(1[12]|0?[1-9])(/([12][0-9]|3[01]|0?[1-9]))?|(1[0-9]{3}|20(\d{2}))\.(1[12]|0?[1-9])(\.([12][0-9]|"\
                  "3[01]|0?[1-9]))|([12][0-9]|3[01]|0?[1-9])/(1[12]|0?[1-9])/(1[0-9]{3}|20(\d{2})))(?!\d)"
    elif types == 'bool':
        pattern = '[Tt][Uu][Rr][Ee]|[Ff][Aa][Ll][Ss][Ee]'
    else:
        pattern = None
    if pattern:
        cur_iter = re.finditer(pattern, string)
        for it in cur_iter:
            ans.append((it.group(), it.start(), it.end()))
        return ans
    return None


a = rec_type('2020.02', 'int')
