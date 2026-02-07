from pymcprotocol import Type3E

plc = Type3E()
try:
    # Menghubungkan ke PLC
    plc.connect("172.16.134.39", 9000)
    
    # Membaca data dari alamat B0 (sama dengan B000 dalam format Hex)
    # Membaca 5 unit word (masing-masing 16 bit)
    data = plc.batchread_wordunits("B700", 1)
    print(f"Data terbaca dari B0: {data}")

except Exception as e:
    print(f"Gagal terhubung atau membaca dari PLC: {e}")
finally:
    plc.close()
