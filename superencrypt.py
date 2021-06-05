import sys
import os
import ntpath # compatibility layer for windows-style paths
import ctypes
import tkinter as tki
import tempfile
import threading
import traceback
from threading import Thread
from pathlib import Path
from tkinter import Tk, Entry, Label, Button
from tkinter.ttk import Progressbar
import subprocess, shlex

#print(sys.argv)

# this will almost always be 2, if it's not something is horribly wrong
assert len(sys.argv) == 3

assert sys.argv[1] == 'enc' or sys.argv[1] == 'dec' or sys.argv[1] == 'run'

def display_mb_error(message):
  ctypes.windll.user32.MessageBoxW(0, message, "SuperEncrypt ERROR", 0x10)

def openTkinterPasswordDialog():
  # tkinter password dialog
  window = Tk()
  window.title('SE')
  window.geometry('270x90')
  window.resizable(0, 0)
  
  # kills the entire program if the password dialog is closed, with a return code of 1
  window.protocol("WM_DELETE_WINDOW", lambda: exit(1))

  # tkinter variable to store the password string
  pass_string_tk = tki.StringVar(window)

  Label(window, text='Password:', width=25, anchor='w').pack(pady=(7, 0))
  entry = Entry(window, width=30, textvariable=pass_string_tk)
  entry.bind('<Return>', lambda _: window.destroy()) # lambda is needed because bind won't call without 1 arg present
  entry.pack()
  entry.focus()
  Button(window, text='Ok', width=15, command=window.destroy).pack(pady=(5, 0))
  
  window.eval('tk::PlaceWindow . center')
  window.mainloop()

  # put the tkinter string into a python string
  pass_string = pass_string_tk.get()
  
  return pass_string

def run_func_with_generic_progress(func, txt):
  window = Tk()
  window.title('SE Progress')
  window.geometry('400x35')
  window.resizable(0, 0)
  Label(window, text=txt).pack(pady=10)
  
  # run a thread that runs the encryption, the window gets closed after it runs because
  # list operations are evaluated in-order by python interpreter
  t1 = Thread(target=lambda: [func(), window.destroy()])
  t1.daemon = True
  t1.start()
  
  window.mainloop()
  
  #t1.join()

# encrypts a file by path using gpg
def encrypt_file_by_name(name):
  gpg_arguments = shlex.split(f'"C:\\Program Files (x86)\\gnupg\\bin\\gpg" --batch --yes --cipher-algo AES256 --compress-algo ZIP --symmetric --passphrase {mypass} --output "{name}.soupen" "{name}"')
  
  CREATE_NO_WINDOW = 0x08000000
  p = subprocess.run(gpg_arguments, check=False, creationflags=CREATE_NO_WINDOW, capture_output=True)
  
  if p.returncode != 0:
    raise Exception(f'Error encrypting {ntpath.basename(name)}', p.stderr)

# decrypts a file by path using gpg
def decrypt_file_by_name(name):
  pathlibn = Path(name)

  gpg_arguments = shlex.split(f'"C:\\Program Files (x86)\\gnupg\\bin\\gpg" --batch --yes --passphrase {mypass} --output "{pathlibn.parent}/{pathlibn.stem}" --decrypt "{name}"')
  
  CREATE_NO_WINDOW = 0x08000000
  p = subprocess.run(gpg_arguments, check=False, creationflags=CREATE_NO_WINDOW, capture_output=True)
  
  if p.returncode != 0:
    raise Exception(f'Error decrypting {ntpath.basename(name)}', p.stderr)

# runs a file by path by decrypting it and running it using gpg
def run_file_by_name(name):
  pathlibn = Path(name)
  
  tmp_file_path = f'"{tempfile.gettempdir()}/{pathlibn.stem}"'
  
  # decrypt to temp directory
  gpg_arguments = shlex.split(f'"C:\\Program Files (x86)\\gnupg\\bin\\gpg" --batch --yes --passphrase {mypass} --output {tmp_file_path} --decrypt "{name}"')
  
  CREATE_NO_WINDOW = 0x08000000
  p = subprocess.run(gpg_arguments, check=False, creationflags=CREATE_NO_WINDOW, capture_output=True)
  
  if p.returncode != 0:
    raise Exception(f'Error running {ntpath.basename(name)}', p.stderr)
  
  # run
  
  os.startfile(tmp_file_path)

action_to_take = sys.argv[1] # action to take (encrypt or decrypt or run)
file_t = ntpath.abspath(sys.argv[2]) # file to operate on

threading.excepthook = lambda e: [display_mb_error(f'SuperEncrypt {action_to_take} operation failed :: \n{e.exc_value.args[0]}\n\n{e.exc_value.args[1].decode("ASCII")}'), os._exit(2)]

# check if file exists

if not ntpath.exists(file_t):
  display_mb_error('File does not exist')

# if it is a file it is 0, directory is 1
file_or_dir = 0

if ntpath.isfile(file_t):
  file_or_dir = 0

if ntpath.isdir(file_t):
  file_or_dir = 1

mypass = openTkinterPasswordDialog()

try:
  if(action_to_take == 'enc'): # encrypt
    if file_or_dir == 0:
      run_func_with_generic_progress(lambda: encrypt_file_by_name(file_t), f"encrypting {ntpath.basename(file_t)}")
    elif file_or_dir == 1:
      # a list of the files
      # it is converted to a list so the length can be used for the progressbar
      file_list = [path for path in Path(file_t).rglob('*') if '.soupen' not in path.suffix and path.is_file()]
      file_list_len = len(file_list)
      # progress bar to display during directory traversal
      
      window = Tk()
      window.title('SE Progress')
      window.geometry('270x60')
      window.resizable(0, 0)
      
      la = Label(window, text='')
      la.pack(pady=(5, 0))
      progress_var = tki.DoubleVar()
      progress = Progressbar(window, orient=tki.HORIZONTAL, variable=progress_var, maximum=file_list_len, mode='determinate').pack(fill=tki.BOTH, pady=(5, 10), padx=10)
      
      pi = 0
      
      for filepath in file_list:
        # progress bar tracking + window update
        pi += 1
        progress_var.set(pi)
        la['text'] = f'encrypting {ntpath.basename(filepath)}'
        window.update()
        
        encrypt_file_by_name(filepath)
      
      window.destroy()
      
    else:
      display_mb_error('Unknown error in fileordir')
  elif(action_to_take == 'dec'): # decrypt
    if file_or_dir == 0:
      run_func_with_generic_progress(lambda: decrypt_file_by_name(file_t), f"decrypting {ntpath.basename(file_t)}")
    else:
      display_mb_error('Passed an invalid path to decrypt, DIRECTORY is not supported')
  elif(action_to_take == 'run'): # now decrypt to %TEMP% + run
    if file_or_dir == 0:
      run_func_with_generic_progress(lambda: run_file_by_name(file_t), f"running {ntpath.basename(file_t)}")
    else:
      display_mb_error('Passed an invalid path to run, DIRECTORY is not supported')
  else:
    display_mb_error('Invalid command passed')
except Exception as e:
  #print(action_to_take)
  #print(file_t)
  #print(file_or_dir)
  #print(e)
  display_mb_error(f'SuperEncrypt {action_to_take} operation failed :: {e}')