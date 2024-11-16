import tkinter as tk
from tkinter import ttk, messagebox
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI


def generate_writing_prompt(writing_type, w5h1_info):
    prompts = {
        "시": f"""다음 정보를 바탕으로 시를 작성해주세요:
            {w5h1_info}
            한국어로 서정적이고 감성적인 시를 작성해주세요.""",
       
        "수필": f"""다음 정보를 바탕으로 수필을 작성해주세요:
            {w5h1_info}
            개인적인 경험과 생각을 담아 수필 형식으로 작성해주세요.""",
       
        "소설": f"""다음 정보를 바탕으로 단편 소설을 작성해주세요:
            {w5h1_info}
            등장인물, 배경, 사건을 포함한 이야기를 전개해주세요.""",
       
        "보고서": f"""다음 정보를 바탕으로 보고서를 작성해주세요:
            {w5h1_info}
            객관적인 사실과 분석을 포함한 공식적인 보고서 형식으로 작성해주세요."""
    }
    return prompts.get(writing_type, "")


class W5H1App:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("육하원칙 작문 생성기")
       
        # API 키 입력
        self.api_frame = tk.Frame(self.window)
        self.api_frame.pack(pady=5)
       
        self.api_label = tk.Label(self.api_frame, text="API 키:")
        self.api_label.pack(side=tk.LEFT)
       
        self.api_key_entry = tk.Entry(self.api_frame, width=50)
        self.api_key_entry.pack(side=tk.LEFT, padx=5)


        # 작문 종류 선택 프레임 추가
        self.writing_type_frame = tk.Frame(self.window)
        self.writing_type_frame.pack(pady=5)
       
        self.writing_type_label = tk.Label(self.writing_type_frame, text="작문 종류:")
        self.writing_type_label.pack(side=tk.LEFT)
       
        self.writing_type_var = tk.StringVar(value="시")
        self.writing_types = ["시", "수필", "소설", "보고서"]
       
        self.writing_type_menu = ttk.Combobox(
            self.writing_type_frame,
            textvariable=self.writing_type_var,
            values=self.writing_types,
            state="readonly"
        )
        self.writing_type_menu.pack(side=tk.LEFT, padx=5)
       
        # 육하원칙 입력 프레임
        self.input_frame = tk.Frame(self.window)
        self.input_frame.pack(pady=5)
       
        # 육하원칙 입력 필드들
        self.labels = ["누가", "언제", "어디서", "무엇을", "어떻게", "왜", "누구와"]
        self.entries = {}
       
        for label in self.labels:
            frame = tk.Frame(self.input_frame)
            frame.pack(pady=2)
           
            tk.Label(frame, text=f"{label}:").pack(side=tk.LEFT)
            entry = tk.Entry(frame, width=50)
            entry.pack(side=tk.LEFT, padx=5)
            self.entries[label.lower()] = entry
       
        # 버튼
        self.button_frame = tk.Frame(self.window)
        self.button_frame.pack(pady=5)
       
        self.generate_button = tk.Button(self.button_frame, text="작문생성", command=self.generate_writing)
        self.generate_button.pack()
       
        # 결과 텍스트
        self.result_frame = tk.Frame(self.window)
        self.result_frame.pack(pady=5, fill=tk.BOTH, expand=True)
       
        self.result_text = tk.Text(self.result_frame, height=10, width=50)
        self.result_text.pack(fill=tk.BOTH, expand=True)
       
        # 스크롤바
        self.scrollbar = tk.Scrollbar(self.result_frame, command=self.result_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=self.scrollbar.set)
        
        # 결과 텍스트 프레임 다음에 수정 요청 프레임 추가
        self.revision_frame = tk.Frame(self.window)
        self.revision_frame.pack(pady=5, fill=tk.X)
        
        self.revision_label = tk.Label(self.revision_frame, text="수정 요청:")
        self.revision_label.pack(side=tk.LEFT)
        
        self.revision_entry = tk.Entry(self.revision_frame, width=50)
        self.revision_entry.pack(side=tk.LEFT, padx=5)
        
        self.revision_button = tk.Button(self.revision_frame, text="수정하기", command=self.revise_writing)
        self.revision_button.pack(side=tk.LEFT)


    @property
    def who_entry(self): return self.entries["누가"]
    @property
    def when_entry(self): return self.entries["언제"]
    @property
    def where_entry(self): return self.entries["어디서"]
    @property
    def what_entry(self): return self.entries["무엇을"]
    @property
    def how_entry(self): return self.entries["어떻게"]
    @property
    def why_entry(self): return self.entries["왜"]
    @property
    def who_with_entry(self): return self.entries["누구와"]


    def generate_writing(self):
        # API 키 확인
        api_key = self.api_key_entry.get()
        if not api_key:
            messagebox.showerror("오류", "API 키를 입력해주세요.")
            return


        # 육하원칙 정보 수집
        w5h1_info = {
            "누가": self.who_entry.get(),
            "언제": self.when_entry.get(),
            "어디서": self.where_entry.get(),
            "무엇을": self.what_entry.get(),
            "어떻게": self.how_entry.get(),
            "왜": self.why_entry.get(),
            "누구와": self.who_with_entry.get()
        }


        # 빈 필드 확인
        if not all(w5h1_info.values()):
            messagebox.showerror("오류", "모든 필드를 입력해주세요.")
            return


        try:
            # Gemini 모델 설정
            genai.configure(api_key=api_key)
            llm = ChatGoogleGenerativeAI(
                google_api_key=api_key,
                model="gemini-1.0-pro",
                temperature=0.7
            )


            # 선택된 작문 종류에 따른 프롬프트 생성
            writing_type = self.writing_type_var.get()
            prompt = generate_writing_prompt(writing_type, w5h1_info)


            # 작문 생성
            response = llm.invoke(prompt)
           
            # 결과 표시
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, response.content)


        except Exception as e:
            messagebox.showerror("오류", f"오류가 발생했습니다: {str(e)}")


    def revise_writing(self):
        # API 키 확인
        api_key = self.api_key_entry.get()
        if not api_key:
            messagebox.showerror("오류", "API 키를 입력해주세요.")
            return
        
        # 현재 텍스트와 수정 요청 가져오기
        current_text = self.result_text.get(1.0, tk.END).strip()
        revision_request = self.revision_entry.get()
        
        if not current_text or not revision_request:
            messagebox.showerror("오류", "수정할 텍스트와 수정 요청 내용을 모두 입력해주세요.")
            return
            
        try:
            # Gemini 모델 설정
            genai.configure(api_key=api_key)
            llm = ChatGoogleGenerativeAI(
                google_api_key=api_key,
                model="gemini-1.0-pro",
                temperature=0.7
            )
            
            # 수정 요청 프롬프트 생성
            revision_prompt = f"""다음 텍스트를 주어진 요청사항에 따라 수정해주세요:

원본 텍스트:
{current_text}

수정 요청사항:
{revision_request}

수정된 전체 텍스트를 출력해주세요."""
            
            # 수정된 텍스트 생성
            response = llm.invoke(revision_prompt)
            
            # 결과 표시
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, response.content)
            
            # 수정 요청 필드 초기화
            self.revision_entry.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("오류", f"오류가 발생했습니다: {str(e)}")


    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = W5H1App()
    app.run()



