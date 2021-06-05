SuperEncrypt Design Doc
-------------------------

---

### Philosophy

A windows shell application that makes it easy to encrypt and decrypt files on any filesystem with gpg, without any complicated containers or gotchas

-------------------------

### Implementation details

extension: '.soupen'

There will be no container, files are encrypted individually.

The file extension will be renamed to .soupen after encrypting.

Each file will be encrypted using OpenPGP, with the bundled application 'GPG(gnupg)'

It will use symmetric password encryption, and it will ask for the password before encrypting or decrypting

The algorithm will be AES256 with ZIP compression

It will be a Windows shell extension, that works when right clicking on a file, folder, or .soupen file, for encryption and decryption

The .soupen file should contain the original extension before the .soupen

It will be able to encrypt a folder via recursively crawling the folder, and encrypting each file

You should be able to run a .soupen file by double clicking on it and entering your password in a dialog

In running the file, the file will be decrypted to %TEMP% and then executed from there

--

delete non soupen files
find . -type f ! -name "*.soupen" -exec rm {} \;

NOTE: if I was actually giving this to anyone, I would use pythonw so the command prompt didn't show

Computer\HKEY_CURRENT_USER\SOFTWARE\Classes\*\shell\SuperEncrypt
Encrypt with SuperEncrypt

Computer\HKEY_CURRENT_USER\SOFTWARE\Classes\*\shell\SuperEncrypt\command
"D:\Python39\python.exe" "D:\tools\superencrypt\superencrypt.py" "enc" "%1"

Computer\HKEY_CURRENT_USER\SOFTWARE\Classes\.soupen\shell\SuperEncryptDecrypt
Decrypt with SuperEncrypt

Computer\HKEY_CURRENT_USER\SOFTWARE\Classes\.soupen\shell\SuperEncryptDecrypt\command
"D:\Python39\python.exe" "D:\tools\superencrypt\superencrypt.py" "dec" "%1"

Computer\HKEY_CURRENT_USER\SOFTWARE\Classes\Folder\shell\SuperEncryptFolder
Encrypt with SuperEncrypt

Computer\HKEY_CURRENT_USER\SOFTWARE\Classes\Folder\shell\SuperEncryptFolder\command
"D:\Python39\python.exe" "D:\tools\superencrypt\superencrypt.py" "enc" "%1"

the dot is here to make it take precedence, windows uses the alphabet
Computer\HKEY_CURRENT_USER\SOFTWARE\Classes\.soupen\shell\.SuperEncryptOpen
Decrypt and Open

Computer\HKEY_CURRENT_USER\SOFTWARE\Classes\.soupen\shell\.SuperEncryptOpen\command
"D:\Python39\python.exe" "D:\tools\superencrypt\superencrypt.py" "run" "%1"
