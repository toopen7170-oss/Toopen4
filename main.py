# main.py (간단/안정 버전) — 게임/오답노트/단어장/랭킹/로그인 포함
import os, json, random, hashlib
from kivy.lang import Builder
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import Snackbar

try:
    from gtts import gTTS
    from kivy.core.audio import SoundLoader
    TTS_READY=True
except Exception:
    TTS_READY=False

APP_DIR=os.path.dirname(os.path.abspath(__file__))
STORE=os.path.join(APP_DIR,"store"); os.makedirs(STORE,exist_ok=True)
AUDIO=os.path.join(STORE,"audio"); os.makedirs(AUDIO,exist_ok=True)
DB_PATH=os.path.join(STORE,"db.json")
WORDS_PATH=os.path.join(APP_DIR,"words.json")

def sha(s): import hashlib; return hashlib.sha256(s.encode("utf-8")).hexdigest()
def load_json(p, d):
    if not os.path.exists(p):
        with open(p,"w",encoding="utf-8") as f: json.dump(d,f,ensure_ascii=False,indent=2)
        return d
    return json.load(open(p,"r",encoding="utf-8"))
def save_json(p, d):
    with open(p,"w",encoding="utf-8") as f: json.dump(d,f,ensure_ascii=False,indent=2)

DB=load_json(DB_PATH, {"users":{}, "session":{"user":None}, "scores":{}, "settings":{"timer":3,"tts":True}, "hall_of_fame":[]})
WORDS=load_json(WORDS_PATH, {"meta":{"languages":["en","ko","vi","zh","ja","es","th"]},"items":[]})

def speak(text, lang="en"):
    if not DB["settings"].get("tts",True) or not TTS_READY or not text: return
    path=os.path.join(AUDIO, f"{lang}_{sha(text)[:16]}.mp3")
    if not os.path.exists(path):
        try:
            gTTS(text=text, lang="zh-CN" if lang=="zh" else lang).save(path)
        except Exception:
            return
    s=SoundLoader.load(path)
    if s: s.play()

KV = '''
<Home@MDScreen>:
    name: "home"
    MDLabel:
        text: "2.0 외국어 단어 맞추기"
        halign: "center"
        pos_hint: {"center_x":.5,"center_y":.92}
        font_style: "H5"
    BoxLayout:
        orientation: "vertical"
        spacing: dp(10)
        size_hint: .9,.65
        pos_hint: {"center_x":.5,"center_y":.5}
        MDRectangleFlatButton:
            text: "로그인/회원가입"
            on_release: app.goto("auth")
        MDRectangleFlatButton:
            text: "4칸 (초급)"
            on_release: app.start_game(4)
        MDRectangleFlatButton:
            text: "6칸 (중급)"
            on_release: app.start_game(6)
        MDRectangleFlatButton:
            text: "9칸 (고급)"
            on_release: app.start_game(9)
        MDRectangleFlatButton:
            text: "16칸 (마스터)"
            on_release: app.start_game(16)
        MDRectangleFlatButton:
            text: "오답노트"
            on_release: app.goto("wrong")
        MDRectangleFlatButton:
            text: "단어장"
            on_release: app.goto("vocab")
        MDRectangleFlatButton:
            text: "명예의 전당"
            on_release: app.goto("hof")

<Auth@MDScreen>:
    name: "auth"
    BoxLayout:
        orientation: "vertical"
        padding: dp(16)
        spacing: dp(8)
        MDTextField:
            id: uid
            hint_text: "아이디"
        MDTextField:
            id: pw
            hint_text: "비밀번호"
            password: True
        BoxLayout:
            size_hint_y: None
            height: dp(48)
            spacing: dp(8)
            MDRectangleFlatButton:
                text: "로그인"
                on_release: app.login(uid.text, pw.text)
            MDRectangleFlatButton:
                text: "회원가입"
                on_release: app.register(uid.text, pw.text)
        MDRectangleFlatButton:
            text: "뒤로"
            on_release: app.goto("home")

<Game@MDScreen>:
    name: "game"
    BoxLayout:
        orientation: "vertical"
        padding: dp(8)
        spacing: dp(6)
        MDLabel:
            id: status
            text: "정답 0 | 오답 0 | 하트 ♥♥♥♥♥ | 타이머 --"
            halign: "center"
            size_hint_y: None
            height: dp(28)
        GridLayout:
            id: grid
            cols: 2
            spacing: dp(8)
            padding: dp(8)
        BoxLayout:
            size_hint_y: None
            height: dp(48)
            spacing: dp(8)
            MDRectangleFlatButton:
                text: "일시정지"
                on_release: app.pause_timer()
            MDRectangleFlatButton:
                text: "다시시작"
                on_release: app.resume_timer()
            MDRectangleFlatButton:
                text: "종료"
                on_release: app.goto("home")

<Wrong@MDScreen>:
    name: "wrong"
    BoxLayout:
        orientation: "vertical"
        padding: dp(8)
        spacing: dp(8)
        MDLabel:
            id: wtitle
            text: "오답노트 모드"
            halign: "center"
            size_hint_y: None
            height: dp(28)
        BoxLayout:
            id: warea

<Vocab@MDScreen>:
    name: "vocab"
    BoxLayout:
        orientation: "vertical"
        padding: dp(8)
        spacing: dp(6)
        MDLabel:
            id: v1
            text: "단어 / 뜻"
            halign: "center"
            font_style: "H5"
        MDLabel:
            id: v2
            text: "예문과 해석"
            halign: "center"
        BoxLayout:
            size_hint_y: None
            height: dp(48)
            spacing: dp(8)
            MDRectangleFlatButton:
                text: "시작"
                on_release: app.vocab_start()
            MDRectangleFlatButton:
                text: "정지"
                on_release: app.vocab_stop()
            MDRectangleFlatButton:
                text: "A-B 반복"
                on_release: app.vocab_ab()
            MDRectangleFlatButton:
                text: "전체 반복"
                on_release: app.vocab_all()
        Slider:
            id: spd
            min: 1
            max: 3
            step: 1
            value: 2

<HoF@MDScreen>:
    name: "hof"
    BoxLayout:
        orientation: "vertical"
        padding: dp(8)
        spacing: dp(6)
        MDLabel:
            text: "명예의 전당 Top 7"
            halign: "center"
            size_hint_y: None
            height: dp(32)
        BoxLayout:
            id: hoflist
            orientation: "vertical"
'''

