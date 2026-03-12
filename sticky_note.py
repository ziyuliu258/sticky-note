import sys
import json
import os
import re
import uuid
from datetime import datetime, date


def maybe_reexec_with_project_venv():
    """Prefer the repo-local virtualenv when launching from a checkout."""
    script_path = os.path.abspath(__file__)
    project_dir = os.path.dirname(script_path)
    venv_python = os.path.join(project_dir, ".venv", "bin", "python")
    if not os.path.exists(venv_python):
        return
    try:
        if os.path.samefile(sys.executable, venv_python):
            return
    except FileNotFoundError:
        pass
    os.execv(venv_python, [venv_python, script_path, *sys.argv[1:]])


maybe_reexec_with_project_venv()

# --- 环境变量设置 (必须在导入 PyQt6 之前设置) ---

# 0. 强制使用 X11 后端 (xcb)
# 在 Wayland 下，无边框窗口的拖拽和调整大小功能会出现问题
# 因为 Wayland 协议限制了应用程序直接移动/调整窗口的能力
# 设置此环境变量可以让 Qt 使用 XWayland 兼容层，恢复正常的窗口操作
if os.environ.get("XDG_SESSION_TYPE") == "wayland":
    os.environ["QT_QPA_PLATFORM"] = "xcb"

# 1. 禁用 Qt 的 Linux 辅助功能支持
# 这可以解决 "QTextCursor::setPosition: Position out of range" 的报错问题
# 该错误通常是由于 Qt 的辅助功能接口 (at-spi) 与某些 Linux 发行版不兼容导致的
os.environ["QT_LINUX_ACCESSIBILITY_ALWAYS_ON"] = "0"

# 2. 尝试修复 fcitx5 输入法支持
# 强制指定输入法模块
# 可选，如果你使用fcitx/fcitx5输入法框架，就应该设置，否则注释掉就好。
os.environ["QT_IM_MODULE"] = "fcitx"

# 尝试添加系统 Qt6 插件路径（包括输入法插件）
# 注意：如果 pip 安装的 PyQt6 版本与系统 Qt 版本差异过大，加载系统插件可能会失败
# 常见的 Qt6 插件路径
qt6_plugin_paths = [
    "/usr/lib/x86_64-linux-gnu/qt6/plugins",  # Debian/Ubuntu
    "/usr/lib/qt6/plugins",                    # Arch/其他发行版
    "/usr/lib64/qt6/plugins",                  # Fedora/RHEL
]
current_paths = os.environ.get("QT_PLUGIN_PATH", "")
for plugin_path in qt6_plugin_paths:
    if os.path.exists(plugin_path) and plugin_path not in current_paths:
        current_paths = f"{current_paths}{os.pathsep}{plugin_path}" if current_paths else plugin_path
if current_paths:
    os.environ["QT_PLUGIN_PATH"] = current_paths


