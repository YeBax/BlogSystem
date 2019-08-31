import random


def get_random_color():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def get_valid_code_img(request):
    # 方式1：
    # with open("validCode.png", "rb") as f:
    #     data = f.read()

    # 方式2
    # from PIL import Image
    # img = Image.new("RGB", (270, 40), color=get_random_color())
    # with open("validCode.png", "wb") as f:
    #     img.save(f, "png")
    #
    # with open("validCode.png", "rb") as f:
    #     data = f.read()

    # 方式3
    # from PIL import Image
    # from io import BytesIO
    # img = Image.new("RGB", (270, 40), color=get_random_color())
    # f = BytesIO()
    # img.save(f, "png")
    # data = f.getvalue()

    # 方式4
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO
    img = Image.new("RGB", (270, 40), color=get_random_color())
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("static/font/UniTortred.ttf", size=20)

    valid_code_str = ""
    for i in range(5):
        random_num = str(random.randint(0, 9))  # 随机数字
        random_low_alpha = chr(random.randint(95, 122))  # 随机小写字母
        random_upper_alpha = chr(random.randint(65, 90))  # 随机大写字母
        random_char = random.choice([random_num, random_low_alpha, random_upper_alpha])
        draw.text((i * 50, 5), random_char, get_random_color(), font=font)

        # 保存验证码
        valid_code_str += random_char

    print(valid_code_str)
    request.session["valid_code_str"] = valid_code_str
    '''
    1 生成一个随机字符串 sdlkfaslkf123123dfs
    2 COOKIE {"sessionid":"sdlkfaslkf123123dfs"}
    3 django-session
        session-key             session-data
        sdlkfaslkf123123dfs        {"valid_code_str":"12345"}
    '''
    # 和图片的宽高一致
    width = 270
    height = 40
    # for i in range(5):
    #     # 划线  噪线
    #     x1 = random.randint(0, width)
    #     x2 = random.randint(0, width)
    #     y1 = random.randint(0, height)
    #     y2 = random.randint(0, height)
    #     draw.line((x1, x2, y1, y2), fill=get_random_color())
    #
    # for i in range(20):
    #     # 画点 画圈， 噪点
    #     draw.point([random.randint(0, width), random.randint(0, height)], fill=get_random_color())
    #     x = random.randint(0, width)
    #     y = random.randint(0, height)
    #     draw.arc((x,y,x+4, y+4), 0, 180, fill=get_random_color())

    f = BytesIO()
    img.save(f, "png")
    data = f.getvalue()
    return data
