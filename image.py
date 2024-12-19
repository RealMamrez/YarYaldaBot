import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

def get_text_size(text, font):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return font.getbbox(bidi_text)[2]

def get_en_num(fa_num):
    numbers = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    }
    return ''.join(numbers.get(digit, digit) for digit in fa_num)


def make_image(file):
    BLACK = (0, 0, 0)
    font = ImageFont.truetype('src/font/Tanha.ttf', 80)
    title = ImageFont.truetype('src/font/Tanha.ttf', 100)

    with open(f'hafez/{file}', 'r', encoding='utf-8') as f:
        text = f.read().split('\n')[:4]

    image = Image.open('src/images/bg.jpg')
    TEXT = ImageDraw.Draw(image)

    _, _, length, width = image.getbbox()
    half_width, half_length = int(width / 2), int(length / 2)

    title_text = f"غزل {get_en_num(file)}"
    reshaped_title_text = arabic_reshaper.reshape(title_text)
    bidi_title_text = get_display(reshaped_title_text)

    # title
    TEXT.text((half_length - int(get_text_size(bidi_title_text, title) / 2), int(width / 3) - 100), bidi_title_text, BLACK, font=title)

    # The first bit
    reshaped_text_0 = get_display(arabic_reshaper.reshape(text[0]))
    reshaped_text_1 = get_display(arabic_reshaper.reshape(text[1]))
    reshaped_text_2 = get_display(arabic_reshaper.reshape(text[2]))
    reshaped_text_3 = get_display(arabic_reshaper.reshape(text[3]))

    TEXT.text((half_length + 50, half_width - 220), reshaped_text_0, BLACK, font=font)
    TEXT.text((half_length - get_text_size(reshaped_text_1, font) - 50, half_width - 70), reshaped_text_1, BLACK, font=font)

    # The second bit
    TEXT.text((half_length + 50, half_width + 80), reshaped_text_2, BLACK, font=font)
    TEXT.text((half_length - get_text_size(reshaped_text_3, font) - 50, half_width + 230), reshaped_text_3, BLACK, font=font)

    image.save('image.jpg', quality=80)
    return 'image.jpg'

