# Setup Instructions

## Steps to create and activate a virtual environment

### macOS
1. Create the virtual environment:
    ```sh
    python3 -m venv myenv
    ```
2. Activate the virtual environment:
    ```sh
    source myenv/Scripts/activate
    ```
3. Upgrade pip:
    ```sh
    python3 -m pip install --upgrade pip
    ```
4. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```
5. Install the face recognition models:
    ```sh
    pip install git+https://github.com/ageitgey/face_recognition_models
    ```
6. Run the main script:
    ```sh
    python3 main.py
    ```

### Windows
1. Create the virtual environment:
    ```sh
    python -m venv myenv
    ```
2. Activate the virtual environment:
    ```sh
    .\myenv\Scripts\Activate.ps1
    ```
3. Upgrade pip:
    ```sh
    python.exe -m pip install --upgrade pip
    ```
4. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```
5. Install the face recognition models:
    ```sh
    pip install git+https://github.com/ageitgey/face_recognition_models
    ```
6. Run the main script:
    ```sh
    python main.py
    ```

## Alternative Setup for Windows with Python 3
1. Create the virtual environment:
    ```sh
    python3 -m venv myenv3
    ```
2. Activate the virtual environment:
    ```sh
    .\myenv3\Scripts\Activate.ps1
    ```
3. Upgrade pip:
    ```sh
    python3 -m pip install --upgrade pip
    ```
4. Install the required packages:
    ```sh
    pip3 install -r requirements.txt
    ```
5. Install the face recognition models:
    ```sh
    pip3 install git+https://github.com/ageitgey/face_recognition_models
    ```
6. Run the main script:
    ```sh
    python3 main.py
    ```
