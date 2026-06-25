# Python Exam Agent

An AI-powered Python coding practice and feedback system for beginner programmers.

This repository currently contains the Phase 1 backend architecture:

- FastAPI application
- SQLite database
- SQLAlchemy models
- exam generation API
- answer submission API
- automatic test-case execution
- basic mistake feedback
- exam history and final feedback report endpoints

The backend currently seeds sanitized Python practice questions. They are not
split by easy, medium, or hard; they are grouped by topic/type and use the
default difficulty value `standard`.

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
|-- README.md
`-- .gitignore
```

## Run Locally

From the project root:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

## Main API Endpoints

```text
GET  /topics
POST /generate-exam
POST /submit-answer
POST /finish-exam/{exam_id}
GET  /exam/{exam_id}
GET  /history
```

## Example Request

Generate an exam:

```json
{
  "topic": "number theory",
  "difficulty": "standard",
  "number_of_questions": 3,
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

When more questions are ready, remove all course, school, instructor, assignment,
exam-source, and private-material information before adding them to this seed
layer or a future admin import endpoint.

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
