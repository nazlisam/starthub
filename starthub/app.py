from flask import Flask, render_template, request, flash, redirect, url_for, session
import heapq
from collections import deque 

app = Flask(__name__)
app.secret_key = 'secret-key'

# --- 1. VERİ MODELLERİ ---

class Yatirimci:
    def __init__(self, id, isim, sektorler, butce, sirket, email, sifre):
        self.id = id
        self.isim = isim
        self.sektorler = sektorler
        self.butce = butce
        self.sirket = sirket
        self.email = email
        self.sifre = sifre
        self.tip = "yatirimci"

class Girisimci:
    def __init__(self, id, isim, sektor, talep_edilen_butce, email, sifre):
        self.id = id
        self.isim = isim
        self.sektor = sektor
        self.talep_edilen_butce = talep_edilen_butce
        self.email = email
        self.sifre = sifre
        self.tip = "girisimci"
    
    def bilgileri_guncelle(self, yeni_sektor, yeni_butce):
        self.sektor = yeni_sektor
        self.talep_edilen_butce = int(yeni_butce)

# --- 2. ÖRNEK VERİLER ---

yatirimcilar_liste = [
    Yatirimci(1, "Ahmet Yılmaz", ["Yazılım", "Finans"], 500000, "Venza Capital", "ahmet@venza.com", "1234"),
    Yatirimci(2, "Seda Kaya", ["Sağlık", "Biyotech"], 1000000, "Health VC", "seda@health.com", "1234"),
    Yatirimci(3, "Mehmet Demir", ["Yazılım", "Oyun"], 250000, "Game Invest", "mehmet@game.com", "1234"),
    Yatirimci(4, "Ayşe Çelik", ["E-Ticaret", "Yazılım"], 750000, "Global Fon", "ayse@global.com", "1234"),
    Yatirimci(5, "Caner Erkin", ["İnşaat"], 100000, "Yapı İnvest", "caner@yapi.com", "1234")
]

girisimciler_liste = [
    Girisimci(99, "Nazlı ŞAM", "Yazılım", 300000, "nazli@starthub.com", "1234"),
    Girisimci(100, "Zeliha Nur İNANÇ", "Sağlık", 150000, "zeliha@starthub.com", "1234")
]

# --- 3. VERİ YAPILARI KURULUMU ---

# [HASH TABLE] Kullanıcı Veritabanı
KULLANICI_HASH_TABLE = {}

def hash_table_doldur():
    for k in yatirimcilar_liste:
        KULLANICI_HASH_TABLE[k.email] = k
    for k in girisimciler_liste:
        KULLANICI_HASH_TABLE[k.email] = k

hash_table_doldur()

# [QUEUE] Mesaj Kuyruğu
mesaj_kuyrugu = deque() 

# [TRIE] Arama Ağacı Yapısı
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.investors = []

class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, text, investor):
        node = self.root
        for char in text.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        if investor not in node.investors:
            node.investors.append(investor)

    def search(self, prefix):
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []
            node = node.children[char]
        results = []
        self._collect_all(node, results)
        return results

    def _collect_all(self, node, results):
        if node.is_end:
            for inv in node.investors:
                if inv not in results:
                    results.append(inv)
        for char in node.children:
            self._collect_all(node.children[char], results)

# Trie'yi Doldur 
arama_agaci = Trie()
for y in yatirimcilar_liste:
    for kelime in y.isim.split(): arama_agaci.insert(kelime, y)
    for kelime in y.sirket.split(): arama_agaci.insert(kelime, y)
    for sektor in y.sektorler: arama_agaci.insert(sektor, y)

# [GRAPH] Sektör Ağı 
sektor_graph = {} 
def graph_olustur():
    for y in yatirimcilar_liste:
        for sektor in y.sektorler:
            if sektor not in sektor_graph:
                sektor_graph[sektor] = []
            sektor_graph[sektor].append(y)
graph_olustur()

# --- 4. ALGORİTMALAR ---

