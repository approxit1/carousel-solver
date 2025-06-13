# Carousel Autocompleter

a simple terminal-based Python script to automate the completion of quizzes on the Carousel Learning platform.

## Features

-   Fetches all questions and their correct answers for a given quiz.
-   Automatically submits all correct answers.
-   Marks all questions as reviewed.
-   Finalizes the quiz attempt.
-   Saves a `.txt` file of the questions and answers for your records.

## Requirements

-   Python 3.x
-   `requests` library

## How to Use

1.  **Install the requests library:**
    ```bash
    pip install requests
    ```

2.  **Run the script from your terminal:**
    ```bash
    python solver.py
    ```

3.  **Follow the prompts:**
    -   Enter your **FORENAME**.
    -   Enter your **SURNAME**.
    -   Paste the full **LINK** to the Carousel quiz.

Once finished a `.txt` file containing all the answers will be saved in the same directory.
