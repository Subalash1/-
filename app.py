from flask import Flask, render_template, request, jsonify, session
import random
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
import uuid

try:
    from pypinyin import pinyin, Style
except ImportError:
    print("请安装pypinyin库: pip install pypinyin")
    exit(1)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

@dataclass
class CharacterInfo:
    chinese: str
    pinyin: str
    tone: str

class ToneExtractor:
    @classmethod
    def extract_tone(cls, pinyin_with_tone: str) -> str:
        tone_match = re.search(r'[1-4]', pinyin_with_tone)
        return tone_match.group() if tone_match else ''

class WordProcessor:
    @staticmethod
    def get_character_info(char: str) -> CharacterInfo:
        py_no_tone = pinyin(char, style=Style.NORMAL, heteronym=False)
        pinyin_str = py_no_tone[0][0] if py_no_tone and py_no_tone[0] else ''
        
        py_with_tone = pinyin(char, style=Style.TONE3, heteronym=False)
        pinyin_with_tone = py_with_tone[0][0] if py_with_tone and py_with_tone[0] else ''
        
        tone_str = ToneExtractor.extract_tone(pinyin_with_tone)
        
        return CharacterInfo(chinese=char, pinyin=pinyin_str, tone=tone_str)
    
    @staticmethod
    def process_word(word: str) -> List[CharacterInfo]:
        if len(word) != 4:
            raise ValueError("词语必须是四个字符")
        
        return [WordProcessor.get_character_info(char) for char in word]

class WordleGameWeb:
    def __init__(self, max_attempts: int = 15):
        self.max_attempts = max_attempts
        self.attempts = 0
        self.target_word = ""
        self.target_info = []
        self.game_over = False
        self.won = False
        self.guess_history = []
        
        self.word_bank = [
           
            # 搞怪幽默词
            "黑人牙膏", "鸽鸽加油","奶茶续命",
            "熬夜冠军", "秃头青年",
            "吃瓜群众", "网络冲浪", 
            "游戏人生", "追番狂魔", "夹带私货", "钱包见底",
            "工资到账",
            "摸鱼达人", "划水专家", "午休冠军", "迟到常客",
            "早起困难", "周一恐惧",
            
            # 彩蛋词（华南理工相关）
            "华南理工", "易烊千玺", "数学学院", "理辩理辩",
            "五山校区", "建筑老八", "食堂排队", "民国宿舍"
        ]
    
    def start_new_game(self):
        self.target_word = random.choice(self.word_bank)
        self.target_info = WordProcessor.process_word(self.target_word)
        self.attempts = 0
        self.game_over = False
        self.won = False
        self.guess_history = []
    
    def compare_words(self, guess_info: List[CharacterInfo]) -> List[Dict]:
        result = []
        target_chars = [info.chinese for info in self.target_info]
        target_pinyins = [info.pinyin for info in self.target_info]
        target_tones = [info.tone for info in self.target_info]
        
        for i, guess_char_info in enumerate(guess_info):
            char_result = {
                'chinese': {'char': guess_char_info.chinese, 'color': 'white'},
                'pinyin': {'text': guess_char_info.pinyin, 'colors': []},
                'tone': {'text': guess_char_info.tone, 'colors': []}
            }
            
            # 比较中文字符
            if guess_char_info.chinese == target_chars[i]:
                char_result['chinese']['color'] = 'blue'
            elif guess_char_info.chinese in target_chars:
                char_result['chinese']['color'] = 'yellow'
            else:
                char_result['chinese']['color'] = 'gray'
            
            # 比较拼音中的每个字母
            guess_pinyin = guess_char_info.pinyin
            for j, letter in enumerate(guess_pinyin):
                color = 'gray'
                found_correct_position = False
                for k, target_py in enumerate(target_pinyins):
                    if j < len(target_py) and letter == target_py[j]:
                        if k == i:
                            color = 'blue'
                            found_correct_position = True
                            break
                
                if not found_correct_position:
                    for target_py in target_pinyins:
                        if letter in target_py:
                            color = 'yellow'
                            break
                
                char_result['pinyin']['colors'].append(color)
            
            # 比较声调
            guess_tone = guess_char_info.tone
            if guess_tone == target_tones[i]:
                char_result['tone']['colors'].append('blue')
            elif guess_tone in target_tones:
                char_result['tone']['colors'].append('yellow')
            else:
                char_result['tone']['colors'].append('gray')
            
            result.append(char_result)
        
        return result
    
    def make_guess(self, guess_word: str) -> Dict:
        if self.game_over:
            return {"success": False, "message": "游戏已结束！"}
        
        if len(guess_word) != 4:
            return {"success": False, "message": "请输入四个字的词语！"}
        
        self.attempts += 1
        
        try:
            guess_info = WordProcessor.process_word(guess_word)
            result = self.compare_words(guess_info)
            
            # 保存到历史记录
            guess_data = {
                'word': guess_word,
                'result': result,
                'attempt': self.attempts
            }
            self.guess_history.append(guess_data)
            
            # 检查是否获胜
            if guess_word == self.target_word:
                self.won = True
                self.game_over = True
                return {
                    "success": True,
                    "result": result,
                    "game_over": True,
                    "won": True,
                    "message": f"🎉 恭喜！你在第{self.attempts}次猜对了！",
                    "attempts": self.attempts,
                    "max_attempts": self.max_attempts
                }
            
            # 检查是否用完机会
            if self.attempts >= self.max_attempts:
                self.game_over = True
                target_details = []
                for info in self.target_info:
                    target_details.append({
                        'chinese': info.chinese,
                        'pinyin': info.pinyin,
                        'tone': info.tone
                    })
                return {
                    "success": True,
                    "result": result,
                    "game_over": True,
                    "won": False,
                    "message": f"😞 游戏结束！正确答案是: {self.target_word}",
                    "target_word": self.target_word,
                    "target_details": target_details,
                    "attempts": self.attempts,
                    "max_attempts": self.max_attempts
                }
            
            return {
                "success": True,
                "result": result,
                "game_over": False,
                "attempts": self.attempts,
                "max_attempts": self.max_attempts,
                "remaining": self.max_attempts - self.attempts
            }
            
        except Exception as e:
            return {"success": False, "message": f"处理词语时出错: {e}"}

