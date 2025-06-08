import fitz
import re
import requests

def pdf_reder(path):
    reader = fitz.open(path)
    text = ""
    for page in reader:
        text += page.get_text()
    return text

def preprocess(txt):
    text = txt.replace('\n', ' ')\
              .replace('\t', ' ')\
              .replace('\xa0', ' ')\
              .replace('‌', '') 

    text = re.sub(r'[•●■▪️✔️❌⬛⬜→←→↔️✅➤➕➖➰⚠️▲▼…]', '', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'(?<=\w) (?=\w)', '', text)

    return text.strip()

def with_gemma3(text):
    try:
        prompt = f"متن زیر را به زبان ساده خلاصه کن:\n{text}"
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'qwen3:8b',
                'prompt': prompt,
                'system': 'اسم تو Paul هست.',
                'stream': False
            }
        )
        response.raise_for_status()
        return response.json().get('response', 'خطا در پاسخ')
    except requests.ConnectionError:
        return "server error"
    except requests.Timeout:
        return 'timeout error'
    except requests.RequestException:
        return "خطای عمومی"


def ask_question(context, question):
    try:
        prompt = f"""متن زیر را بخوان و به پرسش مطرح‌شده پاسخ دقیق و علمی بده.

متن:
{context}

پرسش:
{question}

پاسخ:"""
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'gemma3',
                'prompt': prompt,
                'system': 'تو یک متخصص پاسخ‌گویی به سؤالات علمی هستی.',
                'stream': False
            }
        )
        response.raise_for_status()
        return response.json().get('response', 'پاسخی یافت نشد')
    except requests.RequestException as e:
        return f"❌ خطا:\n{e}"




if __name__ == "__main__":
    pdf_path = "text.pdf"

    print("[+] Reading PDF...")
    full_text = pdf_reder(pdf_path)

    print("[✓] Cleaning text...")
    cleaned_text = preprocess(full_text)

    print("[✓] Sending to Gemma...")
    summary = with_gemma3(cleaned_text[:1500])  

    print("[✓] Summary:\n", summary)



while True:
        q = input("\n❓ سؤالت رو بپرس (یا 'exit' برای خروج): ")
        if q.lower() == "exit":
            break
        answer = ask_question(cleaned_text[:3000], q)  
        print("📘 پاسخ:\n", answer)
