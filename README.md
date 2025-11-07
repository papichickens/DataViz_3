# FIFA World Cup Interactive Explorer

This is a web-based, interactive dashboard for exploring historical FIFA World Cup data from 1930 to 2022. The application is built using Python and the Dash framework.

## Features

- **Interactive World Map:** Visualize all participating nations for every tournament, with medal winners (Gold, Silver, Bronze) highlighted.
- **Tournament Overview:** A dynamic scatter plot showing goals, attendance, and host continent for every World Cup.
- **Detailed Statistics:** Click on a tournament to view detailed stats, including top goal scorers (Golden Boot).
- **Team-Specific Journey:** Select a team to see their complete match-by-match results and player statistics for that tournament.
- **Head-to-Head Analysis:** Compare the all-time World Cup record (wins, draws, goals scored) between any two teams a country has faced.

## Prerequisites

- Python 3.8 or newer
- `pip` (Python's package installer)
- `git` (for cloning the repository)

## Setup and Installation (Manual)

Follow these steps to get the application running on your local machine.

### 1. Clone the Repository

Open your terminal or command prompt and run the following command to download the project files:

```bash
git clone https://github.com/papichickens/DataViz_3.git
cd DataViz_3
```

### 2. Create and Activate a Virtual Environment

A virtual environment isolates your project's dependencies. This is a critical best practice.

**On macOS / Linux:**

```bash
# Create the virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate
```

**On Windows:**

```bash
# Create the virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate
```

You'll know it's active because your terminal prompt will be prefixed with `(venv)`.

### 3. Install Dependencies

Now, install all the necessary Python packages from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 4. Run the Application

With your virtual environment still active, start the Dash server by running:

```bash
python app.py
```

You will see output in your terminal indicating that the server is running, usually on `http://127.0.0.1:8050/`.

Open your web browser and navigate to that address to use the application.

### 5. Stopping the Application

To stop the server, go back to your terminal and press `Ctrl+C`.

---

## Automatic Startup (Recommended)

To answer your question: yes, you can automate this! The easiest way is to use a simple shell script. This script will automatically activate the virtual environment and run the app with a single command.

Create a new file in your project's root directory.

### For macOS / Linux Users

1.  Create a file named `start.sh`.
2.  Paste the following content into it:

    ```sh
    #!/bin/bash
    echo "Activating virtual environment..."
    source venv/bin/activate

    echo "Starting the Dash application..."
    python app.py

    echo "Application stopped."
    ```

3.  Make the script executable by running `chmod +x start.sh` in your terminal.
4.  From now on, you can just run `./start.sh` to start your entire application.

### For Windows Users

1.  Create a file named `start.bat`.
2.  Paste the following content into it:

    ```bat
    @echo off
    echo "Activating virtual environment..."
    call .\venv\Scripts\activate.bat

    echo "Starting the Dash application..."
    python app.py

    echo "Application stopped."
    ```

3.  From now on, you can just double-click `start.bat` or run `start.bat` in your command prompt to start your entire application.
```