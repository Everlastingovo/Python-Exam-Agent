def build_submission_feedback(is_correct: bool, error_message: str | None, failed_count: int) -> str:
    if is_correct:
        return "All visible tests passed. Good work."

    if error_message:
        if "SyntaxError" in error_message:
            return "There is a syntax error. Check brackets, colons, indentation, and spelling."
        if "NameError" in error_message:
            return "A name is not defined. Check variable names and the required function name."
        if "TypeError" in error_message:
            return "A type error occurred. Check the expected input types and return value."
        return "The code raised an error while running. Read the error message and test with a small example."

    return f"{failed_count} test case(s) failed. Review the edge cases and compare your return value with the expected result."
