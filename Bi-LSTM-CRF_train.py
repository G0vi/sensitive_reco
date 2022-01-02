import random
import logging
import pandas as pd
from ast import literal_eval
from pytorch_pretrained_bert import BertTokenizer, BertModel
import sys
import torch
from tqdm import tqdm
import torch.autograd as autograd
import torch.nn as nn
import torch.optim as optim


def argmax(vec):
    _, idx = torch.max(vec, 1)
    return idx.view(-1, 1)


# Compute log sum exp in a numerically stable way for the forward algorithm
# 前向算法是不断累积之前的结果，这样就会有个缺点：
# 指数和累积到一定程度后，会超过计算机浮点值的最大值，变成inf，这样取log后也是inf
# 为了避免这种情况，用一个合适的值clip去提指数和的公因子，这样就不会使某项变得过大而无法计算
# SUM = log(exp(s1)+exp(s2)+...+exp(s100))
#     = log{exp(clip)*[exp(s1-clip)+exp(s2-clip)+...+exp(s100-clip)]}
#     = clip + log[exp(s1-clip)+exp(s2-clip)+...+exp(s100-clip)]
# where clip=max
def log_sum_exp(vec):
    # max_score = vec[0, argmax(vec)]
    max_score = vec.gather(1, argmax(vec))
    max_score_broadcast = max_score.repeat(1, vec.size()[1])
    summary = torch.sum(torch.exp(vec - max_score_broadcast), 1)

    return max_score + torch.log(summary).view(-1, 1)


