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


def get_text(text, hps):
    text = re.sub('[\s+]', ' ', text)
    text_norm = text_to_sequence(text, hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = torch.LongTensor(text_norm)
    return text_norm


# Inference
hps = utils.get_hparams_from_file("./configs/aru.json")
net_g = SynthesizerTrn(
    len(symbols),
    hps.data.filter_length // 2 + 1,
    hps.train.segment_size // hps.data.hop_length,
    n_speakers=hps.data.n_speakers,
    **hps.model).cuda()
_ = net_g.eval()

_ = utils.load_checkpoint(f"../vits_model/aru/G_{sys.argv[1]}.pth", net_g, None)

# 히키가야 하치만 명언 모음
# https://meigenkakugen.net/比企谷八幡/
text_list = [
    '人生には一度や二度、孤独と向き合うべきときってもんがある。いや、なきゃいけない。始終誰かと一緒にいていつもいつでも傍に人がいるなんて、そっちのほうがよほど異常で気持ちが悪い。孤独であるときにしか学べない、感じられないことがきっと存在するはずなのだ。',
    '仕事ってのはやめることはあっても　終わることはねぇんだよ',
    '孤高であることは強い。繋がりを持たないということは守るべきものを持たないということだ。守るべきもの、それは言い換えれば弱点にほかならない。かのギリシャの英雄アキレスにも、最強の僧兵武蔵坊弁慶にも弱点があったからこそ敗れた。きっと彼らは弱点さえなければ歴史に勝利者として名を刻んだはずである。したがって弱点のない、守るべきものを持たない、人との繋がりを持たない者こそは最強。つまり、俺、最強ということである。',
    '舐めんな、監視されようがサボるときはちゃんとサボる。それが俺だ。',
    'いってみれば独りぼっちとは思考の達人だ。人は考える葦であるというように、気づけば何事か思案している。なかでも独りぼっちは他人に思考のリソースを割く必要がないぶんその思索はより深いものになる。したがって我々ぼっちは余人とは違う思考回路を持つに至り、時に常人の枠を越えた発想が飛び出たりするのだ。',
    '青春とは嘘であり、悪である。',
    'まあ、あれだ。強い獣は群れたりしない。一匹狼という言葉を知らないのかよ。猫は可愛いし、狼はかっこいい。つまり、ぼっちは可愛いし、かっこいい。',
    'リア充はリア充としての行動を求められ、ぼっちはぼっちであることを義務づけられ、オタクはオタクらしく振る舞うことを強要される。カーストが高い者が下に理解を示すことは寛大や教養の深さとして認められるが、その逆は許されない。',
    '「特殊で何が悪い。英語でいえばスペシャルだ。なんか優れてるっぽく聞こえるだろ」',
    'お互いに期待しない、期待されないというのは結構楽でいい関係なんじゃないかと俺は思う。まぁ、ほら。パンドラちゃんが持ってた箱の中にはあらゆる災厄と一緒に希望が詰まってたっていうじゃんか。あれだよあれ。希望も災厄ってことだ。',
    '本当に何故かわからないのだが、俺たちスクールカーストが低い連中は上位カーストに出会うと萎縮しちまうんだよな。廊下とかで絶対道を譲っちゃうし、話しかけられるとまず八割がた噛む。それでさらに嫉妬や憎悪が高まるかというとそうでもなく、名前なんて覚えてもらっていた日にゃ逆にちょっと嬉しかったりするのだ。',
    '実際、殴ってやろうかと思うほど本気で腹立たしいときだってあるし、そういうときは自分にまったく似ていないと感じる。けれど、ふとした瞬間にまったく同じ行動をとっていたりして愛着というか愛情というか、そんな感情が湧いてきたりもする。はっきりいってよくわからん距離感にいるのが兄弟というやつだろう。',
    'みんな仲良くという言葉自体が元凶なのに。あれは呪いじみたお題目なのに。あれは強制するための言葉なのだ。ギアスなのだ。',
    '本来、ぼっちというのは誰にも迷惑をかけない存在だ。人と関わらないことによってダメージを与えない、究極的にエコでロハスでクリーンな生き物なのだ。',
    '人間関係に悩みを抱えるなら、それ自体を壊してしまえば悩むことはなくなる。負の連鎖ならもとから断ち切る。それでいいのだ。逃げちゃダメだなんて強者の考え方でしかない。それを強いる世界こそが間違っている。',
    'おいでおいでと誘われた以上、ここで行かないわけにもいくまい。いやもうほんと全然行く気とかないし、紳士であるところの俺がみだりに水着姿の女子に近づいたりするわけないんだけど、呼ばれちゃったらしょうがないし、あ、そうそう俺顔洗わないといけなかったんだよね。ちっ、しょうがねぇから超ダッシュで行くよ！！',
    'ぼっちは人の名前を覚えるのが意外に得意なのである。いつ話しかけられるのかなードキドキと思ってしまうからだろう。',
    '確かに、親が相手だからこそ言えないことというのはある。例えばエロ本のあれこれとか、恋愛がらみのことなんて絶対に親に言いたくないことだ。あと、学校行ったら俺の机がベランダにあったとか下駄箱にゴミ入れられてたとか、ラブレターもらってウキウキしてたら同級生の悪戯だったとか、そういうのって言えないよな。',
    '畢竟、人とうまくやるという行為は、自分を騙し、相手を騙し、相手も騙されることを承諾し、自分も相手に騙されることを承認する、その循環連鎖でしかないのだ。',
    '馬鹿な！俺は断じてシスコンなどではない。むしろ、妹としてではなく、一人の女性として……ああ、もちろん冗談です、やめろ、武装すんな',
    'あれだよな、ゲームしてるときとか超しゃべるよな。「かーそれはねーわー」とか「ほう、そう来たか」とか「凛子、好きだよ」とか。おかげで母親に「友達でも来てたの？」とか言われて「え、で、電話……」とかおろおろしながら答える羽目になるんだ。もう家でラブプラスはできない。',
    'たぶんこの光景を忘れない。忘れられない。あの眩しいステージにはいないけれど。飛び跳ねるアリーナには混じれないけれど。一人で、一番後ろで、ただ眺めているだけだけれど。でも、きっと忘れない。',
    'おいおい、そんなんじゃ一級拒絶鑑定士の俺の目は誤魔化せないぜ。女子が本当に拒絶するときはもっと冷たい目をしてほとんど無表情で「あの、本当にやめてくれる?」って言うんだぜ。心臓凍えるかと思う程怖いし、死にたくなる。',
    'ばしゃばしゃと何度か顔を洗っていると不意に聞き慣れた声が聞こえた。「あら、川に向かって土下座？」「んなわけねーだろ。あっちの方向に聖地があって一日五回の礼拝をだな……」'
    '青春のまっただ中にいる彼らは、敗北すら素敵な思い出に変えて見せる。いざこざももめ事も悩める青春のひと時と化して見せる。',
    '彼らの持つ、青春フィルターを通してみれば世界は変わるのだ。だとすれば、俺のこの青春時代もラブコメ色に染まるのかもしれない。間違ってなどいないのかもしれない。なら、俺が今いるこの場所もいつか輝いて見えるのだろうか。死んだ魚のように腐った目でも。',
    'おそらく、非モテぼっちほどのリアリストはいないだろう。非モテ三原則【（希望を）持たず、（心の隙を）作らず、（甘い話を）持ち込ませず】を心に刻んで生きているのだ。',
    'ていうか、これ当たってる！あ、離れた！また当たった！さっきからおっぱいがヒット・アンド・アウェイ！やべー、このおっぱいモハメド・アリだよ……。',
    'ぼっちには「バカをやる」という行為がなかなか理解しがたい。ノリが悪いと言われる所以だ。別に恥ずかしいわけでないのだ。ただいろんなことを考えてしまうから簡単には動けない。人の迷惑ではないだろうかとか危なくはないだろうかとか自分が入ることで今の楽しい空気が乱れはしないだろうかとか。',
    '働かなきゃいけないうえに人間関係まで気を遣うとか罰ゲームかよ。人間関係手当ちゃんとついてんの？追加料金発生しないとおかしいだろそれ。やっぱり俺は働いてはいけないんだと思いました。',
    'なぜ自分の感じている楽しさを、自分の正しさを、己一人で証明できないのか。',
    'わかるかよ、馬鹿みたいに暑い夏の最中も指先ちぎれそうなくらい寒い雪の日もたった一人で自転車漕いで登下校するつらさが。お前らが暑いだの寒いだのありえないだの言い交して騙しごまかし紛らわしてきたのを俺は一人で切り抜けてきたんだぜ。 　わかってたまるかよ。テストのたびに試験範囲を誰に確認するでもなく、黙々と勉強して、自分の出した結果に真正面から向き合う恐ろしさが。お前らが揃って答え合わせして点数見せ合って馬鹿だのガリ勉だの言い合って現実から逃げ合ってるのに俺は真っ向から受け止めてるんだぜ。',
    '俺はな、こういう、男女で脱衣とか、罰ゲームで盛り上がるとか、そういう、頭の悪い大学生の飲み会みたいなノリが、いっちばん、嫌いなんだよ！いや、むしろ憎んですらいる！',
    '誕生日。それは自分自身が生まれた日であると同時に、新たなトラウマが生まれる日でもある。例えば俺だけが呼ばれなかった誕生日会、俺のためかと感動してたら俺と同じ日に生まれたクラスメイトのために歌われていたバースデーソング、俺の名前が間違っている誕生日ケーキ……。ていうか、最後、俺の母ちゃん何やってんだよ。息子の名前間違えんなよ。',
    '俺も将来、嫁さんに養ってもらうときは充分にいたわってあげよう。それがヒモを越えた超ヒモというやつである。',
    '服選んでるときに話しかけるのほんとやめてほしい。服屋の店員さんはぼっちが放つ「話しかけんなオーラ」を感じ取るスキルを身につけたほうがいい。そのほうがたぶん売り上げ上がるぞ。',
    '実家楽すぎて最高だしな。限界まで働かない、それが俺のジャスティス',
    'みんなって誰だよ……。かーちゃんに『みんな持ってるよぉ！』って物ねだるときに言うみんなかよ……。誰だよそいつら……。友達いないからそんな言い訳使えたことねぇよ……',
    '誰かの顔色を窺って、ご機嫌とって、連絡を欠かさず、話を合わせて、それでようやく繋ぎとめられる友情など、そんな物は友情じゃない。その煩わしい過程を青春と呼ぶのなら俺はそんな物いらない。ぬるいコミュニティで楽しそうに振る舞うなど自己満足となんら変わらない。そんなものは欺瞞だ。唾棄すべき悪だ。',
    'あと、誘われたとき、すぐ「適当に連絡くれ」って言う奴はだいたい次から誘われなくなる。これ豆知識な。ソースは俺。',
]


text_list = [
    '領域展開…無量恐妻',
    '先生、ちょっとお時間いただけますか？',
    '先生…一緒にライディングしに行こう。',
    '行ってきてからは一緒に… お風呂に入ろう。',
    '先生…どこ行くの…？ 今日寝て行くんじゃなかったの？拒否権はないよ。 …こっちおいで。',
    'お風呂にする…？ご飯にする…？それとも……あ…た……し？',
    '誰かに必要とされていることそれはあなたが誰かの希望であることだ',
    'しばらく焚火の跡をかき回してみたが、残念ながら灰の中には食べられそうなものは残っていなかった。',
    '先生…今日、隣で一緒に寝てもいい……？',
    '先生…私……下が…むずむずする……',
    '俺は南の洞窟に着くと、活発化している魔物を避けながら洞窟の最深部に進んだ。',
    '身体強化で反射神経や足の筋肉を強化しているから、魔物を避けるなんて楽勝。一々相手していたらキリがない。',
    'しかも村長の話では、村に被害を与えている訳でもない……',
    '聖女のみが使える聖魔法属性と膨大な魔力量を持って生まれたことで、二歳の頃に神殿へと引き取られた。',
    '今俺の目の前にはゴブリンの集落……',
    '洞窟の最深部は天井に穴が開いており、たくさんの草花が生えている美しい場所だ。',
    'ドラゴンは空を飛べるので、天井の穴から入ってきたんだろう。この場所を傷を癒すポイントにするなんて、結構おしゃれなドラゴンだ。',
]


model_step = sys.argv[1]
speed = 1
for idx, text in enumerate(text_list):
    stn_tst = get_text(text, hps)
    with torch.no_grad():
        x_tst = stn_tst.cuda().unsqueeze(0)
        x_tst_lengths = torch.LongTensor([stn_tst.size(0)]).cuda()
        audio = net_g.infer(x_tst, x_tst_lengths, noise_scale=.667, noise_scale_w=0.8, length_scale=1/speed)[0][0,0].data.cpu().float().numpy()
    write(f'/content/drive/MyDrive/vits_output/aru/aru{model_step}_{idx}.wav', hps.data.sampling_rate, audio)
    print(f'aru_{model_step}_{idx} 음성 합성 완료')