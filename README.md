## vits

출처 : https://github.com/CjangCjengh/vits

## 설명

한글 TTS를 만들기 위해 default 세팅을 해둠.

## 하는 법
- Colab가서 ipynb를 연다.
```sh
!git clone https://github.com/kkt3343/vits
```
- filelists/wavs 안에 보이스를 넣는다.
```sh
!pip install -r requirements.txt
```

```sh
cd monotonic_align
python setup.py build_ext --inplace
cd ..
```
