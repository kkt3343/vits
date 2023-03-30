import matplotlib.pyplot as plt
import IPython.display as ipd

import os
import sys
import re
import json
import math
import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.data import DataLoader

import commons
import utils
from data_utils import TextAudioLoader, TextAudioCollate, TextAudioSpeakerLoader, TextAudioSpeakerCollate
from models import SynthesizerTrn
from text.symbols import symbols
from text import text_to_sequence

from scipy.io.wavfile import write

model_step = sys.argv[1]

def get_text(text, hps):
    text = re.sub('[\s+]', ' ', text)
    text_norm = text_to_sequence(text, hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = torch.LongTensor(text_norm)
    return text_norm


# Inference
hps = utils.get_hparams_from_file("./configs/yuuka2.json")
net_g = SynthesizerTrn(
    len(symbols),
    hps.data.filter_length // 2 + 1,
    hps.train.segment_size // hps.data.hop_length,
    n_speakers=hps.data.n_speakers,
    **hps.model)
_ = net_g.eval()

_ = utils.load_checkpoint(f"/content/drive/MyDrive/vits_model/yuuka2/G_{model_step}.pth", net_g, None)



# text = '誰かに必要とされていることそれはあなたが誰かの希望であることだ'
text = 'お風呂にする？ご飯にする？それとも……あ..た..し？'

# text = '''
# ……ユイトの義理の父はエリートだ。彼は息子であるユイトを引き取り、その知識を余すところなく教えてくれる。おかげで車両や大型機械の操縦にメンテナンスもこなし、改造だってできるほどに技術に通じている。

# 　この村に来るたび大人たちに歓迎されているのは、愛着を持ってほしいという意味もあるだろうが、優秀な技術者に離れてほしくないという下心も含まれているはずだ。

# 　そんな上の世代に厚遇されるユイトが、若者揃いの自警団は気に入らないのだ。



# 　……それは仕方ない。

# 　ただ、だからといって人目につかないところで暴力をふるったりするのはやめてほしいが。
# '''

# text = '''
# よぎ　する　あんず　せ　げまん　がじょだ　ずしご　さいだど　どぅ　びょん　ずせよ~！
# '''


speed = 1
# speed = 0.85 # Takanashi Hoshino
for idx in range(0, 20):
    sid = torch.LongTensor([idx])
    stn_tst = get_text(text, hps)
    with torch.no_grad():
        x_tst = stn_tst.unsqueeze(0)
        x_tst_lengths = torch.LongTensor([stn_tst.size(0)])
        audio = net_g.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=.667, noise_scale_w=0.8, length_scale=1/speed)[0][0,0].data.cpu().float().numpy()
    write(f'/content/drive/MyDrive/vits_output/yuuka2/yuuka2_{model_step}.wav', hps.data.sampling_rate, audio)
    print(f'음성 합성 완료')
    break
