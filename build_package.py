#!/usr/bin/env python3
"""
Sticky Note 打包脚本
支持 Linux (.deb, .rpm, .AppImage), Windows (.exe), macOS (.app)

使用方法:
    python build_package.py [platform]
    
    platform: linux, windows, macos, all (默认当前平台)

依赖安装:
    pip install pyinstaller

Linux 额外依赖 (用于生成 .deb/.rpm):
    # Ubuntu/Debian
    sudo apt install ruby ruby-dev rubygems build-essential rpm
    sudo gem install fpm
    
    # 或使用 AppImage (推荐)
    pip install appimage-builder
"""

import os
import sys
import platform
import shutil
import subprocess
from pathlib import Path

# 项目信息
APP_NAME = "sticky-note"
APP_DISPLAY_NAME = "Sticky Note"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "A beautiful sticky note app with Markdown support"
APP_AUTHOR = "Ziyu Liu"
APP_URL = "https://github.com/ziyuliu258/sticky-note"
APP_ICON = "sticky_note.png"
MAIN_SCRIPT = "sticky_note.py"

# 路径
PROJECT_DIR = Path(__file__).parent.absolute()
DIST_DIR = PROJECT_DIR / "dist"
BUILD_DIR = PROJECT_DIR / "build"


def run_command(cmd, cwd=None):
    """运行命令并打印输出"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed with code {result.returncode}")
    return result


def clean_build():
    """清理之前的构建"""
    print("Cleaning previous builds...")
    for d in [DIST_DIR, BUILD_DIR]:
        if d.exists():
            shutil.rmtree(d)
    # 清理 PyInstaller spec 文件
    for f in PROJECT_DIR.glob("*.spec"):
        f.unlink()


def build_pyinstaller(one_file=True):
    """使用 PyInstaller 打包"""
    print("Building with PyInstaller...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--windowed",  # 不显示控制台窗口
        "--noconfirm",  # 覆盖输出目录
    ]
    
    # 添加图标
    icon_path = PROJECT_DIR / APP_ICON
    if not icon_path.exists():
        # 尝试从用户目录获取
        icon_path = Path.home() / ".local/share/icons/sticky_note.png"
    
    if icon_path.exists():
        if platform.system() == "Windows":
            # Windows 需要 .ico 文件
            ico_path = PROJECT_DIR / "sticky_note.ico"
            if ico_path.exists():
                cmd.extend(["--icon", str(ico_path)])
        elif platform.system() == "Darwin":
            # macOS 需要 .icns 文件
            icns_path = PROJECT_DIR / "sticky_note.icns"
            if icns_path.exists():
                cmd.extend(["--icon", str(icns_path)])
        else:
            cmd.extend(["--icon", str(icon_path)])
    
    if one_file:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")
    
    # 添加隐藏导入
    hidden_imports = [
        "markdown_it",
        "mdit_py_plugins",
        "mdit_py_plugins.tasklists",
        "pygments",
        "pygments.lexers",
        "pygments.formatters",
        "PyQt6",
    ]
    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])
    
    cmd.append(str(PROJECT_DIR / MAIN_SCRIPT))
    
    run_command(cmd, cwd=PROJECT_DIR)
    print(f"PyInstaller build complete: {DIST_DIR}")


def create_desktop_file():
    """创建 Linux .desktop 文件"""
    desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={APP_DISPLAY_NAME}
Comment={APP_DESCRIPTION}
Exec={APP_NAME}
Icon={APP_NAME}
Terminal=false
Categories=Utility;TextEditor;
Keywords=note;sticky;markdown;
StartupWMClass={APP_NAME}
"""
    desktop_path = DIST_DIR / f"{APP_NAME}.desktop"
    desktop_path.write_text(desktop_content)
    return desktop_path


def build_deb():
    """构建 .deb 包 (需要 fpm)"""
    print("Building .deb package...")
    
    # 创建临时目录结构
    pkg_dir = BUILD_DIR / "deb_pkg"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制可执行文件
    bin_dir = pkg_dir / "usr/bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(DIST_DIR / APP_NAME, bin_dir / APP_NAME)
    
    # 复制图标
    icon_src = Path.home() / ".local/share/icons/sticky_note.png"
    if icon_src.exists():
        icon_dir = pkg_dir / "usr/share/icons/hicolor/256x256/apps"
        icon_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(icon_src, icon_dir / f"{APP_NAME}.png")
    
    # 复制 desktop 文件
    desktop_dir = pkg_dir / "usr/share/applications"
    desktop_dir.mkdir(parents=True, exist_ok=True)
    create_desktop_file()
    shutil.copy(DIST_DIR / f"{APP_NAME}.desktop", desktop_dir / f"{APP_NAME}.desktop")
    
    # 使用 fpm 打包
    cmd = [
        "fpm",
        "-s", "dir",
        "-t", "deb",
        "-n", APP_NAME,
        "-v", APP_VERSION,
        "--description", APP_DESCRIPTION,
        "--url", APP_URL,
        "--maintainer", APP_AUTHOR,
        "-C", str(pkg_dir),
        "--prefix", "/",
        "-p", str(DIST_DIR / f"{APP_NAME}_{APP_VERSION}_amd64.deb"),
    ]
    
    try:
        run_command(cmd)
        print(f"DEB package created: {DIST_DIR / f'{APP_NAME}_{APP_VERSION}_amd64.deb'}")
    except FileNotFoundError:
        print("Warning: fpm not found. Install with: sudo gem install fpm")