def toast(m): Snackbar(text=m, duration=1.2).open()

class AppX(MDApp):
    user=""
    hearts=5
    timer_left=3
    t_running=False

    def build(self):
        self.theme_cls.primary_palette="Blue"
        return Builder.load_string(KV)

    def goto(self, name): self.root.current=name

    def ensure_user(self,u):
        if u not in DB["scores"]:
            DB["scores"][u]={"total":0,"correct":0,"wrong":0,"hearts":5,"wrong_notes":{}}
        self.user=u; self.hearts=DB["scores"][u]["hearts"]; save_json(DB_PATH,DB)

    def register(self, u, p):
        u=u.strip(); p=p.strip()
        if not u or not p: toast("아이디/비번 입력"); return
        if u in DB["users"]: toast("이미 존재"); return
        DB["users"][u]=sha(p); save_json(DB_PATH,DB); self.ensure_user(u); toast("회원가입 완료"); self.goto("home")

    def login(self, u, p):
        u=u.strip(); p=p.strip()
        if u in DB["users"] and DB["users"][u]==sha(p):
            DB["session"]["user"]=u; save_json(DB_PATH,DB); self.ensure_user(u); toast("로그인 성공"); self.goto("home")
        else: toast("아이디/비번 오류")

    def start_game(self, n):
        if not DB["session"]["user"]: toast("로그인 필요"); return
        self.goto("game"); self.grid_n=n; self.next_round()

    def update_status(self):
        s=DB["scores"][self.user]; h="♥"*self.hearts+ "♡"*(5-self.hearts)
        self.root.get_screen("game").ids.status.text=f"정답 {s['correct']} | 오답 {s['wrong']} | 하트 {h} | 타이머 {self.timer_left}s"

    def next_round(self):
        items=WORDS.get("items",[])
        if len(items)<max(4,self.grid_n): toast("단어가 부족합니다. CSV 추가 후 재시도"); return
        self.timer_left=DB["settings"]["timer"]; self.t_running=True
        self.answer=random.choice(items); speak(self.answer["en"],"en")
        k=self.grid_n
        others=[w for w in items if w["id"]!=self.answer["id"]]; random.shuffle(others)
        cand=others[:k-1]+[self.answer]; random.shuffle(cand)
        grid=self.root.get_screen("game").ids.grid; grid.clear_widgets()
        grid.cols=2 if k==4 else 3 if k in (6,9) else 4
        for it in cand:
            bt=MDRectangleFlatButton(text=f"{it['en']} / {it['ko']}", on_release=lambda x, it=it: self.pick(it))
            grid.add_widget(bt)
        Clock.unschedule(self._tick); Clock.schedule_interval(self._tick,1); self.update_status()

    def pick(self, it):
        speak(it["en"],"en")
        s=DB["scores"][self.user]
        if it["id"]==self.answer["id"]:
            speak("O","ko"); s["correct"]+=1; s["total"]+=1
            if s["correct"]%10==0 and self.hearts<5: self.hearts+=1
        else:
            speak("외때려","ko"); s["wrong"]+=1; s["total"]+=1
            self.hearts=max(0,self.hearts-1)
            wn=s["wrong_notes"]; wid=self.answer["id"]; wn[wid]=wn.get(wid,0)+1
            if self.hearts==0: toast("하트 소진 → 재도전"); self.hearts=5
        DB["scores"][self.user]["hearts"]=self.hearts; save_json(DB_PATH,DB); self.next_round()

    def _tick(self, dt):
        if not self.t_running: return
        self.timer_left-=1
        if self.timer_left<=0:
            s=DB["scores"][self.user]; s["wrong"]+=1; s["total"]+=1
            self.hearts=max(0,self.hearts-1); DB["scores"][self.user]["hearts"]=self.hearts; save_json(DB_PATH,DB)
            if self.hearts==0: toast("시간초과 → 재도전"); self.hearts=5
            self.next_round()
        self.update_status()

    def pause_timer(self): self.t_running=False
    def resume_timer(self): self.t_running=True

    def render_wrong(self):
        area=self.root.get_screen("wrong").ids.warea; area.clear_widgets()
        if not self.user: area.add_widget(MDLabel(text="로그인 후 이용", halign="center")); return
        wn=DB["scores"][self.user].get("wrong_notes",{})
        if not wn: area.add_widget(MDLabel(text="오답 없음", halign="center")); return
        ids=list(wn.keys()); choose=ids[:4] if len(ids)<4 else random.sample(ids,4)
        items=[next(i for i in WORDS["items"] if i["id"]==x) for x in choose]
        self.w_answer=random.choice(items); speak(self.w_answer["en"],"en")
        cand=items[:]
        while len(cand)<4:
            extra=random.choice([i for i in WORDS["items"] if i["id"] not in choose]); cand.append(extra)
        random.shuffle(cand)
        for it in cand[:4]:
            area.add_widget(MDRectangleFlatButton(text=f"{it['en']} / {it['ko']}", on_release=lambda x, it=it: self.w_pick(it)))

    def w_pick(self, it):
        wn=DB["scores"][self.user]["wrong_notes"]
        if it["id"]==self.w_answer["id"]:
            speak("O","ko"); wid=it["id"]; wn[wid]=max(0, wn.get(wid,1)-1); 
            if wn[wid]==0: wn.pop(wid,None)
        else:
            speak("외때려","ko"); wid=self.w_answer["id"]; wn[wid]=wn.get(wid,0)+1
        save_json(DB_PATH,DB); self.render_wrong()

    v_idx=0; v_run=False; ab_a=None; ab_b=None; repeat_all=False
    def render_vocab(self):
        v1=self.root.get_screen("vocab").ids.v1; v2=self.root.get_screen("vocab").ids.v2
        if not WORDS["items"]: v1.text="단어 없음"; v2.text=""; return
        w=WORDS["items"][self.v_idx%len(WORDS["items"])]; v1.text=f"{w['en']} / {w['ko']}"
        v2.text=f"예문: {w['en']} is useful. | 해석: {w['ko']}는 유용하다."
        speak(w['en'],"en"); Clock.schedule_once(lambda dt: speak(w['ko'],"ko"),1.0)

    def vocab_start(self): self.v_run=True; self._v_next(0)
    def vocab_stop(self): self.v_run=False
    def _v_next(self, dt):
        if not self.v_run: return
        self.render_vocab()
        spd=int(self.root.get_screen("vocab").ids.spd.value); Clock.schedule_once(self._v_advance, spd)
    def _v_advance(self, dt):
        if self.ab_a is not None and self.ab_b is not None:
            if self.v_idx>=self.ab_b: self.v_idx=self.ab_a
            else: self.v_idx+=1
        else:
            self.v_idx+=1
            if self.v_idx>=len(WORDS["items"]) and not self.repeat_all:
                self.v_run=False; Snackbar(text="재생 완료", duration=1.2).open(); return
            self.v_idx%=len(WORDS["items"])
        self._v_next(0)
    def vocab_ab(self):
        if self.ab_a is None: self.ab_a=self.v_idx; Snackbar(text="A 지정", duration=1).open()
        elif self.ab_b is None:
            self.ab_b=self.v_idx
            if self.ab_b<self.ab_a: self.ab_a,self.ab_b=self.ab_b,self.ab_a
            self.v_run=True; Snackbar(text="B 지정, 구간 반복 시작", duration=1.2).open(); self._v_next(0)
        else:
            self.ab_a=self.ab_b=None; Snackbar(text="구간 반복 해제", duration=1).open()
    def vocab_all(self):
        self.repeat_all=not self.repeat_all; Snackbar(text="전체 반복: "+("ON" if self.repeat_all else "OFF"), duration=1).open()

    def render_hof(self):
        box=self.root.get_screen("hof").ids.hoflist; box.clear_widgets()
        ranks=sorted(DB["hall_of_fame"], key=lambda x:x["score"], reverse=True)[:7]
        if not ranks: box.add_widget(MDLabel(text="아직 기록이 없습니다.", halign="center"))
        for i,r in enumerate(ranks, start=1):
            box.add_widget(MDLabel(text=f"{i}. {r['name']}  {r['score']}", size_hint_y=None, height=36))

    def on_start(self): pass

if __name__=="__main__":
    AppX().run()