def import_or_exit(import_name, package_name, import_fn):
    """Fail fast with the pip package name instead of a bare ModuleNotFoundError."""
    try:
        return import_fn()
    except ModuleNotFoundError as exc:
        if exc.name != import_name:
            raise
        print(
            f"Missing dependency: {package_name}\n"
            f"Install project dependencies with:\n"
            f"  python -m pip install -r requirements.txt",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc


def _import_markdown_it():
    from markdown_it import MarkdownIt as imported_markdown_it

    return imported_markdown_it


def _import_tasklists_plugin():
    from mdit_py_plugins.tasklists import tasklists_plugin as imported_tasklists_plugin

    return imported_tasklists_plugin


def _import_pygments():
    from pygments import highlight as imported_highlight
    from pygments.formatters import HtmlFormatter as imported_html_formatter
    from pygments.lexers import TextLexer as imported_text_lexer
    from pygments.lexers import get_lexer_by_name as imported_get_lexer_by_name
    from pygments.lexers import guess_lexer as imported_guess_lexer
    from pygments.util import ClassNotFound as imported_class_not_found

    return (
        imported_highlight,
        imported_get_lexer_by_name,
        imported_guess_lexer,
        imported_text_lexer,
        imported_html_formatter,
        imported_class_not_found,
    )


def _import_pyqt6():
    from PyQt6.QtCore import QDate, QEvent, QPoint, QRect, QSize, QTimer, Qt, QUrl
    from PyQt6.QtGui import (
        QAction,
        QColor,
        QDesktopServices,
        QFont,
        QIcon,
        QTextBlockFormat,
        QTextCharFormat,
        QTextCursor,
        QTextDocument,
    )
    from PyQt6.QtWidgets import (
        QApplication,
        QCalendarWidget,
        QColorDialog,
        QDateEdit,
        QDialog,
        QDialogButtonBox,
        QFontDialog,
        QFrame,
        QHBoxLayout,
        QInputDialog,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QMenu,
        QMessageBox,
        QPushButton,
        QSizeGrip,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    return (
        QApplication,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QTextEdit,
        QPushButton,
        QCalendarWidget,
        QLabel,
        QFrame,
        QColorDialog,
        QFontDialog,
        QMenu,
        QSizeGrip,
        QInputDialog,
        QMessageBox,
        QListWidget,
        QListWidgetItem,
        QDialog,
        QDialogButtonBox,
        QLineEdit,
        QDateEdit,
        Qt,
        QPoint,
        QDate,
        QSize,
        QTimer,
        QEvent,
        QRect,
        QUrl,
        QColor,
        QFont,
        QAction,
        QTextCursor,
        QIcon,
        QDesktopServices,
        QTextDocument,
        QTextCharFormat,
        QTextBlockFormat,
    )


MarkdownIt = import_or_exit("markdown_it", "markdown-it-py", lambda: _import_markdown_it())
tasklists_plugin = import_or_exit("mdit_py_plugins", "mdit-py-plugins", lambda: _import_tasklists_plugin())
highlight, get_lexer_by_name, guess_lexer, TextLexer, HtmlFormatter, ClassNotFound = import_or_exit(
    "pygments",
    "pygments",
    lambda: _import_pygments(),
)
(
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QCalendarWidget,
    QLabel,
    QFrame,
    QColorDialog,
    QFontDialog,
    QMenu,
    QSizeGrip,
    QInputDialog,
    QMessageBox,
    QListWidget,
    QListWidgetItem,
    QDialog,
    QDialogButtonBox,
    QLineEdit,
    QDateEdit,
    Qt,
    QPoint,
    QDate,
    QSize,
    QTimer,
    QEvent,
    QRect,
    QUrl,
    QColor,
    QFont,
    QAction,
    QTextCursor,
    QIcon,
    QDesktopServices,
    QTextDocument,
    QTextCharFormat,
    QTextBlockFormat,
) = import_or_exit("PyQt6", "PyQt6", lambda: _import_pyqt6())

# 配置文件路径
DATA_FILE = os.path.expanduser("~/.local/share/sticky_notes_data.json")

# Pygments 代码高亮函数
def highlight_code(code, lang, attrs):
    """使用 Pygments 对代码块进行语法高亮"""
    try:
        if lang:
            lexer = get_lexer_by_name(lang, stripall=True)
        else:
            # 尝试自动检测语言
            try:
                lexer = guess_lexer(code)
            except ClassNotFound:
                lexer = TextLexer()
    except ClassNotFound:
        lexer = TextLexer()
    
    # 使用 One Dark 风格配色的自定义 formatter
    formatter = HtmlFormatter(
        nowrap=True,  # 不包装在 <div> 中
        style='monokai'  # 使用 monokai 风格，接近 One Dark
    )
    
    highlighted = highlight(code, lexer, formatter)
    return highlighted

# 创建 markdown-it 解析器
def create_markdown_parser():
    """创建配置好的 markdown-it 解析器"""
    md = MarkdownIt('gfm-like', {
        'highlight': highlight_code,
        'html': True,
        'linkify': True,
        'typographer': True,
    })
    # 启用任务列表插件
    md.use(tasklists_plugin)
    return md

# 全局解析器实例
md_parser = create_markdown_parser()

class StickyNoteApp(QWidget):
    def __init__(self):
        super().__init__()
        self.data = self.load_data()
        
        # 便签管理
        self.current_note_id = None  # 当前便签 ID
        self.is_markdown_mode = False
        self.markdown_source = ""
        self._original_code_blocks = []
        self._original_empty_lines = []  # 记录原始空行位置
        
        # 默认样式设置
        self.bg_rgb = (40, 44, 52)  # 背景颜色 RGB
        self.bg_opacity = 220  # 背景不透明度 (0-255)
        self.text_color = "#abb2bf"
        self.font_size = 12
        
        # 边缘调整大小相关
        self._resize_edge = None
        self._resize_start_pos = None
        self._resize_start_geometry = None
        self._edge_margin = 12  # 边缘检测区域宽度（像素）
        
        # 自动保存定时器
        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.setInterval(2000)
        self.save_timer.timeout.connect(self.perform_save)

        self.init_ui()
        
        # 加载上次打开的便签，或创建默认便签
        self.load_last_note()
        
        # 默认进入渲染模式
        if self.editor.toPlainText().strip():
            self.render_markdown()

    def init_ui(self):
        # 窗口属性：无边框、透明背景
        # 去掉 Qt.WindowType.WindowStaysOnTopHint，使窗口行为像普通应用一样（可被覆盖）
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(350, 450)

        # 主布局
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # 背景容器（用于实现圆角和背景色）
        self.container = QFrame(self)
        self.container.setObjectName("Container")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(10, 10, 10, 10)
        self.layout.addWidget(self.container)

        # --- 顶部标题栏 (拖拽区 + 便签名称 + 工具) ---
        self.header = QFrame()
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(5, 0, 5, 0)
        
        # 便签名称（可点击切换）
        self.note_label = QPushButton("新建便签")
        self.note_label.setStyleSheet("""
            QPushButton { 
                color: #61afef; 
                font-weight: bold; 
                border: none; 
                background: transparent; 
                text-align: left;
                padding: 2px 5px;
            }
            QPushButton:hover { 
                background-color: rgba(255,255,255,20); 
                border-radius: 3px;
            }
        """)
        self.note_label.clicked.connect(self.show_note_selector)
        
        # 按钮样式
        btn_style = """
            QPushButton { background: transparent; color: #abb2bf; border: none; font-weight: bold; }
            QPushButton:hover { color: #ffffff; }
        """

        # 日历切换按钮
        self.cal_btn = QPushButton("📅")
        self.cal_btn.setToolTip("查看日历（显示任务截止日期）")
        self.cal_btn.setStyleSheet(btn_style)
        self.cal_btn.clicked.connect(self.toggle_calendar)

        # 新建便签按钮
        self.new_btn = QPushButton("＋")
        self.new_btn.setToolTip("新建便签")
        self.new_btn.setStyleSheet(btn_style)
        self.new_btn.clicked.connect(self.create_new_note)

        # 最小化按钮
        self.min_btn = QPushButton("－")
        self.min_btn.setToolTip("最小化")
        self.min_btn.setStyleSheet(btn_style)
        self.min_btn.clicked.connect(self.showMinimized)

        # 最大化/还原按钮
        self.max_btn = QPushButton("□")
        self.max_btn.setToolTip("最大化")
        self.max_btn.setStyleSheet(btn_style)
        self.max_btn.clicked.connect(self.toggle_maximize)

        # 关闭按钮
        self.close_btn = QPushButton("✕")
        self.close_btn.setToolTip("关闭")
        self.close_btn.setStyleSheet("QPushButton { color: #e06c75; font-weight: bold; border: none; background: transparent; } QPushButton:hover { color: #ff0000; }")
        self.close_btn.clicked.connect(self.close)

        self.header_layout.addWidget(self.note_label)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.new_btn)
        self.header_layout.addWidget(self.cal_btn)
        self.header_layout.addWidget(self.min_btn)
        self.header_layout.addWidget(self.max_btn)
        self.header_layout.addWidget(self.close_btn)
        
        self.container_layout.addWidget(self.header)

        # --- 日历控件 (默认隐藏) ---
        self.calendar = QCalendarWidget()
        self.calendar.setStyleSheet("""
            QCalendarWidget { 
                background-color: #2c313a; 
                color: white; 
            }
            QCalendarWidget QTableView { 
                background-color: #2c313a; 
                color: white; 
                selection-background-color: #61afef; 
                selection-color: white; 
                alternate-background-color: #2c313a;
            }
            QCalendarWidget QHeaderView { 
                background-color: #2c313a; 
                color: white; 
            }
            QCalendarWidget QHeaderView::section { 
                background-color: #2c313a; 
                color: white; 
                padding: 4px; 
                border: none; 
            }
            QCalendarWidget QToolButton { 
                color: white; 
                background-color: transparent; 
                icon-size: 20px; 
                font-weight: bold;
            }
            QCalendarWidget QToolButton:hover { 
                background-color: #3e4451; 
                border-radius: 5px; 
            }
            QCalendarWidget QMenu { 
                background-color: #2c313a; 
                color: white; 
            }
            QCalendarWidget QSpinBox { 
                color: white; 
                background-color: #2c313a; 
                selection-background-color: #61afef; 
            }
            QCalendarWidget QAbstractItemView:enabled { 
                color: white; 
                background-color: #2c313a; 
                selection-background-color: #61afef; 
                selection-color: white; 
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar { 
                background-color: #2c313a; 
            }
        """)
        self.calendar.clicked.connect(self.on_date_selected)
        self.calendar.hide()
        self.container_layout.addWidget(self.calendar)

        # --- 文本编辑区 ---
        self.editor = QTextEdit()
        self.editor.setFrameStyle(QFrame.Shape.NoFrame)
        self.editor.setStyleSheet(f"color: {self.text_color}; background: transparent; selection-background-color: #61afef;")
        self.editor.setFont(QFont("PingFang SC", self.font_size))
        self.editor.textChanged.connect(self.save_current_note)
        
        # 自定义右键菜单
        self.editor.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.editor.customContextMenuRequested.connect(self.show_context_menu)
        
        # 安装事件过滤器以处理 Markdown 模式下的点击和快捷键
        self.editor.installEventFilter(self)
        self.editor.viewport().installEventFilter(self)
        
        self.container_layout.addWidget(self.editor)

        # --- 底部调整大小的手柄 ---
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        size_grip = QSizeGrip(self)
        size_grip.setStyleSheet("background: transparent; width: 15px; height: 15px;")
        bottom_layout.addWidget(size_grip)
        self.container_layout.addLayout(bottom_layout)

        # --- 样式渲染 ---
        self.update_style()
        
        # 启用鼠标追踪，使得鼠标移动时（即使没有按下按钮）也能触发 mouseMoveEvent
        # 这样可以在鼠标接近窗口边缘时更新光标形状
        # 需要为所有子控件也启用，否则子控件会拦截鼠标事件
        self.setMouseTracking(True)
        self.container.setMouseTracking(True)
        self.header.setMouseTracking(True)
        self.editor.setMouseTracking(True)
        self.editor.viewport().setMouseTracking(True)
        
        # 为子控件安装事件过滤器，以便在子控件上移动鼠标时也能更新光标
        self.container.installEventFilter(self)
        self.header.installEventFilter(self)
        
        # 优化：移除 QGraphicsDropShadowEffect
        # 在 Linux 上，透明窗口的软件模糊阴影极其消耗 CPU 资源，会导致严重的界面卡顿和拖拽延迟。
        # 建议由窗口管理器 (Compositor) 处理阴影，或者为了性能牺牲这个效果。
        # shadow = QGraphicsDropShadowEffect(self)
        # shadow.setBlurRadius(20)
        # shadow.setXOffset(0)
        # shadow.setYOffset(5)
        # shadow.setColor(QColor(0, 0, 0, 100))
        # self.container.setGraphicsEffect(shadow)

    def update_style(self):
        """应用CSS样式，控制圆角和背景"""
        r, g, b = self.bg_rgb
        self.container.setStyleSheet(f"""
            #Container {{
                background-color: rgba({r}, {g}, {b}, {self.bg_opacity});
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 20);
            }}
        """)

    # --- 逻辑处理 ---

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self.max_btn.setText("□")
        else:
            self.showMaximized()
            self.max_btn.setText("❐")

    def toggle_calendar(self):
        if self.calendar.isVisible():
            self.calendar.hide()
        else:
            self.calendar.show()
            # 刷新日历以显示有任务的日期
            self.update_calendar_marks()

    def update_calendar_marks(self):
        """更新日历上标记有任务截止日期的日期"""
        # 重置日历样式
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
        
        # 搜集所有便签中的任务日期
        task_dates = {}  # date_str -> [(note_title, task_name, is_due), ...]
        
        for note_id, note_info in self.data.get('notes', {}).items():
            content = note_info.get('content', '')
            note_title = note_info.get('title', '未命名')
            
            # 匹配任务行：- [ ] 或 - [x] 任务名 @start(日期) @due(日期)
            for line in content.split('\n'):
                if line.strip().startswith(('- [ ]', '- [x]', '- [X]', '☐', '☑')):
                    # 提取 @due(日期)
                    due_match = re.search(r'@due\((\d{4}-\d{2}-\d{2})\)', line)
                    if due_match:
                        date_str = due_match.group(1)
                        task_name = re.sub(r'@\w+\([^)]+\)', '', line).strip()
                        task_name = re.sub(r'^[-\s]*\[.\]\s*', '', task_name).strip()
                        task_name = re.sub(r'^[☐☑]\s*', '', task_name).strip()
                        if date_str not in task_dates:
                            task_dates[date_str] = []
                        task_dates[date_str].append((note_title, task_name, True))
                    
                    # 提取 @start(日期)
                    start_match = re.search(r'@start\((\d{4}-\d{2}-\d{2})\)', line)
                    if start_match:
                        date_str = start_match.group(1)
                        task_name = re.sub(r'@\w+\([^)]+\)', '', line).strip()
                        task_name = re.sub(r'^[-\s]*\[.\]\s*', '', task_name).strip()
                        task_name = re.sub(r'^[☐☑]\s*', '', task_name).strip()
                        if date_str not in task_dates:
                            task_dates[date_str] = []
                        task_dates[date_str].append((note_title, task_name, False))
        
        # 标记日历上的日期
        due_format = QTextCharFormat()
        due_format.setBackground(QColor("#e06c75"))  # 红色背景 - 截止日期
        due_format.setForeground(QColor("#ffffff"))
        
        start_format = QTextCharFormat()
        start_format.setBackground(QColor("#61afef"))  # 蓝色背景 - 开始日期
        start_format.setForeground(QColor("#ffffff"))
        
        both_format = QTextCharFormat()
        both_format.setBackground(QColor("#c678dd"))  # 紫色背景 - 两者都有
        both_format.setForeground(QColor("#ffffff"))
        
        for date_str, tasks in task_dates.items():
            try:
                qdate = QDate.fromString(date_str, "yyyy-MM-dd")
                if qdate.isValid():
                    has_due = any(t[2] for t in tasks)
                    has_start = any(not t[2] for t in tasks)
                    if has_due and has_start:
                        self.calendar.setDateTextFormat(qdate, both_format)
                    elif has_due:
                        self.calendar.setDateTextFormat(qdate, due_format)
                    else:
                        self.calendar.setDateTextFormat(qdate, start_format)
            except:
                pass

    def on_date_selected(self, qdate):
        """当日历中选择日期时，显示该日期的任务"""
        date_str = qdate.toString("yyyy-MM-dd")
        self.show_tasks_for_date(date_str)

    def show_tasks_for_date(self, date_str):
        """显示指定日期的所有任务"""
        tasks = []
        for note_id, note_info in self.data.get('notes', {}).items():
            content = note_info.get('content', '')
            note_title = note_info.get('title', '未命名')
            
            for line in content.split('\n'):
                if line.strip().startswith(('- [ ]', '- [x]', '- [X]', '☐', '☑')):
                    if f'@due({date_str})' in line or f'@start({date_str})' in line:
                        task_name = re.sub(r'@\w+\([^)]+\)', '', line).strip()
                        task_name = re.sub(r'^[-\s]*\[.\]\s*', '', task_name).strip()
                        task_name = re.sub(r'^[☐☑]\s*', '', task_name).strip()
                        is_due = f'@due({date_str})' in line
                        is_start = f'@start({date_str})' in line
                        tasks.append((note_id, note_title, task_name, is_due, is_start))
        
        if tasks:
            from PyQt6.QtWidgets import QMessageBox
            msg = f"📅 {date_str} 的任务:\n\n"
            for note_id, note_title, task_name, is_due, is_start in tasks:
                markers = []
                if is_start:
                    markers.append("🟢开始")
                if is_due:
                    markers.append("🔴截止")
                msg += f"• [{note_title}] {task_name} ({', '.join(markers)})\n"
            QMessageBox.information(self, "任务日期", msg)

    def load_data(self):
        """加载数据，支持新旧格式"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    # 检查是否是新格式
                    if 'notes' in data and 'settings' in data:
                        return data
                    else:
                        # 旧格式：按日期存储的内容，迁移到新格式
                        return self.migrate_old_data(data)
            except:
                return {'notes': {}, 'settings': {}}
        return {'notes': {}, 'settings': {}}

    def migrate_old_data(self, old_data):
        """将旧的日期格式数据迁移到新的便签格式"""
        new_data = {'notes': {}, 'settings': {}}
        
        for date_str, content in old_data.items():
            if content and content.strip():
                note_id = str(uuid.uuid4())
                # 去掉 MARKDOWN_SOURCE: 前缀
                if content.startswith("MARKDOWN_SOURCE:"):
                    content = content[16:]
                new_data['notes'][note_id] = {
                    'title': f"便签 ({date_str})",
                    'content': content,
                    'created': date_str,
                    'modified': date_str
                }
                # 设置最后一个为当前便签
                new_data['settings']['last_note_id'] = note_id
        
        return new_data

    def save_data(self):
        # 确保目录存在
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, 'w') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def load_last_note(self):
        """加载上次打开的便签，如果没有则创建新便签"""
        last_note_id = self.data.get('settings', {}).get('last_note_id')
        notes = self.data.get('notes', {})
        
        if last_note_id and last_note_id in notes:
            self.load_note(last_note_id)
        elif notes:
            # 有便签但上次的ID无效，加载第一个
            first_id = list(notes.keys())[0]
            self.load_note(first_id)
        else:
            # 没有便签，创建一个新的
            self.create_new_note()

    def load_note(self, note_id):
        """加载指定ID的便签"""
        notes = self.data.get('notes', {})
        if note_id not in notes:
            return
        
        note_info = notes[note_id]
        self.current_note_id = note_id
        
        # 更新标题栏
        title = note_info.get('title', '未命名便签')
        self.note_label.setText(title)
        
        # 加载内容
        self.editor.blockSignals(True)
        try:
            content = note_info.get('content', '')
            self.markdown_source = content
            self.editor.setPlainText(content)
            self.is_markdown_mode = False
        finally:
            self.editor.blockSignals(False)
        
        # 保存为上次打开的便签
        if 'settings' not in self.data:
            self.data['settings'] = {}
        self.data['settings']['last_note_id'] = note_id

    def create_new_note(self):
        """创建新便签"""
        from PyQt6.QtWidgets import QInputDialog
        
        title, ok = QInputDialog.getText(self, "新建便签", "请输入便签名称:", text="新便签")
        if not ok or not title.strip():
            return
        
        note_id = str(uuid.uuid4())
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if 'notes' not in self.data:
            self.data['notes'] = {}
        
        self.data['notes'][note_id] = {
            'title': title.strip(),
            'content': '',
            'created': now,
            'modified': now
        }
        
        self.load_note(note_id)
        self.save_data()

    def show_note_selector(self):
        """显示便签选择菜单"""
        menu = QMenu(self)
        
        notes = self.data.get('notes', {})
        
        if notes:
            for note_id, note_info in notes.items():
                title = note_info.get('title', '未命名')
                action = QAction(title, self)
                action.setData(note_id)
                if note_id == self.current_note_id:
                    action.setCheckable(True)
                    action.setChecked(True)
                action.triggered.connect(lambda checked, nid=note_id: self.switch_note(nid))
                menu.addAction(action)
            
            menu.addSeparator()
        
        # 重命名当前便签
        rename_action = QAction("✏️ 重命名当前便签", self)
        rename_action.triggered.connect(self.rename_current_note)
        menu.addAction(rename_action)
        
        # 删除当前便签
        delete_action = QAction("🗑️ 删除当前便签", self)
        delete_action.triggered.connect(self.delete_current_note)
        menu.addAction(delete_action)
        
        menu.exec(self.note_label.mapToGlobal(self.note_label.rect().bottomLeft()))

    def switch_note(self, note_id):
        """切换到指定便签"""
        # 先保存当前便签
        self.perform_save()
        # 加载新便签
        self.load_note(note_id)

    def rename_current_note(self):
        """重命名当前便签"""
        from PyQt6.QtWidgets import QInputDialog
        
        notes = self.data.get('notes', {})
        if self.current_note_id not in notes:
            return
        
        current_title = notes[self.current_note_id].get('title', '')
        new_title, ok = QInputDialog.getText(self, "重命名便签", "请输入新名称:", text=current_title)
        
        if ok and new_title.strip():
            notes[self.current_note_id]['title'] = new_title.strip()
            self.note_label.setText(new_title.strip())
            self.save_data()

    def delete_current_note(self):
        """删除当前便签"""
        from PyQt6.QtWidgets import QMessageBox
        
        notes = self.data.get('notes', {})
        if self.current_note_id not in notes:
            return
        
        title = notes[self.current_note_id].get('title', '未命名')
        reply = QMessageBox.question(
            self, "确认删除",
            f'确定要删除便签 "{title}" 吗？\n此操作不可恢复。',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            del notes[self.current_note_id]
            self.save_data()
            
            # 加载其他便签或创建新便签
            if notes:
                first_id = list(notes.keys())[0]
                self.load_note(first_id)
            else:
                self.create_new_note()

    def save_current_note(self):
        # 重置定时器，实现防抖动，避免频繁写入文件和处理 HTML
        self.save_timer.start()

    def perform_save(self):
        """保存当前便签内容"""
        if not self.current_note_id:
            return
        
        notes = self.data.get('notes', {})
        if self.current_note_id not in notes:
            return
        
        if self.is_markdown_mode:
            # 如果处于 Markdown 渲染模式，先转换回源码再保存
            self.markdown_source = self.get_markdown_from_rendered()
            content = self.markdown_source
        else:
            # 源码模式
            content = self.editor.toPlainText()
            self.markdown_source = content
        
        notes[self.current_note_id]['content'] = content
        notes[self.current_note_id]['modified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_data()

    # --- 右键菜单功能 ---

    def show_context_menu(self, pos):
        menu = QMenu(self)
        
        markdown_action = QAction("Markdown 渲染 (Ctrl+M)", self)
        markdown_action.triggered.connect(self.render_markdown)
        menu.addAction(markdown_action)

        menu.addSeparator()

        checkbox_action = QAction("插入复选框 ☑", self)
        checkbox_action.triggered.connect(self.insert_checkbox)
        menu.addAction(checkbox_action)

        font_action = QAction("设置字体/大小", self)
        font_action.triggered.connect(self.change_font)
        menu.addAction(font_action)
        
        color_action = QAction("设置背景颜色", self)
        color_action.triggered.connect(self.change_bg_color)
        menu.addAction(color_action)

        opacity_action = QAction("设置不透明度", self)
        opacity_action.triggered.connect(self.change_opacity)
        menu.addAction(opacity_action)

        menu.exec(self.editor.mapToGlobal(pos))

    def render_markdown(self):
        """切换 Markdown 源码和渲染视图"""
        if self.is_markdown_mode:
            # 切换回源码模式
            # 先从渲染视图获取最新的 Markdown 源码
            self.markdown_source = self.get_markdown_from_rendered()
            
            # 清除所有格式后再设置纯文本，避免继承渲染模式的格式
            self.editor.blockSignals(True)
            try:
                self.editor.clear()
                # 重置为默认格式
                default_fmt = QTextCharFormat()
                self.editor.setCurrentCharFormat(default_fmt)
                self.editor.setPlainText(self.markdown_source)
            finally:
                self.editor.blockSignals(False)
            
            self.is_markdown_mode = False
        else:
            # 切换到渲染模式
            self.markdown_source = self.editor.toPlainText()
            # 保存原始代码块内容，用于还原时保真
            self._original_code_blocks = re.findall(r'```[\s\S]*?```', self.markdown_source)
            # 保存原始引用块内容，用于还原时保真
            self._original_blockquotes = self._extract_blockquotes(self.markdown_source)
            # 保存原始的空行位置模式（用于还原时保持一致）
            self._original_empty_lines = [i for i, line in enumerate(self.markdown_source.split('\n')) if line.strip() == '']
            self.update_markdown_view()
            # 允许在渲染模式下编辑
            self.editor.setReadOnly(False) 
            self.is_markdown_mode = True
    
    def _extract_blockquotes(self, markdown_text):
        """提取 Markdown 中的所有引用块（包括连续的多行引用）"""
        lines = markdown_text.split('\n')
        blockquotes = []
        current_quote = []
        
        for line in lines:
            # 检查是否是引用行（以 > 开头，允许前面有空格）
            if re.match(r'^\s*>', line):
                current_quote.append(line)
            else:
                # 非引用行
                if current_quote:
                    # 保存之前的引用块
                    blockquotes.append('\n'.join(current_quote))
                    current_quote = []
        
        # 处理文件末尾的引用块
        if current_quote:
            blockquotes.append('\n'.join(current_quote))
        
        return blockquotes

    def get_markdown_from_rendered(self):
        """从渲染视图中提取 Markdown 源码
        
        简化策略：直接返回保存的原始 markdown_source，
        仅更新复选框状态（因为用户可能在渲染模式下点击复选框）
        """
        # 返回保存的原始 markdown_source
        # 复选框状态已经在 eventFilter 中通过 update_markdown_source_checkbox 实时更新了
        return self.markdown_source

    def update_markdown_view(self):
        """更新 Markdown 渲染视图（用于刷新字体大小或内容）"""
        if not self.markdown_source:
            return

        # 使用 markdown-it-py 转换 HTML
        html = md_parser.render(self.markdown_source)
        
        # 修复引用块内的换行问题
        # markdown-it 渲染的 <blockquote> 内容中，换行符被保留但 Qt 不会显示为换行
        # 需要把 <blockquote>...</blockquote> 内部的换行符转换成 <br> 标签
        def fix_blockquote_newlines(match):
            content = match.group(1)
            # 将换行符替换为 <br>，但保留 HTML 标签
            # 先处理 <p> 标签内的换行
            content = re.sub(r'(<p>)(.*?)(</p>)', 
                           lambda m: m.group(1) + m.group(2).replace('\n', '<br>') + m.group(3), 
                           content, flags=re.DOTALL)
            return f'<blockquote>{content}</blockquote>'
        
        html = re.sub(r'<blockquote>(.*?)</blockquote>', fix_blockquote_newlines, html, flags=re.DOTALL)

        def replace_blockquote(match):
            content = match.group(1)

            # markdown-it 在引用块里可能生成 <p>、<ul>/<ol>、<li> 等结构。
            # 这里先把常见块级标签拍平成“按行展示”的文本，再统一加左侧竖线。
            content = re.sub(r'</p>\s*<p>', '<br>', content)
            content = re.sub(r'<br\s*/?>', '\n', content)
            content = re.sub(r'</li>\s*', '\n', content)
            content = re.sub(r'<li[^>]*>\s*', '• ', content)
            content = re.sub(r'</?(ul|ol|p)>', '', content)
            content = content.strip()

            # 处理多行内容，但左侧只绘制一根连续竖线，避免字符竖线断开。
            formatted_lines = []
            for line in content.split('\n'):
                line = line.strip()
                if line:
                    formatted_lines.append(f'<span style="color: #6f7785;">{line}</span>')

            inner_html = "<br>".join(formatted_lines)
            return (
                '<div style="margin: 4px 0 6px 0; '
                'line-height: 1.15;">'
                f'{inner_html}'
                '</div>'
            )

        html = re.sub(r'<blockquote>(.*?)</blockquote>', replace_blockquote, html, flags=re.DOTALL)
        
        # 后处理 HTML：将 mdit-py-plugins 生成的任务列表转换为可点击的链接
        # mdit-py-plugins 生成的格式: 
        # <li class="task-list-item"><input class="task-list-item-checkbox" disabled="disabled" type="checkbox">
        # <li class="task-list-item"><input class="task-list-item-checkbox" checked="checked" disabled="disabled" type="checkbox">
        
        self._checkbox_count = 0
        
        def checkbox_replacer(match):
            input_tag = match.group(1)  # 整个 input 标签内容
            idx = self._checkbox_count
            self._checkbox_count += 1
            
            # 检查是否包含 checked 属性
            is_checked = 'checked' in input_tag
            icon = "☑\ufe0e" if is_checked else "☐\ufe0e"
            color = "#98c379" if is_checked else "#e06c75"
            
            return f'<li class="task-list-item" style="list-style-type: none;"><a href="checkbox:{idx}" style="text-decoration: none; color: {color}; font-weight: bold; font-family: \'Symbola\', \'Segoe UI Symbol\', \'DejaVu Sans\', sans-serif;">{icon}</a> '
        
        # 匹配 mdit-py-plugins 生成的任务列表格式
        html = re.sub(r'<li class="task-list-item"><input([^>]*)>\s*', checkbox_replacer, html)

        # 获取 Pygments 生成的 CSS (One Dark 风格的配色)
        pygments_css = HtmlFormatter(style='monokai').get_style_defs('.highlight')
        
        # 动态 CSS - 增强版，支持语法高亮
        style = f"""
        <style>
            body {{ 
                font-size: {self.font_size}pt; 
                color: {self.text_color}; 
                font-family: 'Ubuntu', sans-serif;
            }}
            code {{ 
                background-color: #3e4451; 
                padding: 2px; 
                border-radius: 3px; 
                font-family: 'Ubuntu Mono', 'Consolas', 'Monaco', monospace;
                color: #d19a66;
            }}
            pre {{
                background-color: #282c34;
                padding: 10px;
                border-radius: 5px;
                margin: 5px 0;
                font-family: 'Ubuntu Mono', 'Consolas', 'Monaco', monospace;
                overflow-x: auto;
            }}
            pre code {{
                background-color: transparent;
                padding: 0;
                border-radius: 0;
                color: #abb2bf;
            }}
            /* Pygments 语法高亮颜色 - One Dark 风格 */
            .highlight {{ background-color: #282c34; }}
            .c, .c1, .cm {{ color: #5c6370; font-style: italic; }} /* 注释 */
            .k, .kn, .kd, .kc {{ color: #c678dd; }} /* 关键字 */
            .s, .s1, .s2, .sb {{ color: #98c379; }} /* 字符串 */
            .n, .na {{ color: #abb2bf; }} /* 名称 */
            .nf, .fm {{ color: #61afef; }} /* 函数名 */
            .nc {{ color: #e5c07b; }} /* 类名 */
            .nb {{ color: #e5c07b; }} /* 内置函数 */
            .mi, .mf, .mo, .mh {{ color: #d19a66; }} /* 数字 */
            .o, .ow {{ color: #56b6c2; }} /* 运算符 */
            .p {{ color: #abb2bf; }} /* 标点 */
            .nv, .vi {{ color: #e06c75; }} /* 变量 */
            .bp {{ color: #e5c07b; }} /* 内置常量 */
            .nn {{ color: #e5c07b; }} /* 模块名 */
            ul, ol {{ 
                -qt-list-indent: 1;
                margin: 0px; 
                padding: 0px;
            }}
            li {{ 
                margin-left: -24px;
                margin-bottom: 0.2em; 
            }}
            .task-list-item {{
                list-style-type: none;
            }}
            p {{
                margin-bottom: 0.5em;
            }}
            blockquote {{
                margin: 8px 0;
                padding: 8px 12px;
                background-color: #333842;
                border: 1px solid #454c59;
                border-radius: 10px;
                color: #c8d0df;
            }}
            blockquote p {{
                margin: 0.2em 0;
            }}
            blockquote ul, blockquote ol {{
                margin: 0.25em 0 0.25em 1.2em;
                padding: 0;
            }}
            blockquote li {{
                margin-left: 0;
                margin-bottom: 0.15em;
            }}
            a {{
                cursor: pointer;
                text-decoration: none;
            }}
            /* 普通表格样式 */
            table {{
                border-collapse: collapse;
                margin: 8px 0;
                width: 100%;
            }}
            th, td {{
                border: 1px solid #5c6370;
                padding: 6px 10px;
                text-align: left;
            }}
            th {{
                background-color: #3e4451;
                color: #e5c07b;
                font-weight: bold;
            }}
            td {{
                background-color: #2c313a;
            }}
            tr:hover td {{
                background-color: #3e4451;
            }}
        </style>
        """
        self.editor.setHtml(style + html)

    def update_markdown_source_checkbox(self, checkbox_index, new_checked):
        """更新 markdown_source 中第 checkbox_index 个复选框的状态"""
        lines = self.markdown_source.split('\n')
        new_lines = []
        current_checkbox_idx = 0
        
        for line in lines:
            # 匹配任务列表行：- [ ] 或 - [x] 或 - [X]
            match = re.match(r'^(\s*-\s*)\[([ xX])\](.*)$', line)
            if match:
                if current_checkbox_idx == checkbox_index:
                    # 找到目标复选框，切换状态
                    prefix = match.group(1)
                    suffix = match.group(3)
                    new_state = 'x' if new_checked else ' '
                    new_lines.append(f"{prefix}[{new_state}]{suffix}")
                else:
                    new_lines.append(line)
                current_checkbox_idx += 1
            else:
                new_lines.append(line)
        
        self.markdown_source = '\n'.join(new_lines)

    def eventFilter(self, obj, event):
        # 处理 Markdown 模式下的交互
        if self.is_markdown_mode:
            # 1. 处理鼠标点击复选框
            if obj == self.editor.viewport() and event.type() == QEvent.Type.MouseButtonRelease:
                if event.button() == Qt.MouseButton.LeftButton:
                    cursor = self.editor.cursorForPosition(event.pos())
                    
                    # 尝试向右选择一个字符，看是否是复选框
                    cursor_right = self.editor.cursorForPosition(event.pos())
                    cursor_right.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor)
                    fmt_right = cursor_right.charFormat()
                    href_right = fmt_right.anchorHref()
                    selected_right = cursor_right.selectedText()
                    
                    # 检查是否点击到复选框
                    if href_right.startswith("checkbox:") and ("☑" in selected_right or "☐" in selected_right):
                        is_checked = "☑" in selected_right
                        new_checked = not is_checked
                        new_char = "☐\ufe0e" if is_checked else "☑\ufe0e"
                        new_color = "#e06c75" if is_checked else "#98c379"
                        
                        # 获取复选框索引
                        checkbox_index = int(href_right.split(':')[1])
                        
                        new_fmt = QTextCharFormat()
                        new_fmt.setForeground(QColor(new_color))
                        new_fmt.setAnchor(True)
                        new_fmt.setAnchorHref(href_right)
                        new_fmt.setFontFamilies(["Symbola", "Segoe UI Symbol", "DejaVu Sans", "sans-serif"])
                        
                        self.editor.blockSignals(True)
                        try:
                            cursor_right.insertText(new_char, new_fmt)
                        finally:
                            self.editor.blockSignals(False)
                        
                        # 立即更新 markdown_source
                        self.update_markdown_source_checkbox(checkbox_index, new_checked)
                        self.save_current_note()
                        return True
                    
                    # 尝试向左
                    cursor_left = self.editor.cursorForPosition(event.pos())
                    cursor_left.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor)
                    fmt_left = cursor_left.charFormat()
                    href_left = fmt_left.anchorHref()
                    selected_left = cursor_left.selectedText()
                    
                    if href_left.startswith("checkbox:") and ("☑" in selected_left or "☐" in selected_left):
                        is_checked = "☑" in selected_left
                        new_checked = not is_checked
                        new_char = "☐\ufe0e" if is_checked else "☑\ufe0e"
                        new_color = "#e06c75" if is_checked else "#98c379"
                        
                        # 获取复选框索引
                        checkbox_index = int(href_left.split(':')[1])
                        
                        new_fmt = QTextCharFormat()
                        new_fmt.setForeground(QColor(new_color))
                        new_fmt.setAnchor(True)
                        new_fmt.setAnchorHref(href_left)
                        new_fmt.setFontFamilies(["Symbola", "Segoe UI Symbol", "DejaVu Sans", "sans-serif"])
                        
                        self.editor.blockSignals(True)
                        try:
                            cursor_left.insertText(new_char, new_fmt)
                        finally:
                            self.editor.blockSignals(False)
                        
                        # 立即更新 markdown_source
                        self.update_markdown_source_checkbox(checkbox_index, new_checked)
                        self.save_current_note()
                        return True
                    
                    # 不是复选框点击，让默认行为继续
            
            # 2. 处理快捷键
            if event.type() == QEvent.Type.KeyPress:
                if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                    if event.key() == Qt.Key.Key_M:
                        self.render_markdown()
                        return True
                    elif event.key() == Qt.Key.Key_Equal:
                        self.adjust_font_size(1)
                        return True
                    elif event.key() == Qt.Key.Key_Minus:
                        self.adjust_font_size(-1)
                        return True
                    elif event.key() == Qt.Key.Key_B:
                        self.toggle_bold()
                        return True
                    elif event.key() == Qt.Key.Key_I:
                        self.toggle_italic()
                        return True
                    elif event.key() == Qt.Key.Key_U:
                        # 渲染模式下允许添加下划线（纯视觉效果，切换回源码时会丢弃）
                        self.toggle_underline()
                        return True

        # 非 Markdown 模式下也支持格式快捷键
        if event.type() == QEvent.Type.KeyPress:
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                if event.key() == Qt.Key.Key_B:
                    self.toggle_bold()
                    return True
                elif event.key() == Qt.Key.Key_I:
                    self.toggle_italic()
                    return True
                elif event.key() == Qt.Key.Key_U:
                    self.toggle_underline()
                    return True

        # 处理子控件上的鼠标移动事件，更新边缘光标形状
        if event.type() == QEvent.Type.MouseMove:
            # 将子控件的局部坐标转换为主窗口坐标
            global_pos = event.globalPosition().toPoint()
            local_pos = self.mapFromGlobal(global_pos)
            edge = self._get_resize_edge(local_pos)
            self._update_cursor_shape(edge)

        return super().eventFilter(obj, event)

    def toggle_bold(self):
        """切换加粗"""
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            # 获取选区起始位置的格式来判断当前状态
            fmt = cursor.charFormat()
            current_weight = fmt.fontWeight()
            
            # fontWeight() 返回整数: Normal=400, Bold=700
            # 创建新格式
            new_fmt = QTextCharFormat()
            if current_weight >= 600:  # 600以上视为粗体
                new_fmt.setFontWeight(QFont.Weight.Normal)
            else:
                new_fmt.setFontWeight(QFont.Weight.Bold)
            cursor.mergeCharFormat(new_fmt)
            self.editor.setTextCursor(cursor)
        else:
            # 无选中时，切换当前光标位置的格式（影响后续输入）
            fmt = self.editor.currentCharFormat()
            current_weight = fmt.fontWeight()
            if current_weight >= 600:
                fmt.setFontWeight(QFont.Weight.Normal)
            else:
                fmt.setFontWeight(QFont.Weight.Bold)
            self.editor.setCurrentCharFormat(fmt)

    def toggle_italic(self):
        """切换斜体"""
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            fmt = cursor.charFormat()
            new_fmt = QTextCharFormat()
            new_fmt.setFontItalic(not fmt.fontItalic())
            cursor.mergeCharFormat(new_fmt)
            self.editor.setTextCursor(cursor)
        else:
            fmt = self.editor.currentCharFormat()
            fmt.setFontItalic(not fmt.fontItalic())
            self.editor.setCurrentCharFormat(fmt)

    def toggle_underline(self):
        """切换下划线"""
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            # 只在有选中文本时才应用下划线
            selected_text = cursor.selectedText()
            # 排除特殊字符（复选框等）
            if selected_text and not any(c in selected_text for c in ['☐', '☑', '\ufffc']):
                fmt = cursor.charFormat()
                new_fmt = QTextCharFormat()
                new_fmt.setFontUnderline(not fmt.fontUnderline())
                cursor.mergeCharFormat(new_fmt)
                self.editor.setTextCursor(cursor)
        elif not self.is_markdown_mode:
            # 非 Markdown 模式下，允许无选中时切换格式（影响后续输入）
            fmt = self.editor.currentCharFormat()
            fmt.setFontUnderline(not fmt.fontUnderline())
            self.editor.setCurrentCharFormat(fmt)

    def toggle_checkbox_state(self, target_idx):
        """切换第 target_idx 个复选框的状态 (原地更新)"""
        # 我们不再重新渲染整个 Markdown，而是直接修改文档中的 HTML/字符
        # 这样可以保留光标位置，并支持“渲染模式下编辑”
        
        # 遍历文档查找目标复选框
        # 这是一个简化的查找，依赖于我们生成的 href="checkbox:N"
        
        cursor = self.editor.textCursor()
        doc = self.editor.document()
        
        # 查找所有链接
        # 由于 Qt 没有直接查找特定 href 的 API，我们需要遍历
        # 但我们在 eventFilter 中已经获取了点击位置的 cursor，其实可以直接操作那个位置
        # 不过 eventFilter 传过来的是点击位置，我们这里重新获取一下会更稳健吗？
        # 不，直接利用 eventFilter 里的逻辑更简单。
        # 为了通用性，我们这里还是遍历一下吧，或者优化 eventFilter 直接传 cursor 过来。
        # 鉴于 target_idx 是我们生成的唯一标识，我们用 find 查找
        
        # 实际上，toggle_checkbox_state 是由 eventFilter 调用的。
        # 我们修改一下逻辑，让 eventFilter 直接处理“原地翻转”，不需要这个复杂的函数了。
        pass

    def insert_checkbox(self):
        cursor = self.editor.textCursor()
        
        if self.is_markdown_mode:
            # 渲染模式下：插入 HTML 复选框
            # 移动到行首
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            # 插入一个未选中的复选框 HTML
            # 注意：我们需要手动维护 checkbox:N 的索引吗？
            # 其实不需要严格连续，只要唯一即可。或者我们暂时用一个随机数/时间戳
            import time
            idx = int(time.time() * 1000)
            html = f'<a href="checkbox:{idx}" style="text-decoration: none; color: #e06c75; font-weight: bold;">☐</a> '
            cursor.insertHtml(html)
        else:
            # 源码模式下：插入 Markdown 语法
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            cursor.insertText("- [ ] ")
        
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()

    def change_font(self):
        font, ok = QFontDialog.getFont(self.editor.font(), self)
        if ok:
            self.font_size = font.pointSize()
            self.apply_font_size()

    def adjust_font_size(self, delta):
        """调整字体大小"""
        self.font_size += delta
        if self.font_size < 6: self.font_size = 6
        self.apply_font_size()

    def apply_font_size(self):
        """应用当前的字体大小到编辑器"""
        # 更新编辑器字体（源码模式）
        font = self.editor.font()
        font.setPointSize(self.font_size)
        self.editor.setFont(font)
        
        # 如果处于 Markdown 模式，重新渲染以更新 CSS 中的字体大小
        if self.is_markdown_mode:
            self.update_markdown_view()

    def change_bg_color(self):
        r, g, b = self.bg_rgb
        initial_color = QColor(r, g, b, self.bg_opacity)
        color = QColorDialog.getColor(initial=initial_color, options=QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if color.isValid():
            self.bg_rgb = (color.red(), color.green(), color.blue())
            self.bg_opacity = color.alpha()
            self.update_style()

    def change_opacity(self):
        """打开背景不透明度调节对话框"""
        from PyQt6.QtWidgets import QDialog, QSlider, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle("设置背景不透明度")
        dialog.setFixedSize(300, 120)
        dialog.setStyleSheet("""
            QDialog { background-color: #2c313a; }
            QLabel { color: #abb2bf; font-size: 12px; }
            QPushButton { 
                background-color: #3e4451; 
                color: #abb2bf; 
                border: none; 
                padding: 5px 15px; 
                border-radius: 3px;
            }
            QPushButton:hover { background-color: #4e5561; }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # 显示当前值的标签 (将 0-255 转换为百分比显示)
        current_percent = int(self.bg_opacity / 255 * 100)
        value_label = QLabel(f"背景不透明度: {current_percent}%")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        # 滑块
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(10)  # 最小 10%
        slider.setMaximum(100)  # 最大 100%
        slider.setValue(current_percent)
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #3e4451;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #61afef;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QSlider::sub-page:horizontal {
                background: #61afef;
                border-radius: 3px;
            }
        """)
        
        def on_slider_change(value):
            value_label.setText(f"背景不透明度: {value}%")
            # 将百分比转换为 0-255
            self.bg_opacity = int(value / 100 * 255)
            self.update_style()
        
        slider.valueChanged.connect(on_slider_change)
        layout.addWidget(slider)
        
        # 按钮行
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
        
        dialog.exec()

    # --- 窗口拖拽和边缘调整大小逻辑 ---
    
    def _get_resize_edge(self, pos):
        """检测鼠标位置是否在窗口边缘，返回边缘方向"""
        rect = self.rect()
        x, y = pos.x(), pos.y()
        margin = self._edge_margin
        
        edges = []
        
        if x <= margin:
            edges.append('left')
        elif x >= rect.width() - margin:
            edges.append('right')
        
        if y <= margin:
            edges.append('top')
        elif y >= rect.height() - margin:
            edges.append('bottom')
        
        if edges:
            return '-'.join(edges)
        return None
    
    def _update_cursor_shape(self, edge):
        """根据边缘方向更新鼠标光标形状"""
        if edge is None:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        elif edge in ('left', 'right'):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif edge in ('top', 'bottom'):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif edge in ('left-top', 'right-bottom'):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif edge in ('right-top', 'left-bottom'):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            edge = self._get_resize_edge(pos)
            
            if edge:
                # 开始边缘调整大小
                self._resize_edge = edge
                self._resize_start_pos = event.globalPosition().toPoint()
                self._resize_start_geometry = self.geometry()
            else:
                # 普通拖拽移动
                self._resize_edge = None
                self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self._resize_edge:
                # 边缘调整大小
                self._do_resize(event.globalPosition().toPoint())
            elif hasattr(self, 'drag_pos'):
                # 窗口拖拽
                self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()
        else:
            # 更新鼠标光标
            pos = event.position().toPoint()
            edge = self._get_resize_edge(pos)
            self._update_cursor_shape(edge)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放时重置状态"""
        self._resize_edge = None
        self._resize_start_pos = None
        self._resize_start_geometry = None
        event.accept()
    
    def _do_resize(self, global_pos):
        """执行窗口大小调整"""
        if not self._resize_start_pos or not self._resize_start_geometry:
            return
        
        diff = global_pos - self._resize_start_pos
        geo = QRect(self._resize_start_geometry)
        min_width, min_height = 200, 150  # 最小窗口大小
        
        if 'left' in self._resize_edge:
            new_left = geo.left() + diff.x()
            new_width = geo.right() - new_left + 1
            if new_width >= min_width:
                geo.setLeft(new_left)
        
        if 'right' in self._resize_edge:
            new_width = geo.width() + diff.x()
            if new_width >= min_width:
                geo.setWidth(new_width)
        
        if 'top' in self._resize_edge:
            new_top = geo.top() + diff.y()
            new_height = geo.bottom() - new_top + 1
            if new_height >= min_height:
                geo.setTop(new_top)
        
        if 'bottom' in self._resize_edge:
            new_height = geo.height() + diff.y()
            if new_height >= min_height:
                geo.setHeight(new_height)
        
        self.setGeometry(geo)
    
    def leaveEvent(self, event):
        """鼠标离开窗口时恢复默认光标"""
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().leaveEvent(event)
            
    def keyPressEvent(self, event):
        # 快捷键处理
        modifiers = event.modifiers()
        key = event.key()
        
        if modifiers == Qt.KeyboardModifier.ControlModifier:
            if key == Qt.Key.Key_M:
                self.render_markdown()
            elif key == Qt.Key.Key_Equal: # Ctrl + = (放大)
                self.adjust_font_size(1)
            elif key == Qt.Key.Key_Minus: # Ctrl + - (缩小)
                self.adjust_font_size(-1)
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """确保窗口关闭时完全退出应用程序"""
        QApplication.instance().quit()
        super().closeEvent(event)

if __name__ == "__main__":
    # 设置应用程序名称（用于 WM_CLASS）
    # 必须在创建 QApplication 之前设置
    QApplication.setApplicationName("sticky-note")
    QApplication.setApplicationDisplayName("Sticky Note")
    
    app = QApplication(sys.argv)
    
    # 设置应用程序的 Desktop Entry 名称，用于面板图标匹配
    app.setDesktopFileName("sticky-note")
    
    # 设置窗口图标（用于任务栏/面板）
    icon_path = os.path.expanduser("~/.local/share/icons/sticky_note.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    window = StickyNoteApp()
    window.show()
    sys.exit(app.exec())
