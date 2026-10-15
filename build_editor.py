import PyInstaller.__main__
import os
import sys

sys.dont_write_bytecode = True

def build():
    work_dir = os.getcwd()
    
    # Check for skills.csv
    datas = []
    if os.path.exists(os.path.join(work_dir, 'src', 'Data', 'skills.csv')):
        datas.append(('src/Data/skills.csv', 'src/Data'))
    
    # Check for config.json
    if os.path.exists(os.path.join(work_dir, 'PromptBuilder', 'config.json')):
        datas.append(('PromptBuilder/config.json', 'PromptBuilder'))

    # Add Assets if they exist
    if os.path.exists(os.path.join(work_dir, 'Assets')):
        datas.append(('Assets', 'Assets'))

    params = [
        'PromptBuilder/main.py',
        '--name=PromptEditor',
        '--onedir',
        '--noconfirm',
        '--windowed',
        '--clean',
        '--hidden-import=ttkbootstrap',
        '--hidden-import=src',
        '--paths=.', 
        '--paths=PromptBuilder',
    ]
    
    for src, dst in datas:
        params.append(f'--add-data={src}{os.pathsep}{dst}')
    
    print("Start building PromptEditor...")
    PyInstaller.__main__.run(params)
    print("Build finished.")

if __name__ == "__main__":
    build()
