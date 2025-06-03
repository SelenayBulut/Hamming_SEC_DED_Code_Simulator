# Tkinter modülünü içe aktarıyoruz - arayüz tasarımı için
import tkinter as tk
from tkinter import messagebox  # Uyarı ve hata mesajları için

# Kullanıcının girdiği veri ikili mi ve geçerli uzunlukta mı kontrol eden fonksiyon
def validate_binary_input(data):
    valid_lengths = [8, 16, 32]  # Geçerli veri uzunlukları
    # Girdi sadece 0 ve 1'lerden mi oluşuyor?
    if not all(c in '01' for c in data):
        return False, "Sadece 0 ve 1 karakterlerinden oluşan ikili sayı girilmelidir."

    # Veri uzunluğu geçerli değilse, en yakın geçerli uzunlukla farkı göster
    if len(data) not in valid_lengths:
        closest = min(valid_lengths, key=lambda x: abs(x - len(data)))
        fark = abs(len(data) - closest)
        if len(data) < closest:
            return False, f"{fark} karakter eksik girdiniz. En yakın geçerli uzunluk: {closest} bit."
        else:
            return False, f"{fark} karakter fazla girdiniz. En yakın geçerli uzunluk: {closest} bit."
    return True, "Geçerli uzunlukta veri girdiniz."

# Verilen veri bitlerinden Hamming SEC-DED kodunu hesaplayan fonksiyon
def calculate_hamming(data_bits):
    m = len(data_bits)  # Kullanıcıdan alınan veri bitlerinin sayısı
    r = 0  # Gereken parite bitlerinin sayısı

    # r değerini bul: 2^r ≥ m + r + 1 olacak şekilde r'yi artır
    while (2 ** r) < (m + r + 1):
        r += 1

    # Toplam uzunluk = veri bitleri + parite bitleri + genel parite
    # 1-index'li liste oluşturuyoruz (0. indeks kullanılmaz)
    hamming = ['0'] * (m + r + 1)

    j = 0  # Veri bitlerini yerleştirmek için indeks
    for i in range(1, len(hamming)):
        # 2'nin kuvveti olan pozisyonlar parite biti olarak ayrılmıştır
        if i & (i - 1) == 0:
            continue
        # Veri bitlerini parite bitleri harici yerlere sırayla yerleştir
        hamming[i] = data_bits[j]
        j += 1

    # Her parite biti için kendisine bağlı bitleri kontrol ederek değeri hesapla
    for i in range(r):
        parity_pos = 2 ** i  # Parite bitinin bulunduğu pozisyon
        count = 0
        for j in range(1, len(hamming)):
            if j & parity_pos:
                count += int(hamming[j])  # İlgili bit '1' ise say
        hamming[parity_pos] = str(count % 2)  # Tek/çift sayısına göre parite 0 ya da 1 olur

    # Genel parite (overall parity): Tüm bitlerin toplamı tek mi çift mi kontrol et
    total_ones = sum(int(bit) for bit in hamming[1:])
    overall_parity = str(total_ones % 2)  # 1'lerin toplamı tekse 1, çiftse 0

    # Parite + veri bitleri + genel parite şeklinde kodu döndür
    return ''.join(hamming[1:]) + overall_parity

# Kodlu veride belirli bir pozisyonda yapay hata oluşturma fonksiyonu
def introduce_error(hamming_code, error_position):
    code_list = list(hamming_code)
    if 0 <= error_position < len(code_list):
        # Hedef bit 0 ise 1'e, 1 ise 0'a çevrilir (bit flip)
        code_list[error_position] = '1' if code_list[error_position] == '0' else '0'
    return ''.join(code_list)

