import codecs
buf = b'\xa9\xec\x00P\xd9U\x9c5\x8b9\xa0\xc1\x80\x10\x00\x03o>\x00\x00\x01\x01\x08\n\x0en\x91\xb63fP\x96'
buf2 = buf.decode('unicode_escape').encode('utf-8')
str = buf.decode('unicode_escape')
#str2 = str.decode("UTF-8")
print(type(buf))