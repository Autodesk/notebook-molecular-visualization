from nbmolviz.utils import translate_color

def func(x):
    return x + 1

def test_example():
    css_color = 'tomato'
    translated_color = translate_color(css_color)
    assert translated_color == '0xff6347'
