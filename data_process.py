import pandas as pd


def change_file_to_csv(file_path, replace='O', out_name=''):
    content = open(file_path, 'r').read().split('\n')
    segments = []
    seg_labels = []
    length = len(content)
    words = []
    labels = []
    pairs = []
    types = {}

    for i in range(length + 1):
        if i == length or (not content[i].strip()):
            if len(words):
                segments.append(''.join(words))
                seg_labels.append(' '.join(labels))
            words = []
            labels = []
            continue
        cur_word, cur_label = content[i].split()
        cur_type = cur_label.split('-')[-1]
        if cur_type == 'ORG':
            cur_label = replace
        else:
            if cur_type not in types:
                types[cur_type] = 1
        words.append(cur_word)
        labels.append(cur_label)

    assert len(segments) == len(seg_labels)
    length = len(segments)
    for i in range(length):
        pairs.append({'id': i, 'text': segments[i], 'BIO_anno': seg_labels[i]})
    dataframe = pd.DataFrame(pairs, columns=['id', 'text', 'BIO_anno'])
    if not out_name:
        out_name = file_path + '.csv'
    dataframe.to_csv(out_name, index=False)
    return types.keys()


if __name__ == '__main__':
    # change_file_to_csv('data/dev.char.bmes')
    all_types = {'NAME', 'TITLE', 'RACE', 'CONT', 'PRO', 'LOC', 'EDU'}
    list = ['O']
    for eve_type in all_types:
        list.append('B-' + eve_type)
        list.append('M-' + eve_type)
        list.append('E-' + eve_type)
    print(list)
    # idx = {}
    # for id_ in range(len(list)):
    #     idx[list[id_]] = id_
    # print(idx)



