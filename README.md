# ⚡ TypeSprint - Typing Speed Tracker & Tester

A modern, desktop-based Typing Speed & Accuracy Tracker built in Python using **Tkinter**, **Object-Oriented Programming (OOP)**, and **JSON File Handling**.

---

## 🚀 Key Features

* **Real-Time Character Highlighting**:
  - 🟢 **Green**: Correct characters.
  - 🔴 **Red & Underline**: Mismatched/incorrect characters.
  - 🟡 **Yellow**: Current cursor character.
  - ⚪ **Muted Gray**: Remaining untyped text.
* **Live Dynamic Metrics**:
  - **WPM (Words Per Minute)**: Standard formula based on $((\text{correct characters} / 5) / \text{time in minutes})$.
  - **Accuracy (%)**: Real-time percentage of accurate keystrokes.
  - **Live Timer**: Real-time elapsed time or countdown.
  - **Error Counter**: Real-time tally of typing mistakes.
* **Multiple Test Modes**:
  - **Sentence Mode**: Practice completing sentences at your own pace.
  - **30s Sprint**: High-intensity 30-second countdown challenge.
  - **60s Challenge**: Standard 1-minute typing test.
* **Difficulty Tiers**:
  - **Easy**: Short, simple everyday sentences.
  - **Medium**: Conversational and descriptive phrases.
  - **Hard**: Complex vocabulary, technical terms, and varied punctuation.
* **📊 Performance Tracking & History**:
  - Automatically saves all your past sessions to `typing_history.json`.
  - Open the **History & Stats** dashboard to view:
    - **Personal Best WPM**
    - **Average WPM**
    - **Average Accuracy**
    - **Total Tests Completed**
    - Formatted table of recent test attempts with timestamps.
* **🏆 Results Dialog**:
  - Provides a performance summary and rating badge after each test.
* **Keyboard Shortcuts**:
  - `Ctrl + R`: Instant reset / load next sentence.

---

## 📁 Project Structure

```
├── main.py              # Main Tkinter GUI application & event loop
├── sentences.py         # Curated sentences categorized by difficulty
├── history_manager.py   # JSON file handling & analytics calculations
├── typing_history.json  # Auto-generated local storage for past scores
└── README.md            # Documentation & project guide
```

---

## 🛠️ Requirements & How to Run

### Requirements
- **Python 3.8+** (Uses Python's built-in `tkinter` and standard libraries — **no external `pip` install required!**)

### Running the App
Open your terminal/command prompt in this folder and run:

```bash
python main.py
```

---

## 📚 Concepts & Technologies Used
- **Tkinter GUI**: Canvas, Frames, Text Widgets with custom tag styling, Treeview table, Combobox, and Toplevel modal dialogs.
- **Object-Oriented Programming (OOP)**: Clean separation of UI classes, history management, and modular architecture.
- **String Manipulation**: Real-time character comparison, indexing, and slicing.
- **Event Handling**: Key releases, shortcuts, and focus binding.
- **File Handling**: JSON serialization for persistent test history.
