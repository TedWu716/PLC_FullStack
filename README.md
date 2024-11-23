# 🤖 PLC Fullstack Project

A full-stack application for PLC programming using OpenPLC and AI assistance.

## 📋 Prerequisites

- **Linux Operating System**
- **Python 3.10** or higher
- **Node.js** and **npm**
- **OpenPLC Runtime** installed

## 🗂️ Project Structure
```diff
PLC_FullStack/
+ ├── backend/
+ │   ├── plc_generator/
+ │   ├── venv/
+ │   └── Temp_Keychain.txt
! ├── frontend/
# ├── PLC_Code/
# ├── Log/
- └── prompt/
```

## 🚀 Installation

### **Step 1:** Clone the Repository
```bash
git clone <repository-url>
cd PLC_FullStack
```

### **Step 2:** Backend Setup

1. **Create and activate Python virtual environment**
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API Keys**
- Create `Temp_Keychain.txt` in the backend directory with the following format:
```ini
# Google API Key 
YOUR_GEMINI_API_KEY
# SSH Username 
YOUR_USERNAME
# SSH Password 
YOUR_PASSWORD
```

### **Step 3:** Frontend Setup

1. **Install Node.js dependencies**
```bash
cd frontend
npm install
```

## 🎯 Running the Application

### **Start Backend Server**
```bash
# Make sure you're in the backend directory and virtual environment is activated
cd backend
source venv/bin/activate
python server.py
```

### **Start Frontend Development Server**
```bash
# In a new terminal, navigate to frontend directory
cd frontend
npm run dev
```

## ✨ Features

- **AI-assisted PLC programming** using Google's Gemini API
- **Structured Text (ST)** code generation and compilation
- Integration with **OpenPLC Runtime**
- **Real-time** feedback and error handling
- **Web-based** user interface

## 📦 Required Packages

### **Backend Dependencies**
```python
google-generativeai
# Add other major dependencies
```

### **Frontend Dependencies**
```javascript
// Add major frontend dependencies
```

## ⚙️ Configuration

### **Backend Configuration**
- **Google Gemini API key** required
- **OpenPLC Runtime** must be installed and configured
- Proper permissions for file operations

### **Frontend Configuration**
- Ensure proper API endpoint configuration
- (other frontend-specific configurations)

## 👨‍💻 Development

### **Backend Development**
- **Python 3.10+** required
- Follow **PEP 8** style guidelines
- Add new modules in the `backend/plc_generator` directory

### **Frontend Development**
- **Node.js** required
- Follow JavaScript/TypeScript best practices
- Component-based architecture

## 🔧 Troubleshooting

Common issues and solutions:

1. **Virtual Environment Issues**
```bash
# If venv creation fails
sudo apt-get install python3-venv

# If activation fails
source venv/bin/activate
```

2. **API Key Issues**
- ✔️ Verify Gemini API key is valid
- ✔️ Check Temp_Keychain.txt formatting
- ✔️ Ensure proper file permissions

3. **OpenPLC Integration Issues**
- ✔️ Verify OpenPLC installation
- ✔️ Check file paths and permissions
- ✔️ Review error logs in Log directory

---
<div align="center">
<strong>Made with ❤️ by Your Team</strong>
</div>