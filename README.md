# Encode_Framework
# Project overview
**Uniencode** is a desktop GUI utility for common encoding, cryptography, steganography and light media/QR tooling. It’s implemented in a single, well-commented Python module `unicode_framework.py` (main GUI + logic) and its required packages listed in `requirement.txt`.

The app is intentionally modular: each major capability (Text/Data, Crypto, Neural Network placeholder, Media conversion, QR, Stego) is a separate tab in the GUI so you can iteratively add more capabilities.

---

# Highlights / Features
- **Text/Data**: Base64, URL, HTML encode / decode.
- **Crypto**: AES (EAX) encrypt/decrypt, SHA-256 hashing.  
- **QR**: Generate and save QR codes, basic decoding UI.  
- **Steganography**: Hide/extract text in PNG images using LSB steganography.  
- **Media conversion**: GUI + simulated conversion thread (placeholder for ffmpeg integration).  
- **Cross-platform GUI** built on PySide6.  

---

# Quick start (install & run)

1. **Create & activate a virtual environment (recommended)**
python -m venv venv
# Linux / macOS
source venv/bin/activate
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
**Install dependencies**
pip install -r requirement.txt
**Run the app**
python unicode_framework.py

**Detailed usage — UI walkthrough**
1. Text/Data
Input text, choose Base64, URL, or HTML, then Encode or Decode.

Output shown in read-only box with a "Copy to Clipboard" button.

2. Crypto
Generate a random 128-bit key with Generate Key.

AES Encrypt/Decrypt using AES-EAX mode. Output is base64(nonce || tag || ciphertext).

SHA-256 Hashing also available.

3. Neural Network
Placeholder tab for future AI-related modules.

4. Media
Select input file and output path.

Supported options (simulated): "Audio to MP3" / "Video to H.264".

Runs in a separate thread for non-blocking progress.

5. QR Code
Generate QR codes from text and preview/save as PNG.

Decode QR from image (basic reveal).

6. Stego
Hide text in PNG images with Hide Data.

Extract hidden text with Extract Data.

In-depth code walkthrough
Imports: Optional feature detection for Crypto, Stegano, QR.

Logging & Settings: QSettings used for persistence.

MediaConversionThread: Simulated conversion with progress; replace with ffmpeg for real conversions.

MainWindow: Builds GUI tabs with PySide6 and connects actions.

Crypto details: AES-EAX, key in hex, layout = nonce(16) + tag(16) + ciphertext.

QR: Uses qrcode for generation, stegano for reveal.

Stego: Uses stegano.lsb.hide and stegano.lsb.reveal.

Dependencies & troubleshooting
Declared in requirement.txt:

PySide6

pycryptodome

stegano

qrcode[pil]

Common fixes
ModuleNotFoundError: No module named 'PySide6' → pip install PySide6

AES errors (MAC check failed) → Ensure key & input are correct.

QR decode issues → Use pyzbar or opencv for more robust decoding.

**Security considerations**
Keys are handled in hex → do not store production secrets.

AES-EAX is authenticated (good), but nonce must stay unique.

Steganography is not strong encryption — for casual hiding only.

Input should be validated before adding file/network features.

Extending & roadmap ideas
Replace simulated media conversion with ffmpeg integration.

Use pyzbar for robust QR decoding.

Add CLI interface (uniencode-cli).

Add unit tests for encode/decode, crypto, stego.

Add CI/CD pipeline and PyInstaller packaging.

Packaging & distribution

**Build executable with PyInstaller:**
pip install pyinstaller
pyinstaller --onefile unicode_framework.py
Contributing
Fork this repo.

Create a branch: git checkout -b feat/my-feature.

Commit & push your changes.

Open a Pull Request.

**License**
MIT License (recommended).
Do you want me to also add **badges (like Python version, license, etc.)** and a **demo screenshot placeholder** to make the README look more professional?



