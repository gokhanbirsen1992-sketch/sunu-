# Denetim kontrol listesi

Bu oturumdaki dört kılavuz ve üç orijinal çalışmada gerçekten bulunan hata türlerinden derlendi. Her maddenin yanında örnek var.

## A. Aritmetik
- [ ] Her yüzde = pay / payda. Payda değişiyor mu (34 mü 33 mü)? Örnek: "%78 (n=26)" → 26/34 = %76,5.
- [ ] Alt grupların toplamı ana grubu veriyor mu? Örnek: profilaksi alan 23 + almayan 12 = 35, kohort 34.
- [ ] Akış şemasındaki her kutu bir öncekiyle tutarlı mı?
- [ ] Tablo toplamları (ör. evre dağılımı satır/sütun toplamları).
- [ ] Özet, metin ve tablo aynı sayıyı mı veriyor?

## B. İstatistik
- [ ] 2×2 tabloda beklenen hücre değeri <5 → Fisher exact gerekir. Yeniden hesapla:
  ```python
  from scipy.stats import fisher_exact, chi2_contingency
  t=[[a,b],[c,d]]
  print(fisher_exact(t)[1], chi2_contingency(t,correction=False)[1], chi2_contingency(t)[3].min())
  ```
  Makaledeki p düzeltmesiz ki-kareyle birebir örtüşüyorsa ve Fisher anlamsızsa → ana bulgu çöker.
- [ ] Çoklu karşılaştırma düzeltmesi var mı? Kaç test yapılmış?
- [ ] Güven aralığı: nokta tahmini aralığın içinde mi? (Örnek: "RR 0,26, GA 0,26–0,88" imkânsız.) Ortalama farkta aralık simetrik mi?
- [ ] OR / RR / mutlak fark: mutlak fark ve tedavi edilmesi gereken sayıyı hesapla (1/fark).
- [ ] Alt grup içi OR gerçekten o alt grupta mı hesaplanmış?
- [ ] Ortalamaya gerileme: en uç başlangıç değeri olan grup "en çok düzelen" mi?

## C. Tasarım
- [ ] Döngüsellik: tanı ölçütü sonlanımı içeriyor mu? (Örnek: "diyete yanıt" hem tanı hem sonlanım.)
- [ ] Sonlanım hekim takdirine bağlı mı? (İnfüzyon endikasyonu tanımsız.)
- [ ] Kontrol grubu yoksa kendiliğinden düzelme ayrılabiliyor mu?
- [ ] Sevk yanlılığı (yalnız üçüncü basamak), seçilim yanlılığı.
- [ ] Endikasyon karıştırıcılığı (ör. "ilaç alan daha kötü seyretti").
- [ ] İzlem süresi gruplar arasında farklı mı?
- [ ] Kayıp veri oranı (n/N her değişkende).
- [ ] "Refrakter" ya da "yanıtsız" tanımı yeterli süre sonra mı yapılmış? (1 aylık oktreotid denemesi.)
- [ ] Bulgular tanımlanan popülasyonla uyumlu mu? (Ör. "refrakter" denen ülserlerin çoğu iyileşme evresinde.)

## D. Kılavuza özgü
- [ ] Uzlaşı eşiği (ör. ">%75 üye >6 oy") her oylamada sağlanıyor mu? Hesapla:
  ```python
  v=[6,6,6,6,8,8,8,8,8,9]; print(sum(x>6 for x in v)/len(v))
  ```
  Oy veren sayısı değişiyor mu?
- [ ] "Suggest" = zayıf, "recommend" = güçlü. Fiil ile etiket uyuşuyor mu?
- [ ] "Based on expert opinion" + "strong" → gerekçesi yazılmış mı?
- [ ] Metindeki öneri ile özet tablosundaki öneri birebir aynı mı ("ya da" / "ve", kapsam daralması)?
- [ ] Algoritma ile öneriler çelişiyor mu?
- [ ] Erişkin kılavuzuyla farklıysa gerekçe biyolojik mi, coğrafi mi?
- [ ] Tarama bitiş tarihi ile yayın tarihi arası; sonradan çıkan önemli kanıt (RKÇ) var mı?
- [ ] Referans gerçekten iddiayı destekliyor mu? (Örnek: Maastricht VI diye Maastricht III'e atıf; mikrobiyota iddiası farmakovijilans çalışmasına dayanıyor.)

## E. Doz tablosu
- [ ] Her bandın alt ve üst sınırında mg/kg/gün hesapla.
- [ ] Bant boşlukları (15 kg altı, 49–50 kg, tam 20 kg).
- [ ] Metindeki üst sınır (ör. metronidazol 30 mg/kg/gün) tabloyla çelişiyor mu?
- [ ] "Maksimum" doz başına mı gün başına mı?
- [ ] Önerilmeyen ilacın dozu listelenmiş mi? Yaş kontrendikasyonu yazılmış mı?
- [ ] Piyasadan çekilmiş ilaç var mı? (Bellekten ise `[doğrulanmalı]`.)

## F. Çıkar ve bağlam
- [ ] Çıkar beyanı belirli bir öneriyle (ör. formül değişikliği) ilişkili mi? Bu tek başına öneriyi geçersiz kılmaz; okuyucuya bildir.
- [ ] Sponsor çalışanı yazar mı (ilaç çalışmaları)?
- [ ] Türkiye'ye uyarlanabilirlik: direnç oranları, ilaç erişimi, prevalans. Bilmiyorsan "bulamadım".

## G. Yazım / dil
- [ ] İlaç adı yanlış sınıflanmış mı? (Örnek: Calciparine = kalsiyum heparin, kalsiyum kanal blokeri değil `[doğrulanmalı]`.)
- [ ] Tekrarlanan ya da eksik dipnot, dizgi hatası — yalnız anlamı etkiliyorsa yaz.
