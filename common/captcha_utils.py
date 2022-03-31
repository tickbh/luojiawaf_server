from captcha.image import ImageCaptcha
import random
import string
import io
import base64

#characters为验证码上的字符集，10个数字加26个大写英文字母
#0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ str类型

characters = "0123456789ABCDEFGHJKMNOPQRSTUVWXYZ"
def gen_random_image(num=4, width=170,height=80):
    generator=ImageCaptcha(width=width,height=height)
    random_str=''.join([random.choice(characters) for j in range(num)])
    img=generator.generate_image(random_str)
    img_byte=io.BytesIO()
    img.save(img_byte,format='PNG')
    return random_str, img_byte.getvalue()