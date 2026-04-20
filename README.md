# IdentForge – Identity Generator and Inbox Tool

This is a simple, graphical application for generating fake identities and managing temporary inboxes. It is designed for testing, development, and privacy-focused workflows.

## Main Features

- Generate fake identities (names, addresses, etc.)
- Temporary email inbox management
- View and read messages from inboxes
- Simple, modern graphical interface

## Technologies

- Python 3
- PySide6 (graphical interface)
- Faker (identity generation)
- requests (API communication)
- PyInstaller (for building executables)

## Installation and Running

### 1. Pre-compiled version (recommended)

Find the latest version on the following website: https://github.com/zoardgodor/IdentForge/releases

1. Download `IdentForge_vX.X_WIN64.zip` or `IdentForge_vX.X_WIN64_installer.exe`.
2. For ZIP, extract the archive and run it (for installer, follow the instructions).

(The Installer was created with Inno Setup Compiler)

**You'll need to build the Linux version yourself using PyInstaller; see below**

### 2. Running main.py

Required:
- Python 3
- pip package manager

Install the necessary packages:
```sh
pip install -r requirements.txt
```

Run main.py:
```sh
python main.py
```

### 3. Creating your own build (for developers)

Required:
- Python 3
- pip package manager

Install the necessary packages:
```sh
pip install -r requirements.txt
pip install pyinstaller
```

Then create the exe according to the make_executable.txt file in the repo.

The resulting executable will be in the `dist` folder.

## Usage

1. Start the program (`IdentForge.exe` if built, or run `main.py`).
2. Use the interface to generate fake identities or manage inboxes.
3. View, read, and manage messages as needed.

## License
See: LICENSE
BY INSTALLING AND USING THE PROGRAM, YOU ACCEPT THE LICENSE AGREEMENT.

## Additional Features
- Modern, user-friendly interface
- Advanced error handling and user feedback

**Created by: Gódor Zoárd**

**Contacts for reporting issues:**

GitHub's built-in issue reporting system

EMail: zoard.godor@gmail.com

The software is prohibited from being used for illegal activities!

# Temp mail service: mail.tm

 
