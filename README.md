## vits

출처 : https://github.com/CjangCjengh/vits

출처 : https://github.com/jaywalnut310/vits

## 설명

한글 TTS를 만들기 위해 default 세팅을 해둠.

## 하는 법
- Colab가서 ipynb를 연다.
- 런타임 GPU 설정 한다.
- filelists/wavs 안에 보이스를 넣는다.
- 아래 코드를 차례대로 실행한다.
```sh
!git clone https://github.com/kkt3343/vits
```
```sh
%cd vits
!pip install -r requirements.txt
```

```sh
%cd content/vits #만약 재시작을 했다면
%cd monotonic_align
!python setup.py build_ext --inplace
%cd ..
```

## 학습
```sh
~~!python train.py -c configs/nahida.json -m nahida~~
```

### 메모
```sh
우선 KSS로 먼저 학습을 실시하고 보이스를 바꿀 예정
```

