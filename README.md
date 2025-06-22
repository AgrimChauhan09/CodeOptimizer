# C Code Optimizer - ML-based LLVM Optimization Platform

A sophisticated web-based platform that uses machine learning to predict optimal LLVM optimization passes for C code, providing real-time performance analysis and optimization recommendations.

## Features

- **ML-Powered Optimization**: Predicts the best optimization passes (O1, O2, O3, Os, Oz) using machine learning
- **Real-time Performance Analysis**: Measures actual execution times with nanosecond precision
- **Code Caching**: Prevents duplicate analysis and ensures consistent results
- **Training Dataset**: Contribute your own C code to improve the ML model
- **LLVM IR Visualization**: View generated intermediate representation
- **Optimization Techniques Analysis**: Detailed breakdown of applied optimizations

## System Requirements

- **Operating System**: Linux, macOS, or Windows (with WSL2)
- **Python**: 3.8 or higher
- **LLVM/Clang**: Version 10 or higher
- **GCC**: For compilation (alternative to Clang)
- **Memory**: At least 2GB RAM
- **Storage**: 500MB free space

## Installation

### 1. Install System Dependencies

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install -y clang llvm gcc python3 python3-pip python3-venv git
```


### 2. Clone or Download the Project

If you have git:
```bash
git clone <repository-url>
cd c-code-optimizer
```

Or download the project files and extract them to a folder.

### 3. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows (WSL):
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 4. Verify LLVM Installation

```bash
# Check if clang is installed
clang --version

# Check if llvm-dis is available
which llvm-dis

# If llvm-dis is not found, you may need to install llvm-dev
sudo apt install llvm-dev  # Ubuntu/Debian
brew install llvm          # macOS
```

## Running the Application

### 1. Start the Server

```bash
# Make sure you're in the project directory
cd c-code-optimizer

# Activate virtual environment if not already active
source venv/bin/activate

# Start the application
python main.py
```

### 2. Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

The application will be ready to use!

## Usage

1. **Write or Paste C Code**: Use the code editor to input your C program
2. **Click "Run & Optimize"**: The system will analyze and optimize your code
3. **View Results**: See execution times, optimization recommendations, and performance improvements
4. **Add to Dataset**: Contribute your code to improve the ML model (optional)
5. **Explore Details**: View LLVM IR, optimization techniques, and feature analysis

## Project Structure

```
c-code-optimizer/
├── main.py                 # Flask application entry point
├── app.py                  # Main application logic
├── requirements.txt        # Python dependencies
├── models/                 # Trained ML models
├── dataset/               # Training data
│   ├── training_codes/    # C code examples
│   └── optimization_cache.json
├── utils/                 # Core utilities
│   ├── compiler.py        # LLVM compilation
│   ├── timer.py          # Execution timing
│   ├── feature_extractor.py
│   ├── model_predictor.py
│   └── cache_manager.py
├── static/               # CSS, JS, assets
│   ├── css/style.css
│   └── js/main.js
└── templates/            # HTML templates
    └── index.html
```

## Contributing

1. Add your C code examples to `dataset/training_codes/`
2. Use the "Add to Dataset" feature in the web interface
3. Report issues or suggest improvements

## License

This project is open source. Feel free to modify and distribute according to your needs.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all system dependencies are installed
3. Ensure the Python virtual environment is activated
4. Check that LLVM/Clang is properly installed and accessible

---