# 全局游戏实例存储
games = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/new_game', methods=['POST'])
def new_game():
    game_id = str(uuid.uuid4())
    game = WordleGameWeb()
    game.start_new_game()
    games[game_id] = game
    session['game_id'] = game_id
    
    return jsonify({
        "success": True,
        "game_id": game_id,
        "max_attempts": game.max_attempts
    })

@app.route('/api/guess', methods=['POST'])
def guess():
    data = request.get_json()
    guess_word = data.get('word', '').strip()
    game_id = session.get('game_id')
    
    if not game_id or game_id not in games:
        return jsonify({"success": False, "message": "游戏会话无效，请开始新游戏"})
    
    game = games[game_id]
    result = game.make_guess(guess_word)
    
    return jsonify(result)

@app.route('/api/game_status', methods=['GET'])
def game_status():
    game_id = session.get('game_id')
    
    if not game_id or game_id not in games:
        return jsonify({"success": False, "message": "无有效游戏会话"})
    
    game = games[game_id]
    
    return jsonify({
        "success": True,
        "attempts": game.attempts,
        "max_attempts": game.max_attempts,
        "game_over": game.game_over,
        "won": game.won,
        "guess_history": game.guess_history
    })

# 已移除 /api/get_pinyin 接口，不再需要实时查询拼音

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print("启动中文四字词语猜词游戏Web版...")
    print(f"本地访问: http://localhost:{port}")
    print("按 Ctrl+C 停止服务器")
    
    app.run(debug=debug, host='0.0.0.0', port=port)