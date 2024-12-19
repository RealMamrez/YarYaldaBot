import openpyxl
from random import choice
import arabic_reshaper
import pandas as pd

# تابع برای خواندن تمام تفسیرها از ستون سوم فایل اکسل
def read_meanings_from_xlsx(file_path):
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    meanings = []
    for row in sheet.iter_rows(min_row=2, values_only=True):  # نادیده گرفتن سطر سرصفحه
        if row[2]:  # بررسی کنید که ستون سوم مقدار دارد
            meanings.append(row[2].replace("_x000D_", "").strip())
    return meanings

# تابع برای انتخاب تصادفی یک تفسیر
def get_random_meaning(meanings):
    return choice(meanings)

def get_en_num(text):
    text = text[2:]
    english_numbers = "0123456789"
    persian_numbers = "۰۱۲۳۴۵۶۷۸۹"
    translation_table = str.maketrans(english_numbers, persian_numbers)
    return text.translate(translation_table)

df = pd.read_excel('faal.xlsx')
random_row = df.sample(n=1)

def show_poem(meaning):
    text = f"""
فال حافظ شما:
{meaning}
"""
    return text
# صادرات توابع
__all__ = ['read_meanings_from_xlsx', 'get_random_meaning', 'get_en_num', 'show_poem']
