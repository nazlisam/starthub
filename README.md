# starthub

geçen sene arkadaşım zeliha nur inanç (github: zeliha-nur) ile veri yapıları dersi için geliştirdiğimiz flask tabanlı yatırımcı ve girişimci eşleştirme platformu.

## kullanılan veri yapıları

* **hash table:** kullanıcı veritabanı ve hızlı kimlik doğrulama işlemleri için.
* **heap:** girişimciye en uygun yatırımcıları puanlayıp listelemek için.
* **trie (prefix tree):** yatırımcı arama motorunda anlık ve hızlı arama yapabilmek için.
* **queue (fifo):** "bize ulaşın" sayfasından gelen mesajları sıraya koyup yönetmek için.

## kurulum

projeyi yerelinde çalıştırmak için sırasıyla şu komutları yazabilirsin:

```bash
pip install -r requirements.txt
python app.py
