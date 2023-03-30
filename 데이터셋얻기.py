import time

from selenium.webdriver import Chrome
import chromedriver_autoinstaller
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By

import requests
import os
chromedriver_autoinstaller.install('./')

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

driver = Chrome(options=chrome_options)

'''
KO, kr, 호두, 0
JA, jp, 胡桃, 1
EN, en, Hu Tao, 2
CHS, cn, 胡桃, 3
'''

country_code_1 = 'KO'
country_code_2 = 'kr'
speaker_name = '페이몬'
charactername = 'paimon'
sitecode = 'paimon'

def character_voice_download():
    driver.get(f'https://genshin.honeyhunterworld.com/{sitecode}/?lang={country_code_1}')

    metadata = open(f'./{charactername}/metadata.txt', 'a', encoding='utf-8')

    # 높이 얻기
    # 스크롤을 해야 값을 얻는다.
    height = driver.execute_script("return document.body.scrollHeight")
    while True:
        for i in range(0, height, 500):
            driver.execute_script(f"window.scrollTo(0, {i})")
            time.sleep(0.05)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if height == new_height:
            break
        else:
            height = driver.execute_script("return document.body.scrollHeight")

    # 띄어 쓰기 => . 처리 하기
    g = driver.find_elements(By.CLASS_NAME, "genshin_table.quotes_table")
    tb = g[1].find_element(By.TAG_NAME, "tbody")
    trs = tb.find_elements(By.TAG_NAME, "tr")
    for i in range(len(trs)):
        try:
            tt = trs[i].find_elements(By.TAG_NAME, "span")
            transcript = tt[1].text

            # character script
            transcript = transcript.replace("\n", "")

            t = trs[i].find_elements(By.TAG_NAME, "div")
            voice_code = t[1].get_attribute("id")

            # voice download
            audio_url = 'https://genshin.honeyhunterworld.com/audio/quotes/' + f"{charactername}" + "/" + voice_code + f'_{country_code_2}.wav'
            r = requests.get(
                url=audio_url,
                headers={
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
                    'referer': f'https://genshin.honeyhunterworld.com/{sitecode}/?lang={country_code_1}'
                }
            )
            tmp_wav_path = f'./{charactername}/tmp_wavs/' + voice_code + f'_{country_code_2}.wav'
            wav_path = f'./{charactername}/wavs/{country_code_2}/' + voice_code + f'_{country_code_2}.wav'
            open(tmp_wav_path, 'wb').write(r.content)

            metadata.writelines(f'{wav_path}|[{country_code_1}]{transcript}[{country_code_1}]\n')

            # output
            print(tmp_wav_path, transcript)
        except:
            continue
            # print("err")
            # tt = trs[i].find_elements(By.TAG_NAME, "span")
            # print(len(tt))
            # #print(trs[i].text)
            # print("###")


def legendary_mission_download():
    #사이트 주소 입력이 필요함
    story_urls = [
        f'https://genshin.honeyhunterworld.com/q_3000/?lang={country_code_1}',
    ]

    #story_urls = []

    # 11009 ~ 11015 : 중간장 제1막


    # # 2000 ~ 2021 까지 이나즈마 스토리
    # for i in range(2000, 2022, 1):
    #     story_urls.append(f'https://genshin.honeyhunterworld.com/q_'+str(i)+f'/?lang={country_code_1}',)

    # # 8000 ~ 데인슬레이프
    # for i in range(8000, 8008, 1):
    #     story_urls.append(f'https://genshin.honeyhunterworld.com/q_'+str(i)+f'/?lang={country_code_1}',)


    #3000 ~ 3028 까지 수메르 스토리 3029 ~ 3032 중간장 제3막 뒤집힌 기원 // 3015 없어서 빼야함
    for i in range(3001, 3015, 1):
        story_urls.append(f'https://genshin.honeyhunterworld.com/q_'+str(i)+f'/?lang={country_code_1}',)

    for i in range(3016, 3033, 1):
        story_urls.append(f'https://genshin.honeyhunterworld.com/q_'+str(i)+f'/?lang={country_code_1}',)
    #
    #
    # # # 12000 ~ 12042 이나즈마의 캐릭터 전설퀘스트
    # # for i in range(12000, 12043, 1):
    # #     story_urls.append(f'https://genshin.honeyhunterworld.com/q_'+str(i)+f'/?lang={country_code_1}',)
    #
    # 13000 ~ 13022 수메르의 캐릭터 전설퀘스트
    for i in range(13000, 13023, 1):
        story_urls.append(f'https://genshin.honeyhunterworld.com/q_'+str(i)+f'/?lang={country_code_1}',)

    metadata = open(f'./{charactername}/metadata.txt', 'a', encoding='utf-8')

    # 페이지 반복문 페이지 개수 마다 반복 하게 된다.
    for aa in range(len(story_urls)):
        driver.get(story_urls[aa])
        driver.implicitly_wait(2)

        # 높이 얻기
        # 스크롤을 해야 값을 얻는다.
        height = driver.execute_script("return document.body.scrollHeight")
        while True:
            for i in range(0, height, 400):
                driver.execute_script(f"window.scrollTo(0, {i})")
                time.sleep(0.05)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if height == new_height:
                break
            else:
                height = driver.execute_script("return document.body.scrollHeight")


        #voice가 있는 곳
        s = driver.find_elements(By.CLASS_NAME, "dialog_cont")

        #voice 가 구간마다 잘려 있는데 잘려 있는 것 만큼 크기 얻음
        for i in range(len(s)):
            g = s[i].find_elements(By.TAG_NAME, "div")
            for j in range(len(g)):
                try:
                    c = g[j].find_elements(By.TAG_NAME, "b")
                    # speakername 일 때
                    if len(c) == 1 and c[0].text == speaker_name:
                        voice_code = g[j].get_attribute("id")

                        # character script
                        transcript = g[j].text.split(f"{speaker_name}" + " : ")[1]

                        # voice download
                        audio_url = 'https://genshin.honeyhunterworld.com/audio/dialogue/wav/' + voice_code + f'_{country_code_2}.ogg'
                        r = requests.get(
                            url = audio_url,
                            headers={
                                'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
                                'referer' : f'https://genshin.honeyhunterworld.com/{sitecode}/?lang={country_code_1}'
                            }
                        )
                        tmp_wav_path = f'./{charactername}/tmp_wavs/'+voice_code+f'_{country_code_2}.ogg'
                        wav_path = f'./{charactername}/wavs/{country_code_2}/'+voice_code+f'_{country_code_2}.ogg'
                        open(tmp_wav_path, 'wb').write(r.content)

                        metadata.writelines(f'{wav_path}|[{country_code_1}]{transcript}[{country_code_1}]\n')
                        #print("write")
                        # output
                        print(tmp_wav_path, transcript)
                except:
                    continue


if __name__ == "__main__":
    # 파일 클리어
    os.system(f'del /s /q {charactername}\\tmp_wavs\\*.wav')
    # 캐릭터 대사
    #character_voice_download()
    # 임무 대사
    legendary_mission_download()