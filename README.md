# Python Exam Agent

An AI-powered Python coding practice and feedback system for beginner programmers.

This repository currently contains the Phase 1 backend architecture:

- FastAPI application
- SQLite database
- SQLAlchemy models
- exam generation API
- answer submission API
- automatic test-case execution
- 90-minute 8-question exam UI
- visible and hidden backend edge tests
- one-question-at-a-time exam navigation
- optional AI question draft generation with user-provided API key
- basic mistake feedback
- exam history and final feedback report endpoints

The backend seeds sanitized Python practice questions from the repository into
SQLite when the server starts. Each generated exam draws 8 questions from this
built-in question bank. There is no topic or question-count selection in the
exam UI.
The exam distribution is 3 easy questions, 3 medium questions, and 2 hard
questions. No topic/type appears more than 2 times.

## Project Structure

```text
Python-Exam-Agent/
|-- backend/
|   |-- app/
|   |   |-- main.py
|   |   |-- db/
|   |   |-- models/
|   |   |-- routers/
|   |   |-- schemas/
|   |   |-- services/
|   |   `-- utils/
|   `-- requirements.txt
|-- frontend/
|   |-- index.html
|   |-- styles.css
|   `-- app.js
|-- run.ps1
|-- stop.ps1
|-- start.bat
|-- stop.bat
|-- run.sh
|-- stop.sh
|-- README.md
`-- .gitignore
```

## Run Locally

Recommended one-click run on Windows:

```powershell
.\run.ps1
```

You can also double-click:

```text
start.bat
```

If Windows blocks script execution, use:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1
```

Recommended one-click run on macOS/Linux:

```bash
chmod +x run.sh stop.sh
./run.sh
```

Recommended Python version:

```text
Python 3.12 or 3.13
```

The one-click runner starts:

```text
Frontend: http://localhost:3000
Backend docs: http://localhost:8000/docs
```

Stop the app:

```powershell
.\stop.ps1
```

On macOS/Linux:

```bash
./stop.sh
```

Manual backend start from the project root:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Manual frontend start in a second terminal from the project root:

```bash
cd frontend
python -m http.server 3000
```

Open the frontend manually:

```text
http://localhost:3000
http://127.0.0.1:3000
```

Demo login account:

```text
Username: test
Password: 123456
```

Open the API docs:

```text
http://localhost:8000/docs
http://127.0.0.1:8000/docs
```

## Main API Endpoints

```text
POST /login
GET  /topics
POST /ai/generate-questions
POST /generate-exam
POST /submit-answer
POST /finish-exam/{exam_id}
GET  /exam/{exam_id}
GET  /history
GET  /wrong-questions
```

## Example Request

Generate an exam:

```json
{
  "topic": "__all__",
  "difficulty": "mixed",
  "number_of_questions": 8,
  "username": "demo"
}
```

Submit an answer:

```json
{
  "exam_id": 1,
  "question_id": 1,
  "code": "def prime_factors(n):\n    factors = []\n    p = 2\n    while p * p <= n:\n        exponent = 0\n        while n % p == 0:\n            exponent += 1\n            n //= p\n        if exponent:\n            factors.append([p, exponent])\n        p += 1\n    if n > 1:\n        factors.append([n, 1])\n    return factors\n"
}
```

## Question Bank Notes

Questions are currently seeded in:

```text
backend/app/services/question_generator.py
```

These questions are committed to the repository, so another device can clone the
GitHub project, start the backend, and draw exams from the same built-in
question bank.
When more questions are ready, remove all course, school, instructor,
assignment, exam-source, and private-material information before adding them to
this seed layer or a future admin import endpoint.

### File-Based Test Cases

For file reading questions, add a `files` object to each test case. The runner
creates those files in an isolated temporary folder before executing the answer.

```json
{
  "input": {
    "filename": "data.csv"
  },
  "files": {
    "data.csv": "name,score\nAda,10\nBo,7\n"
  },
  "expected": ["Ada"]
}
```

### Class-Based Test Cases

Class questions can use `kind: "class"` with constructor inputs and method steps.
For example, the built-in Bank Account question tests deposits, withdrawals,
interest, and the final balance attribute.

### Hidden Backend Tests

Add `"hidden": true` to a test case to make it count toward grading without
showing the exact input, expected output, or actual output in the frontend.

```json
{
  "input": {
    "n": 1024
  },
  "expected": {
    "binary": "10000000000",
    "ones": 1
  },
  "hidden": true
}
```

For file writing questions, add `expected_files`. The runner checks that the
student code creates the expected output files with exactly matching content.

```json
{
  "input": {
    "input_filename": "words.txt",
    "output_filename": "lengths.txt"
  },
  "files": {
    "words.txt": "cat\npython\n"
  },
  "expected": 2,
  "expected_files": {
    "lengths.txt": "cat: 3\npython: 6\n"
  }
}
```

## Safety Note

The MVP runs submitted Python code in a temporary subprocess with a timeout. This
is acceptable for a local prototype, but it is not a production security sandbox.
Before deploying publicly, code execution should be isolated with stronger
container or sandbox controls.
