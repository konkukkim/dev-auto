import tkinter as tk
from tkinter import messagebox
import os
import sys
import ctypes

# MeCab을 임포트하기 전에 환경 설정
def setup_mecab():
    """MeCab 설정 및 의존성 확인"""
    try:
        import MeCab
        return MeCab
    except ImportError:
        messagebox.showerror("MeCab 오류", "MeCab 모듈이 설치되어 있지 않습니다.")
        sys.exit(1)
    except Exception as e:
        messagebox.showerror("MeCab 오류", f"MeCab 로드 중 오류 발생: {str(e)}")
        sys.exit(1)

# 실행 파일 디렉토리 기준 경로 반환
def get_base_path():
    """실행 파일 또는 스크립트 위치 기준으로 기본 경로 반환"""
    if getattr(sys, 'frozen', False):
        # PyInstaller로 패키징된 경우
        return os.path.dirname(sys.executable)
    else:
        # 일반 스크립트 실행 경우
        return os.path.dirname(os.path.abspath(__file__))

def find_mecab_rc():
    """실행파일 기준 고정된 mecabrc 경로 반환"""
    base_path = get_base_path()
    mecab_rc_path = os.path.join(base_path, 'mecab', 'etc', 'mecabrc')

    if os.path.exists(mecab_rc_path):
        return mecab_rc_path
    else:
        return None


def load_word_dict():
    """word.txt 파일을 읽고 단어와 매핑되는 값들을 딕셔너리로 반환"""
    base_path = get_base_path()
    file_path = os.path.join(base_path, 'word.txt')
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"단어 사전 파일({file_path})을 찾을 수 없습니다.")
    
    word_dict = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                word_dict[parts[0]] = parts[1]
    
    if not word_dict:
        raise ValueError("단어 사전이 비어 있습니다. 올바른 형식의 파일인지 확인하세요.")
    
    return word_dict

def get_morphs(text):
    """MeCab에서 형태소 리스트만 뽑아내기"""
    MeCab = setup_mecab()
    
    try:
        # mecabrc 파일 경로 찾기
        mecab_rc_path = find_mecab_rc()
        
        if mecab_rc_path:
            # 경로에 공백이 있을 수 있으므로 따옴표로 묶음
            tagger = MeCab.Tagger(f'-r "{mecab_rc_path}"')
        else:
            # 설정 파일을 찾지 못하면 인자 없이 시도
            try:
                tagger = MeCab.Tagger('')
            except:
                # 그래도 안 되면 기본 생성자 사용
                tagger = MeCab.Tagger()
        
        parsed = tagger.parse(text)
        lines = parsed.split('\n')
        morphs = []
        for line in lines:
            if line == 'EOS' or line == '':
                continue
            morph = line.split('\t')[0]
            morphs.append(morph)
        return morphs
    except Exception as e:
        error_msg = f"형태소 분석 중 오류 발생: {str(e)}"
        messagebox.showerror("MeCab 오류", error_msg)
        return []

def generate_column_name(input_words, word_dict):
    """입력된 단어들에 대해 DB 컬럼명 생성"""
    matched_words = [word_dict[word] for word in input_words if word in word_dict]
    if not matched_words:
        return ""
    column_name = '_'.join(matched_words)
    return column_name

class DBColumnGenerator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DB 컬럼명 생성기 (MeCab)")
        self.geometry("500x300")
        self.minsize(500, 300)
        
        # 아이콘 설정 (있는 경우)
        try:
            base_path = get_base_path()
            icon_path = os.path.join(base_path, "icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except:
            pass
        
        # mecabrc 파일 확인
        self.mecab_rc_path = find_mecab_rc()
        if not self.mecab_rc_path:
            self.after(100, lambda: messagebox.showwarning(
                "MeCab 설정 없음", 
                "MeCab 설정 파일(mecabrc)을 찾을 수 없습니다.\n"
                "MeCab이 제대로 작동하지 않을 수 있습니다."
            ))
        
        # 단어 사전 로드
        try:
            self.word_dict = load_word_dict()
        except FileNotFoundError:
            self.word_dict = {}
            self.after(100, lambda: messagebox.showwarning(
                "단어 사전 없음",
                "word.txt 파일을 찾을 수 없습니다.\n"
                "프로그램 실행 폴더에 word.txt 파일을 배치하세요."
            ))
        except Exception as e:
            self.word_dict = {}
            self.after(100, lambda: messagebox.showerror(
                "단어 사전 오류",
                f"단어 사전 로드 중 오류 발생: {str(e)}"
            ))
        
        self.create_widgets()
    
    def create_widgets(self):
        # 메인 프레임
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 입력 프레임
        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(input_frame, text="D:\\tmp\get-col 에서 실행하면 됩니다.\n단어를 입력하세요:").pack(side=tk.LEFT, padx=5)
        
        self.entry = tk.Entry(input_frame)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.entry.bind("<Return>", lambda e: self.process_input())
        
        # 버튼 프레임
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        generate_btn = tk.Button(button_frame, text="생성", command=self.process_input)
        generate_btn.pack(side=tk.LEFT, padx=5)
        
        # 결과 프레임
        result_frame = tk.Frame(main_frame)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 결과 표시 텍스트 박스
        result_label = tk.Label(result_frame, text="결과:")
        result_label.pack(anchor=tk.W)
        
        self.result_text = tk.Text(result_frame, height=10, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        self.result_text.config(state=tk.DISABLED)
        
        # 상태바
        self.status_var = tk.StringVar()
        if self.mecab_rc_path:
            self.status_var.set(f"MeCab 설정: {self.mecab_rc_path}")
        else:
            self.status_var.set("MeCab 설정 없음")
        status_bar = tk.Label(self, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def process_input(self):
        input_text = self.entry.get().strip()
        if not input_text:
            messagebox.showwarning("입력 오류", "단어를 입력해주세요.")
            return
        
        if not self.word_dict:
            messagebox.showwarning("단어 사전 없음", "단어 사전이 로드되지 않았습니다.")
            return
        
        try:
            self.status_var.set("처리 중...")
            self.update_idletasks()
            
            morphs = get_morphs(input_text)
            if not morphs:
                self.status_var.set("형태소 분석 실패")
                return
            
            column_name = generate_column_name(morphs, self.word_dict)
            
            result_text = f"입력: {input_text}\n\n"
            result_text += f"형태소: {', '.join(morphs)}\n\n"
            result_text += f"생성된 컬럼명: {column_name}"
            
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result_text)
            self.result_text.config(state=tk.DISABLED)
            
            if self.mecab_rc_path:
                self.status_var.set(f"MeCab 설정: {self.mecab_rc_path}")
            else:
                self.status_var.set("완료 (MeCab 설정 없음)")
        except Exception as e:
            self.status_var.set("오류 발생")
            messagebox.showerror("처리 오류", str(e))

if __name__ == "__main__":
    # 높은 DPI 설정 대응
    if sys.platform == 'win32':
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    
    app = DBColumnGenerator()
    app.mainloop()