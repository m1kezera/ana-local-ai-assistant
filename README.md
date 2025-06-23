
NOTE : Some files, commentaries or other texts might be in portuguese, just translate it.

# ANA - Autonomous Neural Assistant (v1.0)


ANA is a local administrative assistant powered by a Mistral-based LLM (OpenHermes 2.5 in GGUF format), capable of learning from PDFs, answering intelligently, and managing operations through a GUI built in PyQt6. This is version **1.0**, an early-stage release intended for showcasing and further development.

⚠️ **This release contains known bugs, potential crashes and instability**, especially related to `llama-cpp-python` integration on Windows platforms. All logs are provided for inspection inside the `/logs` folder.

---

## 🔧 Features

- Chatbot interface via PyQt6 with chat history management
- Offline LLM support (OpenHermes 2.5 - Mistral Q4_K_M via `llama-cpp-python`)
- Self-learning from local PDFs (`content_diverse/ebooks`)
- Web scraping & autopilot via Selenium
- MongoDB integration (optional)
- Logging system and startup diagnostics
- Modular architecture for expansion

---

## 🧠 Folder Structure

```bash
ANA/
├── app_desktop.py             # Main startup launcher
├── main.py                    # Alternative entry point
├── requirements.txt           # Dependencies list
├── prisma2.ico                # System tray & window icon
├── modules/                   # Core modules (see breakdown below)
├── content_diverse/ebooks/   # Offline PDF learning material
├── logs/                      # Execution logs and debug info
├── models/openhermes/        # GGUF model file here (.gguf)
├── chats/                    # Saved chat histories (JSON)
├── data/, downloads/, user/  # Runtime assets
```

### `modules/` breakdown:

| Folder            | Description |
|-------------------|-------------|
| `ana_core.py`     | Consciousness controller and lifecycle |
| `ana_llm.py`      | Interface with the local LLM via llama-cpp-python |
| `gui_assistant.py`| Full-featured PyQt6 interface |
| `learning_core.py`| Handles offline self-learning from PDFs |
| `tools/`          | Utilities: logger, system actions, chat repair |
| `web/`            | Web automation and learning from online sources |
| `brain/`          | Main brain logic of ANA |
| `knowledge/`      | Vector storage and similarity-based memory |
| `memory/`         | Memory context manager |
| `interface_assistant.py` | Launch helper for web commands |

---

## ✅ Requirements

This version was built with **Python 3.11** and **llama-cpp-python 0.2.72**. You can install all dependencies with:

```bash
pip install -r requirements.txt
```

> Make sure you are not using a virtual environment if facing RAM issues with `llama-cpp` on Windows.

---

## 🚀 Usage

```bash
python app_desktop.py
```

ANA will load the local model, verify the GUI, and activate the assistant. First-time loading may take several seconds.

---

## 📌 Known Issues

- `llama-cpp-python` might crash with **access violation 0x0000000000000000** on some Windows setups using `gguf` files.
- High RAM usage when loading large models like Mistral Q4_K_M.
- Logs often mention `model not loaded` due to bad threading or startup race conditions.

**Solution for now**: Load a small model (like TinyLlama) or test performance on Linux.

---

## ❗ Fake Model Placeholder (GitHub limitation)

Due to [GitHub's file size limit](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github), the `models/openhermes` directory contains a **fake `.gguf` placeholder**. To use the assistant, download the original model here:

```text
https://huggingface.co/TheBloke/OpenHermes-2.5-Mistral-GGUF
```
And place it in `models/openhermes/openhermes-2.5-mistral.Q4_K_M.gguf`

---

## 📄 License

Project ANA 1.0 is shared for educational and personal experimentation. Contributions welcome in future versions.

---

## 🙋 About the Author

Created by **Mikhael Ravi Medeiros Coelho** — AI enthusiast and developer from João Pessoa, Brazil 🇧🇷. ANA is part of a broader academic and portfolio project.

---
