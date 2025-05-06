# 🌟 WormGPT Neural Interface

A modern, cyber-themed GUI interface for WormGPT built with PyQt6. Features a Matrix-style animation background and a sleek chat interface.

![WormGPT Interface](https://raw.githubusercontent.com/JustLachin/wormgpt-gui/refs/heads/main/preview.png)

## ✨ Features

- 🎨 Modern, cyber-themed interface
- 🔮 Matrix-style animated background
- 💬 Advanced chat functionality
- 🌍 Multi-language support
- 📝 Code highlighting and formatting
- 📋 One-click message/code copying
- 🎯 Thread-safe performance
- 🛡️ Error handling and recovery
- 🎭 Custom styling and animations

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Windows OS (tested on Windows 10/11)
- Internet connection for API calls

### Installation

1. Clone the repository:
```bash
git clone https://github.com/JustLachin/wormgpt-gui.git
cd wormgpt-gui
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python wormgpt_gui.py
```

## 📦 Building the Executable

To create a standalone executable:

1. Run the export script:
```bash
python export-windows.py
```

2. Wait for the build process to complete
3. Find the executable in `output/WormGPT/WormGPT.exe`

⚠️ Important: Keep all files in the WormGPT folder together. Do not move the .exe file alone.

## 🎮 Usage Guide

### Starting a Chat

1. Launch the application
2. Select your preferred language from the dropdown
3. Type your message in the input field
4. Press Enter or click "EXECUTE" to send

### Working with Code

1. Code blocks are automatically detected when using triple backticks:
\```python
print("Hello World!")
\```

2. Features for code blocks:
   - Syntax highlighting
   - Copy button for each block
   - Language detection
   - Proper formatting

### Keyboard Shortcuts

- `Enter`: Send message
- `Shift + Enter`: New line in input
- `Ctrl/Cmd + C`: Copy selected text

## 🛠️ Technical Details

### Architecture

- **GUI Framework**: PyQt6
- **Code Highlighting**: Pygments
- **Background Animation**: Custom QThread implementation
- **API Integration**: Requests library
- **Theme Engine**: Qt Material

### Components

1. **MatrixBackground**
   - Custom widget for animated background
   - Thread-safe implementation
   - Optimized rendering

2. **ChatArea**
   - Scrollable message container
   - Dynamic message loading
   - Automatic scroll handling

3. **MessageWidget**
   - Rich text support
   - Code block detection
   - Copy functionality

4. **CodeBlock**
   - Syntax highlighting
   - Language detection
   - Copy with animation

## 🔧 Configuration

### Language Settings

Available languages:
- English
- Turkish
- Spanish
- French
- German

### Theme Customization

The interface uses a cyber theme with:
- Matrix-style animations
- Neon green accents
- Dark mode optimization
- Custom glow effects

## 🚨 Troubleshooting

### Common Issues

1. **Application Won't Start**
   - Verify Python installation
   - Check required packages
   - Run as administrator

2. **No API Response**
   - Check internet connection
   - Verify API endpoint
   - Check server status

3. **Display Issues**
   - Update graphics drivers
   - Check PyQt6 installation
   - Verify screen resolution

### Error Messages

- QPainter errors: Restart application
- Thread errors: Check system resources
- API errors: Check connection/endpoint

## 📝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0) - see the [LICENSE](LICENSE) file for details.

This means you are free to:
- ✅ Use the software for any purpose
- ✅ Study how the software works and modify it
- ✅ Redistribute copies of the software
- ✅ Distribute modified versions of the software

Requirements:
- 📝 Include the original source code when you distribute the software
- 📝 State any significant changes made to the software
- 📝 Make available any modifications under the same license
- 📝 Include the full text of the license and copyright notice

## 🤝 Support

For support, issues, or feature requests:
1. Create an issue in the repository
2. Contact via GitHub discussions
3. Check existing documentation

## 🙏 Acknowledgments

- PyQt6 team for the framework
- Matrix digital rain concept
- Open source community

## 🔄 Updates

Check the repository for:
- Latest features
- Bug fixes
- Performance improvements
- New themes

---

Made with ❤️ by [JustLachin](https://github.com/JustLachin) 
