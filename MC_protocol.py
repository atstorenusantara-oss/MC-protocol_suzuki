from pymcprotocol import Type3E

plc = Type3E()
try:
    # Menghubungkan ke PLC
    plc.connect("172.16.134.39", 9000)
    
    # Membaca data dari alamat W3C0 - W3C1 (2 word)
    data = plc.batchread_wordunits("W3C0", 2)
    
    print("------------------------------------------")
    print("Hasil pembacaan alamat W3C0 - W3C1:")
    print("------------------------------------------")
    
    ascii_string = ""
    for val in data:
        # Mitsubishi menyimpan 2 karakter per word
        # Karakter pertama di byte rendah, karakter kedua di byte tinggi
        low_byte = val & 0xFF
        high_byte = (val >> 8) & 0xFF
        
        char1 = chr(low_byte)
        char2 = chr(high_byte)
        
        ascii_string += char1 + char2
        
        hex_val = f"{val:04X}"
        print(f"Alamat Register: {hex_val} -> ASCII: '{char1}{char2}'")

    print("------------------------------------------")
    print(f"String Gabungan (ASCII): {ascii_string}")
    
    try:
        # Konversi string ASCII (misal '1646') ke angka desimal
        decimal_val = int(ascii_string)
        print(f"Hasil Konversi ke Desimal: {decimal_val}")
    except ValueError:
        print("Gagal konversi ke desimal: String mengandung karakter non-angka.")
    print("------------------------------------------")

except Exception as e:
    print(f"Gagal terhubung atau membaca dari PLC: {e}")
finally:
    plc.close()
