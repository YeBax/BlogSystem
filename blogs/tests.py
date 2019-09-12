from django.test import TestCase

# Create your tests here.

from bs4 import BeautifulSoup

s = '''
<h1>hello world</h1>
<div>
    11111111111
    <span>aaaaaaaaaaaaa</span>
</div>
'''

soup = BeautifulSoup(s, "html.parser")


print(soup.find_all())
print(soup.name)
for tag in soup.find_all():
    print(tag.name)
    tag.decompose()
print(soup)