class BertBiLSTMCRF(nn.Module):
    def __init__(self, bert_path: str, tag2ix, hidden_dim, lstm_layers=2, device='cuda:0'):
        super().__init__()
        self.tokenizer = BertTokenizer.from_pretrained(bert_path)
        self.bert = BertModel.from_pretrained(bert_path)
        self.embedding_dim = 768
        self.hidden_dim = hidden_dim
        self.tag_to_ix = tag2ix
        self.tag_num = len(tag2ix)
        embedding_dim = 768
        self.lstm = nn.LSTM(embedding_dim, hidden_dim // 2, num_layers=lstm_layers, bidirectional=True)
        self.layer_num = lstm_layers

        # 将BiLSTM提取的特征向量映射到特征空间，即经过全连接得到发射分数
        self.hidden2tag = nn.Linear(hidden_dim, self.tag_num)
        self.device = device
        # 转移矩阵的参数初始化，transitions[i,j]代表的是从第j个tag转移到第i个tag的转移分数
        self.transitions = nn.Parameter(
            torch.randn(self.tag_num, self.tag_num).to(self.device))

        # 初始化所有其他tag转移到START_TAG的分数非常小，即不可能由其他tag转移到START_TAG
        # 初始化STOP_TAG转移到所有其他tag的分数非常小，即不可能由STOP_TAG转移到其他tag
        self.transitions.data[tag_to_ix[START_TAG], :] = -10000
        self.transitions.data[:, tag_to_ix[STOP_TAG]] = -10000

    def init_hidden(self, batch_size=1):
        # 初始化LSTM的参数
        return (torch.randn(self.layer_num * 2, batch_size, self.hidden_dim // 2).to(self.device),
                torch.randn(self.layer_num * 2, batch_size, self.hidden_dim // 2).to(self.device))
    
    def _forward_alg(self, feats):
        # 通过前向算法递推计算
        init_alphas = torch.full((len(feats), self.tag_num), -10000.).to(self.device)
        # 初始化step 0即START位置的发射分数，START_TAG取0，其他位置取-10000
        # init_alphas[0][self.tag_to_ix[START_TAG]] = 0.
        previous = init_alphas.scatter(1, torch.zeros(len(feats), 1).long().to(self.device), 0.)
        # 将初始化START位置为0的发射分数赋值给previous

        # 迭代整个句子
        for i in range(len(feats[0])):
            obs = feats[:, i]
            # 当前时间步的前向tensor
            alphas_t = []
            for next_tag in range(self.tag_num):
                # 取出当前tag的发射分数，与之前时间步的tag无关
                emit_score = obs[:, next_tag].view(-1, 1).repeat(1, self.tag_num)
                # 取出当前tag由之前tag转移过来的转移分数
                trans_score = self.transitions[next_tag].expand(len(feats), self.tag_num)
                # 当前路径的分数：之前时间步分数 + 转移分数 + 发射分数
                next_tag_var = previous + trans_score + emit_score
                # 对当前分数取log-sum-exp
                alphas_t.append(log_sum_exp(next_tag_var))
            # 更新previous 递推计算下一个时间步
            previous = torch.cat(alphas_t, 1)
        # 考虑最终转移到STOP_TAG
        terminal_var = previous + self.transitions[self.tag_to_ix[STOP_TAG]].expand(len(feats), self.tag_num)
        # 计算最终的分数
        scores = log_sum_exp(terminal_var)
        return scores

    def _get_lstm_features(self, sentences_ids):
        # 通过Bi-LSTM提取特征

        embeds, _ = self.bert(sentences_ids, attention_mask=sentences_ids > 0.5)
        embedding = embeds[11]
        self.hidden = self.init_hidden(batch_size=len(embedding[0]))
        lstm_out, self.hidden = self.lstm(embedding, self.hidden)
        lstm_out = lstm_out.view(len(sentences_ids), len(sentences_ids[0]), self.hidden_dim)
        lstm_feats = self.hidden2tag(lstm_out)
        return lstm_feats

    def _score_sentence(self, feats, tags):
        # 计算给定tag序列的分数，即一条路径的分数
        score = torch.zeros(len(tags), 1).to(self.device)
        first = torch.tensor([self.tag_to_ix[START_TAG]], dtype=torch.long).expand(len(tags), 1).to(self.device)
        tags = torch.cat([first, tags], 1)
        for i in range(len(feats[0])):
            # 递推计算路径分数：转移分数 + 发射分数
            feat = feats[:, i]
            first = torch.unsqueeze(tags[:, i + 1], 0)
            second = torch.unsqueeze(tags[:, i], 0)
            index_list = torch.cat([first, second], 0)
            score = score + self.transitions[list(index_list)].view(-1, 1) + feat.gather(1, tags[:, i + 1].view(-1, 1))
        first = torch.tensor([self.tag_to_ix[STOP_TAG]] * len(tags)).to(self.device)
        first = torch.unsqueeze(first, 0)
        second = torch.unsqueeze(tags[:, -1], 0)
        index_list = torch.cat([first, second], 0)
        score = score + self.transitions[list(index_list)].view(-1, 1)
        return score

    # 使用Viterbi，求解最优路径（即累计分数最大）
    def _viterbi_decode(self, feats):
        back_pointers = []
        if feats.dim() > 1:
            feats = feats[0]
        # 初始化viterbi的previous变量
        init_vars = torch.full((1, self.tag_num), -10000.).to(self.device)
        init_vars[0][self.tag_to_ix[START_TAG]] = 0

        previous = init_vars
        for obs in feats:
            # 保存当前时间步的回溯指针
            bp_trs_t = []
            # 保存当前时间步的viterbi变量
            viterbi_vars_t = []

            for next_tag in range(self.tag_num):
                # 维特比算法记录最优路径时只考虑上一步的分数以及上一步tag转移到当前tag的转移分数
                # 并不取决与当前tag的发射分数
                next_tag_var = previous + self.transitions[next_tag]
                best_tag_id = argmax(next_tag_var)
                bp_trs_t.append(best_tag_id)
                viterbi_vars_t.append(next_tag_var[0][best_tag_id].view(1))
            # 更新previous，加上当前tag的发射分数obs
            previous = (torch.cat(viterbi_vars_t) + obs).view(1, -1)
            # 回溯指针记录当前时间步各个tag来源前一步的tag
            back_pointers.append(bp_trs_t)

        # Transition to STOP_TAG
        # 考虑转移到STOP_TAG的转移分数
        terminal_var = previous + self.transitions[self.tag_to_ix[STOP_TAG]]
        best_tag_id = argmax(terminal_var)
        path_score = terminal_var[0][best_tag_id]

        # 通过回溯指针解码出最优路径
        best_path = [best_tag_id]
        # best_tag_id作为线头，反向遍历back_pointers找到最优路径
        for bp_trs_t in reversed(back_pointers):
            best_tag_id = bp_trs_t[best_tag_id]
            best_path.append(best_tag_id)
        # 去除START_TAG
        start = best_path.pop()
        assert start == self.tag_to_ix[START_TAG]  # Sanity check
        best_path.reverse()
        return path_score, best_path
    
    def neg_log_likelihood(self, sentence, tags):
        # CRF损失函数由两部分组成，真实路径的分数和所有路径的总分数。
        # 真实路径的分数应该是所有路径中分数最高的。
        # log真实路径的分数/log所有可能路径的分数，越大越好，构造crf loss函数取反，loss越小越好
        feats = self._get_lstm_features(sentence)
        forward_score = self._forward_alg(feats)
        gold_score = self._score_sentence(feats, tags)
        return forward_score - gold_score
    
    # 前向传播，计算score和tag_seq
    def forward(self, sentence):
        # 通过BiLSTM提取发射分数
        lstm_feats = self._get_lstm_features(sentence)

        # 根据发射分数以及转移分数，通过Viterbi算法找到一条最优路径
        score, tag_seq = self._viterbi_decode(lstm_feats)
        return score, tag_seq


class NER:
    def __init__(self, bert_model_path, tag2ix, tag_list, hidden_dim=50, device='cuda:0'):
        if 'cuda' in device and not torch.cuda.is_available():
            self.device = 'cpu'
        else:
            self.device = device
        self.model = BertBiLSTMCRF(bert_model_path, tag2ix, hidden_dim=hidden_dim, device=self.device)
        self.losses = torch.tensor(0).float().to(self.device)
        self.total_size = torch.tensor(0).to(self.device)
        self.tag_list = tag_list
        self.model.to(self.device)

    def token2ids(self, token):
        token_list = []
        token = list(token)
        for eve_tok in token:
            token_list += self.model.tokenizer.tokenize(eve_tok)
        cur_id = self.model.tokenizer.convert_tokens_to_ids(token_list)
        return cur_id

    def data_loader(self, train_data, batch_size=256):
        tags = []
        all_ids = []
        for pair in train_data:
            token, labels = pair
            assert(len(token) == len(labels))
            cur_id = self.token2ids(token)
            cur_tag = [self.model.tag_to_ix[entity] for entity in labels]
            all_ids.append(cur_id)
            tags.append(cur_tag)
            if len(cur_id) != len(cur_tag):
                print('错误')
                print(len(cur_id), len(cur_tag), pair)
        return self.make_batch([all_ids, tags], batch_size=batch_size, padding=0)

    @staticmethod
    def make_batch(src_data: list, batch_size=256, padding=None):
        length = len(src_data[0])
        final_batches = []
        for start in range(0, length, batch_size):
            end = start + batch_size if start + batch_size <= length else length
            cur_batch = []
            if padding is not None:
                cur_max_len = max([len(eve_segment) for eve_segment in src_data[0][start: end]])
                # print(cur_max_len)
                for eve_data in src_data:
                    cur_waiting = eve_data[start: end]
                    cur_padded = []
                    for eve_wait in cur_waiting:
                        cur_padded.append(eve_wait + [padding] * (cur_max_len - len(eve_wait)))
                    cur_batch.append(cur_padded)
            else:
                for eve_data in src_data:
                    cur_batch.append(eve_data[start: end])
            final_batches.append(cur_batch)
        return final_batches

    def update_loss(self, loss, batch_size):
        cur_size = self.total_size + batch_size
        self.losses = (self.losses * self.total_size + loss * batch_size) / cur_size
        self.total_size = cur_size

    def resume(self):
        self.losses -= self.losses
        self.total_size -= self.total_size

    def train(self, data_to_train, epochs=22, lr=1e-2, decay=1e-4, batch_size=256, model_dir='models/model_'):
        # optimizer = optim.SGD(self.model.parameters(), lr=lr, weight_decay=decay)
        bert_params = list(map(id, self.model.bert.parameters()))
        base_params = filter(lambda p: id(p) not in bert_params,  self.model.parameters())

        optimizer = optim.AdamW([{'params': base_params},
                                 {'params': self.model.bert.parameters(), 'lr': lr / 100}], lr=lr)
        train_batches = self.data_loader(data_to_train, batch_size=batch_size)
        for epoch in range(1 + epochs):
            print('the', epoch, ' epoch')
            self.resume()
            for batch in tqdm(train_batches):
                cur_ids, cur_tags = batch
                self.model.zero_grad()
                cur_ids = torch.tensor(cur_ids).long().to(self.device)
                cur_tags = torch.tensor(cur_tags).long().to(self.device)
                loss = torch.sum(self.model.neg_log_likelihood(cur_ids, cur_tags))
                print(loss)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                self.update_loss(loss, len(batch))
            print('cur_loss:', self.losses)
            self.save(model_dir + str(epoch))

    def save(self, filename):
        torch.save(self.model.state_dict(), filename)

    def load(self, model_path: str):
        if self.device == 'cpu':
            self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        else:
            self.model.load_state_dict(torch.load(model_path))

    def predict(self, token):
        # ans = []
        # for eve_data in data_to_test:
        #     cur_ans = self.model(eve_data)[1]
        #     cur_tags = []
        #     for eve in cur_ans:
        #         cur_tags.append(self.tag_list[eve])
        #     ans.append(cur_tags)
        # return ans
        data_to_test = torch.unsqueeze(torch.tensor(self.token2ids(token)).to(self.device), 0)
        cur_ans = self.model(data_to_test)[1]
        cur_tags = []
        for eve in cur_ans:
            cur_tags.append(self.tag_list[eve])
        return cur_tags


def data_process(file_path):
    data_src = pd.read_csv(file_path)
    data_src['BIO_anno'] = data_src['BIO_anno'].apply(lambda x: x.split(' '))
    data_src['training_data'] = data_src.apply(lambda row: (row['text'], row['BIO_anno']), axis=1)
    using_data = []
    for i in range(len(data_src)):
        using_data.append(data_src.iloc[i]['training_data'])
    return using_data


if __name__ == '__main__':
    torch.manual_seed(2021)
    training_data = data_process('data/train.char.bmes.csv')
    random.shuffle(training_data)
    testing_data = data_process('data/test.char.bmes.csv')

    START_TAG = "<START>"
    STOP_TAG = "<STOP>"

    HIDDEN_DIM = 50
    tag_to_ix = {'O': 0, 'B-TITLE': 1, 'M-TITLE': 2, 'E-TITLE': 3, 'B-NAME': 4, 'M-NAME': 5, 'E-NAME': 6, 'B-CONT': 7,
                 'M-CONT': 8, 'E-CONT': 9, 'B-RACE': 10, 'M-RACE': 11, 'E-RACE': 12, 'B-LOC': 13, 'M-LOC': 14,
                 'E-LOC': 15,
                 'B-EDU': 16, 'M-EDU': 17, 'E-EDU': 18, 'B-PRO': 19, 'M-PRO': 20, 'E-PRO': 21, 'S-RACE': 22,
                 'S-NAME': 23,
                 START_TAG: 24, STOP_TAG: 25}

    all_tags = ['O', 'B-TITLE', 'M-TITLE', 'E-TITLE', 'B-NAME', 'M-NAME', 'E-NAME', 'B-CONT', 'M-CONT', 'E-CONT',
                'B-RACE', 'M-RACE', 'E-RACE', 'B-LOC', 'M-LOC', 'E-LOC', 'B-EDU', 'M-EDU', 'E-EDU', 'B-PRO', 'M-PRO',
                'E-PRO', 'S-RACE', 'S-NAME', START_TAG, STOP_TAG]
    act_model = NER('bert-base', tag_to_ix, all_tags, hidden_dim=50)
    print('model loading...')
    act_model.load('models/model_9')
    print('model loaded.')
    # act_model.train(training_data, batch_size=64)
    # print(testing_data[0])
    # answers = act_model.predict(testing_data[0][0])
    source = testing_data[34]
    print(source[0])
    answers = source[1]
    predict_ans = act_model.predict(source[0])
    print(answers)
    print(predict_ans)

# tag字典
# tag_to_ix = { "O": 0, "B-BANK": 1, "I-BANK": 2, "B-PRODUCT":3,'I-PRODUCT':4,
#              'B-COMMENTS_N':5, 'I-COMMENTS_N':6, 'B-COMMENTS_ADJ':7,
#              'I-COMMENTS_ADJ':8, START_TAG: 9, STOP_TAG: 10}


# 网络模型训练
# EPOCHS = 20  # 这里需要修改！！
# for epoch in range(EPOCHS):
#
#     print(f'Time Taken: {round(time.time()-t)} seconds')
#     for sentence, tags in training_data:
#         # 第一步，pytorch梯度累积，需要清零梯度
#         model.zero_grad()
#
#         # 第二步，将输入转化为tensors
#         sentence_in = prepare_sequence(sentence, word_to_ix)
#         targets = torch.tensor([tag_to_ix[t] for t in tags], dtype=torch.long)
#
#         # 第三步，前向计算，得到crf loss
#         loss = model.neg_log_likelihood(sentence_in, targets)
#
#         # 第四步，loss反向传播，通过optimier更新参数
#         loss.backward()
#         optimizer.step()
#     # 每1轮保存一次模型，每一轮大约需要10分钟
#     if (epoch+1) % 1 == 0:
#         file_name = "model{}.pt".format(epoch+1)
#         torch.save(model.state_dict(), file_name)
#         print('{} saved'.format(file_name))

# 训练结束查看模型预测结果，对比观察模型是否学到
# with torch.no_grad():
#     # 再来预测 训练集第一条数据
#     precheck_sent = prepare_sequence(training_data[0][0], word_to_ix)
#     a = model(precheck_sent)
#     print('预测结果：', a)
#     print('实际结果：', precheck_tags)
#     a = pd.Series(a)
#