# [HEAP] Eşleştirme Algoritması
def en_uygun_yatirimcilari_bul(girisimci, top_n=3):
    aday_havuzu = []
    
    for yatirimci in yatirimcilar_liste:
        puan = 0
        if yatirimci.butce < girisimci.talep_edilen_butce: continue
        if girisimci.sektor in yatirimci.sektorler: puan += 50
        puan += (yatirimci.butce / 10000)
        
        heapq.heappush(aday_havuzu, (-puan, yatirimci.id, yatirimci))

    sonuc_listesi = []
    for _ in range(min(top_n, len(aday_havuzu))):
        puan, _, yatirimci = heapq.heappop(aday_havuzu)
        
        sektor_komsulari = len(sektor_graph.get(girisimci.sektor, [])) - 1
        yuzde = max(0, sektor_komsulari * 20)
        
        sonuc_listesi.append({
            "isim": yatirimci.isim,
            "sirket": yatirimci.sirket,
            "sektorler": yatirimci.sektorler,
            "uyum_puani": int(-puan),
            "network_gucu": sektor_komsulari,
            "network_yuzdesi": yuzde
        })
    return sonuc_listesi

# --- 5. ROTALAR (ROUTES) ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/giris-yap', methods=['GET', 'POST'])
def giris_yap():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Hash Table Kontrolü (O(1))
        if email in KULLANICI_HASH_TABLE:
            kullanici = KULLANICI_HASH_TABLE[email]
            if kullanici.sifre == password:
                session['user_email'] = kullanici.email
                session['user_name'] = kullanici.isim
                
                flash(f'Hoşgeldiniz, {kullanici.isim}!', 'success')
                
                # YÖNLENDİRME: Girişimci -> Profil, Yatırımcı -> Arama
                if kullanici.tip == 'girisimci':
                    return redirect(url_for('profil')) 
                else:
                    return redirect(url_for('ara'))
            else:
                flash('Hatalı şifre!', 'error')
        else:
            flash('Kullanıcı bulunamadı!', 'error')
            
    return render_template('giris-yap.html')

@app.route('/profil', methods=['GET', 'POST'])
def profil():
    if 'user_email' not in session:
        return redirect(url_for('giris_yap'))
    
    aktif_kullanici = KULLANICI_HASH_TABLE.get(session['user_email'])
    
    if request.method == 'POST':
        yeni_sektor = request.form.get('sektor')
        yeni_butce = request.form.get('butce')
        
        aktif_kullanici.bilgileri_guncelle(yeni_sektor, yeni_butce)
        flash('Bilgileriniz güncellendi, eşleşmeler hesaplanıyor...', 'success')
        return redirect(url_for('uygun_yatirimcilar'))
        
    return render_template('profil.html', kullanici=aktif_kullanici)

@app.route('/uygun-yatirimcilar')
def uygun_yatirimcilar():
    if 'user_email' not in session:
        return redirect(url_for('giris_yap'))
        
    aktif_kullanici = KULLANICI_HASH_TABLE.get(session['user_email'])
    sonuclar = en_uygun_yatirimcilari_bul(aktif_kullanici)
    
    return render_template('portal.html', girisimci=aktif_kullanici, eslesmeler=sonuclar)

@app.route('/ara')
def ara():
    kelime = request.args.get('q', '') 
    sonuclar = []
    if kelime:
        sonuclar = arama_agaci.search(kelime)
    return render_template('arama.html', sonuclar=sonuclar, aranan=kelime)

@app.route('/bize-ulasin', methods=['GET', 'POST'])
def bize_ulasin():
    if request.method == 'POST':
        form_data = {
            "ad": request.form.get('ad'),
            "mesaj": request.form.get('mesaj')
        }
        mesaj_kuyrugu.append(form_data)
        flash(f'Mesajınız sıraya alındı! Sırada {len(mesaj_kuyrugu)} kişi var.', 'success')
        return redirect(url_for('bize_ulasin'))
    return render_template('bize-ulasin.html')

@app.route('/admin/mesajlar')
def admin_mesajlar():
    return render_template('admin-mesajlar.html', mesajlar=list(mesaj_kuyrugu))

@app.route('/cikis')
def cikis():
    session.clear()
    return redirect(url_for('index'))

# Diğer Statik Sayfalar
@app.route('/hizmetler')
def hizmetler(): return render_template('hizmetler.html')
@app.route('/basari-oykuleri')
def basari_oykuleri(): return render_template('basari-oykuleri.html')
@app.route('/blog-detay')
def blog_detay(): return render_template('blog-detay.html')
@app.route('/hakkimizda')
def hakkimizda(): return render_template('hakkimizda.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
