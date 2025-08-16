import random
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass

try:
    from pypinyin import pinyin, Style
except ImportError:
    print("请安装pypinyin库: pip install pypinyin")
    exit(1)

@dataclass
class CharacterInfo:
    chinese: str
    pinyin: str
    tone: str

class ToneExtractor:
    # 声调提取器
    @classmethod
    def extract_tone(cls, pinyin_with_tone: str) -> str:
        # 从带声调的拼音中提取声调数字
        tone_match = re.search(r'[1-4]', pinyin_with_tone)
        return tone_match.group() if tone_match else ''

class WordProcessor:
    @staticmethod
    def get_character_info(char: str) -> CharacterInfo:
        # 获取不带声调的拼音
        py_no_tone = pinyin(char, style=Style.NORMAL, heteronym=False)
        pinyin_str = py_no_tone[0][0] if py_no_tone and py_no_tone[0] else ''
        
        # 获取带声调数字的拼音
        py_with_tone = pinyin(char, style=Style.TONE3, heteronym=False)
        pinyin_with_tone = py_with_tone[0][0] if py_with_tone and py_with_tone[0] else ''
        
        # 提取声调
        tone_str = ToneExtractor.extract_tone(pinyin_with_tone)
        
        return CharacterInfo(chinese=char, pinyin=pinyin_str, tone=tone_str)
    
    @staticmethod
    def process_word(word: str) -> List[CharacterInfo]:
        if len(word) != 4:
            raise ValueError("词语必须是四个字符")
        
        return [WordProcessor.get_character_info(char) for char in word]

class WordleGame:
    def __init__(self, max_attempts: int = 6):
        self.max_attempts = max_attempts
        self.attempts = 0
        self.target_word = ""
        self.target_info = []
        self.game_over = False
        self.won = False
        
        # 简单的词库
        self.word_bank = [
            "春夏秋冬", "东南西北", "喜怒哀乐", "酸甜苦辣", 
            "梅兰竹菊", "琴棋书画", "诗词歌赋", "金木水火",
            "风花雪月", "山川河流", "日月星辰", "花鸟鱼虫",
            "青红皂白", "黑白分明", "高低不平", "大小不一"
        ]
    
    def start_new_game(self):
        self.target_word = random.choice(self.word_bank)
        self.target_info = WordProcessor.process_word(self.target_word)
        self.attempts = 0
        self.game_over = False
        self.won = False
        print(f"=== 中文四字词语猜词游戏 ===")
        print(f"规则: 猜一个四字词语，最多{self.max_attempts}次机会")
        print(f"颜色提示: 🟦蓝色=正确位置, 🟨黄色=存在但位置错误, ⬜白色=不存在")
        print(f"开始游戏！请输入四字词语:")
    
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
            
            # 比较拼音中的每个字母
            guess_pinyin = guess_char_info.pinyin
            for j, letter in enumerate(guess_pinyin):
                color = 'white'
                # 检查是否在正确位置
                found_correct_position = False
                for k, target_py in enumerate(target_pinyins):
                    if j < len(target_py) and letter == target_py[j]:
                        if k == i:  # 同位置比较
                            color = 'blue'
                            found_correct_position = True
                            break
                
                if not found_correct_position:
                    # 检查是否存在于其他位置
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
                char_result['tone']['colors'].append('white')
            
            result.append(char_result)
        
        return result
    
    def display_result(self, guess_word: str, guess_info: List[CharacterInfo], result: List[Dict]):
        print(f"\n第{self.attempts}次猜测: {guess_word}")
        
        # 显示中文字符
        chinese_line = ""
        for char_data in result:
            char = char_data['chinese']['char']
            color = char_data['chinese']['color']
            if color == 'blue':
                chinese_line += f"🟦{char}"
            elif color == 'yellow':
                chinese_line += f"🟨{char}"
            else:
                chinese_line += f"⬜{char}"
        print(f"中文: {chinese_line}")
        
        # 显示拼音
        pinyin_line = ""
        for i, char_data in enumerate(result):
            pinyin = char_data['pinyin']['text']
            colors = char_data['pinyin']['colors']
            for j, letter in enumerate(pinyin):
                if j < len(colors):
                    color = colors[j]
                    if color == 'blue':
                        pinyin_line += f"🟦{letter}"
                    elif color == 'yellow':
                        pinyin_line += f"🟨{letter}"
                    else:
                        pinyin_line += f"⬜{letter}"
                else:
                    pinyin_line += f"⬜{letter}"
            if i < len(result) - 1:
                pinyin_line += " "
        print(f"拼音: {pinyin_line}")
        
        # 显示声调
        tone_line = ""
        for i, char_data in enumerate(result):
            tone = char_data['tone']['text']
            colors = char_data['tone']['colors']
            if colors:
                color = colors[0]
                if color == 'blue':
                    tone_line += f"🟦{tone}"
                elif color == 'yellow':
                    tone_line += f"🟨{tone}"
                else:
                    tone_line += f"⬜{tone}"
            else:
                tone_line += f"⬜{tone}"
            if i < len(result) - 1:
                tone_line += " "
        print(f"声调: {tone_line}")
    
    def make_guess(self, guess_word: str) -> bool:
        if self.game_over:
            print("游戏已结束！")
            return False
        
        if len(guess_word) != 4:
            print("请输入四个字的词语！")
            return False
        
        self.attempts += 1
        
        try:
            guess_info = WordProcessor.process_word(guess_word)
            result = self.compare_words(guess_info)
            self.display_result(guess_word, guess_info, result)
            
            # 检查是否获胜
            if guess_word == self.target_word:
                self.won = True
                self.game_over = True
                print(f"\n🎉 恭喜！你在第{self.attempts}次猜对了！")
                return True
            
            # 检查是否用完机会
            if self.attempts >= self.max_attempts:
                self.game_over = True
                print(f"\n😞 游戏结束！正确答案是: {self.target_word}")
                # 显示正确答案的拼音和音标
                print("正确答案详情:")
                for info in self.target_info:
                    print(f"  {info.chinese} - {info.pinyin} - 第{info.tone}声")
                return False
            
            print(f"\n剩余机会: {self.max_attempts - self.attempts}")
            return False
            
        except Exception as e:
            print(f"处理词语时出错: {e}")
            return False
    
    def play(self):
        self.start_new_game()
        
        while not self.game_over:
            guess = input("请输入四字词语: ").strip()
            if not guess:
                continue
            
            self.make_guess(guess)
        
        # 询问是否再玩一局
        while True:
            play_again = input("\n是否再玩一局？(y/n): ").strip().lower()
            if play_again in ['y', 'yes', '是', '好']:
                self.play()
                break
            elif play_again in ['n', 'no', '否', '不']:
                print("谢谢游玩！")
                break
            else:
                print("请输入 y 或 n")

if __name__ == "__main__":
    game = WordleGame()
    game.play()