# Kod içinde hata olup olmadığını tespit eden ve gerekirse düzelten fonksiyon
def detect_and_correct(hamming_code):
    n = len(hamming_code)  # Kodun toplam uzunluğu
    r = 0  # Parite biti sayısını belirle

    while (2 ** r) < n:
        r += 1

    syndrome = 0  # Sendrom değeri: hatalı bitin pozisyonunu temsil eder

    # Sendrom hesaplaması (parite bitlerini yeniden kontrol ederek)
    for i in range(r):
        parity_pos = 2 ** i
        count = 0
        for j in range(1, n):  # Son bit genel parite olduğu için hariç tutulur
            if j & parity_pos:
                count += int(hamming_code[j - 1])
        if count % 2 != 0:
            syndrome += parity_pos  # Hatalı parite bitlerinin pozisyonlarının toplamı hata yerini verir

    # Genel pariteyi kontrol et
    data_and_parity = hamming_code[:-1]
    overall_parity_bit = int(hamming_code[-1])
    total_ones = sum(int(b) for b in data_and_parity)
    calculated_overall = total_ones % 2

    corrected = list(hamming_code)  # Geri döndürülecek düzeltmeli kod

    if syndrome == 0 and overall_parity_bit == calculated_overall:
        # Hata yok
        return 0, ''.join(corrected)
    elif syndrome != 0 and overall_parity_bit != calculated_overall:
        # Tek bitlik hata → düzeltilebilir
        pos = syndrome - 1  # 0-index'e çevir
        corrected[pos] = '1' if corrected[pos] == '0' else '0'
        return syndrome, ''.join(corrected)
    elif syndrome == 0 and overall_parity_bit != calculated_overall:
        # Sadece genel parite bitinde hata var
        pos = len(hamming_code) - 1
        corrected[pos] = '1' if corrected[pos] == '0' else '0'
        return pos + 1, ''.join(corrected)
    else:
        # Çift bitli hata → tespit edilebilir ama düzeltilemez
        return -1, ''.join(corrected)

# Hamming SEC-DED simülasyonu için Tkinter tabanlı GUI sınıfı
class HammingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hamming SEC-DED Simülatörü")  # Pencere başlığı

        # Veri girişi etiketi ve kutusu
        tk.Label(root, text="Veri (8, 16 veya 32 bit):").grid(row=0, column=0)
        self.data_entry = tk.Entry(root, width=40)
        self.data_entry.grid(row=0, column=1)

        # Hamming kodu hesapla butonu
        tk.Button(root, text="Hamming Kodu Hesapla", command=self.compute).grid(row=1, column=0, columnspan=2)

        # Kod çıktısı etiketi ve kutusu
        tk.Label(root, text="Kodlu veri:").grid(row=2, column=0)
        self.hamming_output = tk.Entry(root, width=40)
        self.hamming_output.grid(row=2, column=1)

        # Hata pozisyonu etiketi ve giriş kutusu
        tk.Label(root, text="Hata pozisyonu (0 tabanlı):").grid(row=3, column=0)
        self.error_pos_entry = tk.Entry(root, width=10)
        self.error_pos_entry.grid(row=3, column=1, sticky='w')

        # Hata oluştur ve düzeltme butonları
        tk.Button(root, text="Hata Ekle", command=self.introduce_error).grid(row=4, column=0)
        tk.Button(root, text="Hata Tespit & Düzelt", command=self.detect).grid(row=4, column=1)

        # Sonuç mesajlarının gösterileceği etiket
        self.result_label = tk.Label(root, text="", fg="blue")
        self.result_label.grid(row=5, column=0, columnspan=2)

    # Hamming kodunu hesapla ve GUI'de göster
    def compute(self):
        data = self.data_entry.get()
        valid, message = validate_binary_input(data)
        if not valid:
            messagebox.showerror("Hatalı Girdi", message)
            return
        hamming = calculate_hamming(data)
        self.hamming_output.delete(0, tk.END)
        self.hamming_output.insert(0, hamming)
        self.result_label.config(text="Kod hesaplandı.")

    # Belirtilen pozisyonda hata oluştur
    def introduce_error(self):
        code = self.hamming_output.get()
        try:
            pos = int(self.error_pos_entry.get())
        except ValueError:
            messagebox.showerror("Hata", "Geçerli bir sayı girin.")
            return

        if not code or pos < 0 or pos >= len(code):
            messagebox.showerror("Hata", "Hata pozisyonu geçersiz.")
            return

        errored = introduce_error(code, pos)
        self.hamming_output.delete(0, tk.END)
        self.hamming_output.insert(0, errored)
        self.result_label.config(text=f"{pos}. bitte hata oluşturuldu.")

    # Hata tespit et ve gerekiyorsa düzelt
    def detect(self):
        code = self.hamming_output.get()
        syndrome, corrected = detect_and_correct(code)

        if syndrome == 0:
            self.result_label.config(text="Hata tespit edilmedi.")
        elif syndrome == -1:
            self.result_label.config(text="Çift bitli hata tespit edildi! Düzeltilemez.")
        else:
            mesaj = f"Hata bulundu! Bit pozisyonu: {syndrome - 1 if syndrome <= len(code) else 'Genel Parite'}. Düzeltildi."
            self.result_label.config(text=mesaj)
            self.hamming_output.delete(0, tk.END)
            self.hamming_output.insert(0, corrected)

# Programı başlatan ana blok
if __name__ == "__main__":
    root = tk.Tk()
    app = HammingGUI(root)
    root.mainloop()