def build_rpm():
    """构建 .rpm 包 (需要 fpm)"""
    print("Building .rpm package...")
    
    # 使用与 deb 相同的目录结构
    pkg_dir = BUILD_DIR / "deb_pkg"
    
    if not pkg_dir.exists():
        print("Error: Run build_deb first to create package structure")
        return
    
    cmd = [
        "fpm",
        "-s", "dir",
        "-t", "rpm",
        "-n", APP_NAME,
        "-v", APP_VERSION,
        "--description", APP_DESCRIPTION,
        "--url", APP_URL,
        "--maintainer", APP_AUTHOR,
        "-C", str(pkg_dir),
        "--prefix", "/",
        "-p", str(DIST_DIR / f"{APP_NAME}-{APP_VERSION}-1.x86_64.rpm"),
    ]
    
    try:
        run_command(cmd)
        print(f"RPM package created: {DIST_DIR / f'{APP_NAME}-{APP_VERSION}-1.x86_64.rpm'}")
    except FileNotFoundError:
        print("Warning: fpm not found. Install with: sudo gem install fpm")


def build_appimage():
    """创建 AppImage (最简单的 Linux 分发方式)"""
    print("Building AppImage...")
    
    appdir = BUILD_DIR / f"{APP_DISPLAY_NAME}.AppDir"
    appdir.mkdir(parents=True, exist_ok=True)
    
    # 复制可执行文件
    shutil.copy(DIST_DIR / APP_NAME, appdir / "AppRun")
    os.chmod(appdir / "AppRun", 0o755)
    
    # 复制图标
    icon_src = Path.home() / ".local/share/icons/sticky_note.png"
    if icon_src.exists():
        shutil.copy(icon_src, appdir / f"{APP_NAME}.png")
    
    # 创建 desktop 文件
    desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={APP_DISPLAY_NAME}
Exec=AppRun
Icon={APP_NAME}
Terminal=false
Categories=Utility;
"""
    (appdir / f"{APP_NAME}.desktop").write_text(desktop_content)
    
    # 下载 appimagetool
    appimagetool = BUILD_DIR / "appimagetool"
    if not appimagetool.exists():
        print("Downloading appimagetool...")
        url = "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
        run_command(["wget", "-O", str(appimagetool), url])
        os.chmod(appimagetool, 0o755)
    
    # 构建 AppImage
    output = DIST_DIR / f"{APP_DISPLAY_NAME}-{APP_VERSION}-x86_64.AppImage"
    run_command([str(appimagetool), str(appdir), str(output)])
    print(f"AppImage created: {output}")


def build_windows():
    """Windows 构建"""
    if platform.system() != "Windows":
        print("Windows builds must be done on Windows")
        print("Tip: Use GitHub Actions for cross-platform builds")
        return
    
    build_pyinstaller(one_file=True)
    
    # 重命名为 .exe
    exe_path = DIST_DIR / f"{APP_NAME}.exe"
    if exe_path.exists():
        final_path = DIST_DIR / f"{APP_DISPLAY_NAME}-{APP_VERSION}-Windows.exe"
        shutil.move(exe_path, final_path)
        print(f"Windows executable: {final_path}")


def build_macos():
    """macOS 构建"""
    if platform.system() != "Darwin":
        print("macOS builds must be done on macOS")
        print("Tip: Use GitHub Actions for cross-platform builds")
        return
    
    build_pyinstaller(one_file=False)
    
    # PyInstaller 在 macOS 上会生成 .app
    app_path = DIST_DIR / f"{APP_NAME}.app"
    if app_path.exists():
        # 创建 DMG
        dmg_path = DIST_DIR / f"{APP_DISPLAY_NAME}-{APP_VERSION}-macOS.dmg"
        run_command([
            "hdiutil", "create", "-volname", APP_DISPLAY_NAME,
            "-srcfolder", str(app_path),
            "-ov", "-format", "UDZO",
            str(dmg_path)
        ])
        print(f"macOS DMG: {dmg_path}")


def build_linux():
    """Linux 完整构建"""
    build_pyinstaller(one_file=True)
    
    # 重命名
    exe_path = DIST_DIR / APP_NAME
    if exe_path.exists():
        final_path = DIST_DIR / f"{APP_NAME}-{APP_VERSION}-linux-x86_64"
        shutil.copy(exe_path, final_path)
        os.chmod(final_path, 0o755)
        print(f"Linux executable: {final_path}")
    
    # 尝试创建 .deb 和 .rpm
    try:
        build_deb()
        build_rpm()
    except Exception as e:
        print(f"Package creation skipped: {e}")
    
    # 尝试创建 AppImage
    try:
        build_appimage()
    except Exception as e:
        print(f"AppImage creation skipped: {e}")


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else platform.system().lower()
    
    clean_build()
    
    if target in ("linux", "Linux"):
        build_linux()
    elif target in ("windows", "Windows", "win"):
        build_windows()
    elif target in ("macos", "Darwin", "mac"):
        build_macos()
    elif target == "all":
        print("Building for current platform only (cross-compilation not supported)")
        print("Use GitHub Actions for multi-platform builds")
        if platform.system() == "Linux":
            build_linux()
        elif platform.system() == "Windows":
            build_windows()
        elif platform.system() == "Darwin":
            build_macos()
    else:
        print(f"Unknown target: {target}")
        print("Usage: python build_package.py [linux|windows|macos|all]")
        sys.exit(1)
    
    print("\n✅ Build complete!")
    print(f"Output directory: {DIST_DIR}")


if __name__ == "__main__":
    main()
