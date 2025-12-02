# Sticky Note - An Elegant PyQt6-based Sticky Note Application

## Introduction

This application was developed entirely through vibe coding and will continue to evolve in the same spirit. It has been tested on Linux Mint 22.2, but compatibility with other environments has not yet been verified.

## Getting Started

1. Clone the repository.

2. Install the required packages:
```bash
cd sticky_note
pip install -r requirements.txt  # A virtual environment is recommended
```

3. Run the application:
```bash
python3 ./sticky_note.py
```

4. (Optional) Install system-wide on Linux:
```bash
sudo mkdir -p /opt/sticky-note
sudo cp ./sticky_note.py /opt/sticky-note/
```

5. (Optional) Create a `.desktop` file to add it to your application menu:
```bash
cd ~/.local/share/applications/
nano sticky-note.desktop  # Or use any text editor of your choice
```

Add the following content:
```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=Sticky Note
Name[zh_CN]=便签
Comment=A Markdown sticky note application
Comment[zh_CN]=Markdown 便签应用
Exec=python3 /opt/sticky-note/sticky_note.py
Icon=accessories-text-editor
Terminal=false
Categories=Utility;Office;
Keywords=note;sticky;markdown;便签;
StartupNotify=true
```

Then update the desktop database:
```bash
sudo update-desktop-database
```

## Features

- **WYSIWYG Markdown Rendering**  
  Write your notes in Markdown syntax, then right-click and select "Render" to see the formatted result — or simply press `Ctrl+M`.

- **Resizable Window**  
  Drag the edges of the window to resize it as needed.

- **Rich Text Shortcuts**  
  Common text formatting shortcuts are supported: `Ctrl+B` for **bold**, `Ctrl+I` for *italic*, and `Ctrl+U` for <u>underline</u>.

- **Task Scheduling with Date Tags**  
  Use `- [ ]` to create task items, and add `@start(2025-12-01)` or `@due(2025-12-21)` to mark important dates. Click the calendar icon to view all scheduled tasks.

<!-- ## Customization

### Application Icon

The application supports custom icons. To add your own icon:

1. Create an `icons` directory in the project root:
```bash
mkdir icons
```

2. Place your icon file in the `icons` directory as `icon.png` (recommended size: 256x256 pixels)

3. Supported formats: PNG, SVG, ICO, etc.

The application will automatically load `icons/icon.png` if it exists. -->
