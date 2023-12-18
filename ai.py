import httpx
import textwrap
import time

sessionKey = input("Please enter your KakaoTalk session key: ")

host = "https://talk-pilsner.kakao.com"

# path
get_user = "/a1-talk/talk/user"
join = "/a1-talk/talk/user/join"
setting = "/talk/ai/settings"
get_tone = "/a1-talk/talk/settings"

change_tone_path = "/a1-talk/talk/tone"

header = {
    'Authorization': sessionKey,
    'Talk-Agent': 'android/10.4.5',
    'Talk-Language': 'ko',
    'User-Agent': 'okhttp/4.10.0'
}

class Translation:
    def __init__(self, ko: str, en: str, ja: str):
        self.ko = ko
        self.en = en
        self.ja = ja
        
    def __str__(self):
        return f'Translation(ko={self.ko}, en={self.en}, ja={self.ja})'

class ToneModel:
    def __init__(self, type: str, name: str, translations: Translation, logMeta: str):
        self.type = type
        self.name = name
        self.translations = translations
        self.logMeta = logMeta

    def __str__(self):
        return f'ToneModel(type={self.type}, name={self.name}, translations={self.translations}, logMeta={self.logMeta})'


def is_joined():
    user_res = httpx.get(host + get_user, headers=header)
    if user_res.json()['userStatus'] == 'NONE':
        return False
    elif user_res.json()['userStatus'] == 'JOINED':
        return True
    else:
        raise Exception('Unknown user status')
    

def join_user():
    join_res = httpx.post(host + join, headers=header)
    if join_res.json()['code'] == 0:
        return True
    else:
        raise Exception('error in joining user')
    

def active_ai():
    setting_res = httpx.post(host + setting, headers=header, json={'active': True})
    if setting_res.json()['status'] == 0:
        return True
    else:
        raise Exception('error in activating AI')
    
    
def get_tone_list():
    tone_res = httpx.get(host + get_tone, headers=header)
    tone_json = tone_res.json()
    tone_list = []
    for tone in tone_json['toneTypes']:
        translations = Translation(tone['translations']['ko'], tone['translations']['en'], tone['translations']['ja'])
        tone_model = ToneModel(tone['type'], tone['name'], translations, tone['logMeta'])
        tone_list.append(tone_model)
    return tone_list


def change_tone(tone_type: str, message: str) -> str:
    change_res = httpx.post(host + change_tone_path, headers=header, json={'type': tone_type, 'message': message})
    
    if change_res.json()['code'] == 0:
        return change_res.json()['result']
    else:
        raise Exception('error in changing tone')


print('Checking if user is joined...')
if not is_joined():
    print('User is not joined, joining user...')
    join_user()
    print('User joined')
    
    
print('Activating AI...')
active_ai()
print('AI activated')


print('Getting tone list...')
tone_list = get_tone_list()
print('Tone list got')


while True:
    print(
        textwrap.dedent(
            '''
            What do you want to do?
            
            1. chnage tone
            2. exit
            '''
        )
    )

    mod = input('Enter your choice: ')
    if mod == '1':
        original_tone = input('What do you want to change from: ')
        
        for i, tone in enumerate(tone_list):
            print(f"{i+1}. {tone.translations.ko} ({tone.translations.en})")
            
        tone_num = int(input('Enter the number of tone you want to change to: '))
        
        if tone_num > len(tone_list):
            print('Invalid tone number')
            continue
        
        tone = tone_list[tone_num - 1]
        
        print(f'Changing tone from {original_tone} to {tone.translations.ko} ({tone.translations.en})')
        
        changed = change_tone(tone.type, original_tone)
        
        print(f'Tone changed to {changed}')
        
        time.sleep(2)
    elif mod == '2':
        print('Exiting...')
        break
    else:
        print('Invalid choice')
        
        time.sleep(2)
