from django import template

register = template.Library()

@register.filter(name='email_to_entity')
def email_to_entity(value):
    """Minimal email address encoding.  Change to HTML entities.
    e.g. mzepedarivera@fas.harvard.edu becomes:
    &#109;&#122;&#101;&#112;&#101;&#100;&#97;&#114;&#105;&#118;&#101;&#114;&#97;&#64;&#102;&#97;&#115;&#46;&#104;&#97;&#114;&#118;&#97;&#114;&#100;&#46;&#101;&#100;&#117;
    """
    if value is None:
        return ''
    encode_chars = []
    for char in value:
        try:
            fmt_char = '&#%s;' % ord(char)
        except:
            fmt_char = char
        encode_chars.append(fmt_char)
    return ''.join(encode_chars)
        
