import urllib.request

url = "https://raw.githubusercontent.com/adaoduque/Brasileirao_Dataset/master/campeonato-brasileiro-full.csv"

# Baixa os primeiros bytes brutos do arquivo
with urllib.request.urlopen(url) as r:
    raw = r.read(500)

print(raw)