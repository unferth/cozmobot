import sys
from googletrans import Translator
translator = Translator()
text = sys.argv[1]
output = ''

# remove fortune quotes
text = text.replace('-+-','')
text = text.strip()

# english
trans = ''
try:
    result = translator.translate(text)
    trans = result.text.strip()
    trans = trans.replace('.','')
except:
    trans = text.lower()
# phonetic = result.pronunciation
if trans.lower().replace('.','') != text.lower().replace('.',''):
    output += trans + ' '

# french
trans = ''
try:
    result = translator.translate(text, dest='fr')
    trans = result.text.strip()
    trans = trans.replace('.','')
except:
    trans = text.lower()
if trans.lower().replace('.','') != text.lower().replace('.',''):
    output += trans + ' '

# spanish
trans = ''
try:
    result = translator.translate(text, dest='es')
    trans = result.text.strip()
    trans = trans.replace('.','')
except:
    trans = text.lower()
if trans.lower().replace('.','') != text.lower().replace('.',''):
    output += trans + ' '

output = output.replace(text,'')
output = output.strip()
if output != text:
    print(output)
