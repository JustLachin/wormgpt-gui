from requests import get as istekGönder
import pyfiglet as logoYardımcısı
import shutil as terminalYardımcısı
from time import sleep as bekle
from os import system as sistem
from urllib.parse import quote as şifrele
# =========================
varsayılanBeklemeSüresi = 2
# =========================
varsayılanDil = ""
# =========================
normal = "\x1b[0m"
# =========================
siyah = "\x1b[0;30m"
kırmızı = "\x1b[0;31m"
yeşil = "\x1b[0;32m"
sarı = "\x1b[0;33m"
mavi = "\x1b[0;34m"
mor = "\x1b[0;35m"
camgöbeği = "\x1b[0;36m"   # açık mavi
beyaz = "\x1b[0;37m"
# =========================
parlak_siyah = "\x1b[1;30m"   # gri
parlak_kırmızı = "\x1b[1;31m"
parlak_yeşil = "\x1b[1;32m"
parlak_sarı = "\x1b[1;33m"
parlak_mavi = "\x1b[1;34m"
parlak_mor = "\x1b[1;35m"
parlak_cyano = "\x1b[1;36m"
parlak_beyaz = "\x1b[1;37m"
# =========================
arkaplan_siyah = "\x1b[40m"
arkaplan_kırmızı = "\x1b[41m"
arkaplan_yeşil = "\x1b[42m"
arkaplan_sarı = "\x1b[43m"
arkaplan_mavi = "\x1b[44m"
arkaplan_mor = "\x1b[45m"
arkaplan_cyano = "\x1b[46m"
arkaplan_beyaz = "\x1b[47m"
# =========================
def ekranıTemizle():
    sistem("clear")
# =========================
def başlık():
    ekranıTemizle()
    print(mavi+"="*67+normal)
    terminalBoyutu = terminalYardımcısı.get_terminal_size().columns
    başlıkMetni = logoYardımcısı.figlet_format("Worm GPT")
    for satır in başlıkMetni.splitlines():
        print(satır.center(terminalBoyutu))
    print(mavi+"="*67+normal)
    print(kırmızı+"["+sarı+"INFO"+kırmızı+"]"+parlak_beyaz+" Tool: Worm GPT / Programmer: @İncphp")
    print(mavi+"="*67+normal)
# =========================
def bağlantıBilgileri(soru, dil):
    bağlantıLinki = "https://newtonhack.serv00.net/GPT/wormgpt.php?ask="+şifrele(soru)+şifrele(" (ONLY {dil} ANSWER)")
    return bağlantıLinki
# =========================
def cevabıAl(soru, dil):
    try:
        bağlantıLinki = bağlantıBilgileri(soru, dil)
        cevap = istekGönder(bağlantıLinki).text
        return cevap
    except Exception as HATA:
        print(kırmızı+"["+parlak_kırmızı+"ALERT"+kırmızı+"]"+parlak_mavi+" Bilinmeyen hata:",HATA)
# =========================
def soruyuAl():
    while True:
        ekranıTemizle()
        başlık()
        try:
            soruGirişi = input(kırmızı+"["+sarı+"INPUT"+kırmızı+"]"+yeşil+" Sorunuzu Girin: "+parlak_sarı)
            if soruGirişi:
                return soruGirişi
            else:
                print(kırmızı+"["+parlak_kırmızı+"ALERT"+kırmızı+"]"+parlak_mavi+" Soru Girişi Hatalı Tanımlandı. Tekrar Deneyin.")
                bekle(varsayılanBeklemeSüresi)
        except Exception as HATA:
            print(kırmızı+"["+parlak_kırmızı+"ALERT"+kırmızı+"]"+parlak_mavi+" Bilinmeyen hata:", HATA)
            break


# =========================
def diliAl():
    global varsayılanDil
    if varsayılanDil:
        return varsayılanDil
    while True:
        ekranıTemizle()
        başlık()
        try:
            dilGirişi = input(kırmızı+"["+sarı+"INPUT"+kırmızı+"]"+yeşil+" Dil Girin: "+parlak_sarı)
            if not dilGirişi:
                print(kırmızı+"["+parlak_kırmızı+"ALERT"+kırmızı+"]"+parlak_mavi+" Dil Girişi Hatalı Tanımlandı. Tekrar Deneyin.")
                bekle(varsayılanBeklemeSüresi)
                diliAl()
            varsayılanDil = dilGirişi
            return dilGirişi
        except Exception as HATA:
            print(kırmızı+"["+parlak_kırmızı+"ALERT"+kırmızı+"]"+parlak_mavi+" Bilinmeyen hata:", HATA)
            break
# =========================
def kalanTekKral():
    while True:
        soru = soruyuAl()
        dil = diliAl()
        cevap = cevabıAl(soru, dil)
        print(sarı+"["+ yeşil+"ANSWER"+  sarı+"] "+parlak_sarı+cevap+arkaplan_siyah)
        input(kırmızı+"["+sarı+"INPUT"+kırmızı+"]"+yeşil+" Yeni Soru Sormak İçin Enter' a Basın' "+parlak_sarı)

if __name__ == "__main__":
    kalanTekKral()