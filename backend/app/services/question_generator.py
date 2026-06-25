from app.models.question import Question


SUPPORTED_TOPICS = [
    "lists",
    "integers",
    "number theory",
    "file processing",
    "matrices",
    "patterns",
    "sets and words",
]


def seed_original_questions() -> list[Question]:
    return [
        Question(
            title="Increasing Runs Without Consecutive Duplicates",
            description=(
                "Write a function that receives a list of integers. First remove consecutive duplicate values, "
                "then decompose the remaining list into maximal strictly increasing runs. Return the runs as a list of lists."
            ),
            topic="lists",
            difficulty="standard",
            function_signature="increasing_runs(values)",
            starter_code="def increasing_runs(values):\n    # write your code here\n    pass\n",
            test_cases=[
                {"input": {"values": []}, "expected": []},
                {"input": {"values": [6, 6, 0, 4, 8, 7, 6]}, "expected": [[6], [0, 4, 8], [7], [6]]},
                {
                    "input": {"values": [3, 8, 2, 5, 7, 1, 0, 7, 4, 8, 3, 3, 7, 8, 8]},
                    "expected": [[3, 8], [2, 5, 7], [1], [0, 7], [4, 8], [3, 7, 8]],
                },
                {
                    "input": {"values": [1, 1, 2, 2, 1, 3, 3, 4]},
                    "expected": [[1, 2], [1, 3, 4]],
                    "hidden": True,
                },
            ],
            reference_solution=(
                "def increasing_runs(values):\n"
                "    compact = []\n"
                "    for value in values:\n"
                "        if not compact or value != compact[-1]:\n"
                "            compact.append(value)\n"
                "    runs = []\n"
                "    for value in compact:\n"
                "        if not runs or value <= runs[-1][-1]:\n"
                "            runs.append([value])\n"
                "        else:\n"
                "            runs[-1].append(value)\n"
                "    return runs\n"
            ),
        ),
        Question(
            title="Count Set Bits",
            description="Write a function that returns the binary representation of a positive integer and the number of bits set to 1.",
            topic="integers",
            difficulty="standard",
            function_signature="binary_bit_count(n)",
            starter_code="def binary_bit_count(n):\n    # write your code here\n    pass\n",
            test_cases=[
                {"input": {"n": 1}, "expected": {"binary": "1", "ones": 1}},
                {"input": {"n": 2314}, "expected": {"binary": "100100001010", "ones": 4}},
                {"input": {"n": 9871}, "expected": {"binary": "10011010001111", "ones": 8}},
                {"input": {"n": 1024}, "expected": {"binary": "10000000000", "ones": 1}, "hidden": True},
            ],
            reference_solution="def binary_bit_count(n):\n    binary = bin(n)[2:]\n    return {\"binary\": binary, \"ones\": binary.count(\"1\")}\n",
        ),
        Question(
            title="Prime Factor Decomposition",
            description=(
                "Write a function that returns the prime factor decomposition of an integer n >= 2. "
                "Return a list of [prime, exponent] pairs in increasing prime order."
            ),
            topic="number theory",
            difficulty="standard",
            function_signature="prime_factors(n)",
            starter_code="def prime_factors(n):\n    # write your code here\n    pass\n",
            test_cases=[
                {"input": {"n": 2}, "expected": [[2, 1]]},
                {"input": {"n": 100}, "expected": [[2, 2], [5, 2]]},
                {"input": {"n": 45100}, "expected": [[2, 2], [5, 2], [11, 1], [41, 1]]},
                {"input": {"n": 5432}, "expected": [[2, 3], [7, 1], [97, 1]], "hidden": True},
            ],
            reference_solution=(
                "def prime_factors(n):\n"
                "    factors = []\n"
                "    p = 2\n"
                "    while p * p <= n:\n"
                "        exponent = 0\n"
                "        while n % p == 0:\n"
                "            exponent += 1\n"
                "            n //= p\n"
                "        if exponent:\n"
                "            factors.append([p, exponent])\n"
                "        p += 1\n"
                "    if n > 1:\n"
                "        factors.append([n, 1])\n"
                "    return factors\n"
            ),
        ),
        Question(
            title="Count Primes In Range",
            description="Write a function that counts how many prime numbers are between a and b, inclusive.",
            topic="number theory",
            difficulty="standard",
            function_signature="count_primes_between(a, b)",
            starter_code="def count_primes_between(a, b):\n    # write your code here\n    pass\n",
            test_cases=[
                {"input": {"a": 2, "b": 2}, "expected": 1},
                {"input": {"a": 4, "b": 4}, "expected": 0},
                {"input": {"a": 100, "b": 800}, "expected": 114},
                {"input": {"a": 14, "b": 16}, "expected": 0, "hidden": True},
            ],
            reference_solution=(
                "def count_primes_between(a, b):\n"
                "    def is_prime(n):\n"
                "        if n < 2:\n"
                "            return False\n"
                "        if n == 2:\n"
                "            return True\n"
                "        if n % 2 == 0:\n"
                "            return False\n"
                "        divisor = 3\n"
                "        while divisor * divisor <= n:\n"
                "            if n % divisor == 0:\n"
                "                return False\n"
                "            divisor += 2\n"
                "        return True\n"
                "    return sum(1 for number in range(a, b + 1) if is_prime(number))\n"
            ),
        ),
        Question(
            title="Maximum Monthly Inflation From CSV",
            description=(
                "Write a function that receives a year, an input CSV filename, and an output filename. "
                "The CSV file has Date and Inflation columns. Return the maximum inflation for that year and the month names where it occurs, "
                "and write the same summary to the output file."
            ),
            topic="file processing",
            difficulty="standard",
            function_signature="maximum_inflation(year, input_filename, output_filename)",
            starter_code="def maximum_inflation(year, input_filename, output_filename):\n    # write your code here\n    pass\n",
            test_cases=[
                {
                    "input": {
                        "year": 1922,
                        "input_filename": "inflation.csv",
                        "output_filename": "report.txt",
                    },
                    "files": {
                        "inflation.csv": (
                            "Date,Inflation\n"
                            "1922-01-01,0.1\n"
                            "1922-07-01,0.6\n"
                            "1922-10-01,0.6\n"
                            "1923-01-01,1.2\n"
                        )
                    },
                    "expected": {"maximum": 0.6, "months": ["Jul", "Oct"]},
                    "expected_files": {"report.txt": "Maximum inflation: 0.6\nMonths: Jul, Oct\n"},
                },
                {
                    "input": {
                        "year": 2013,
                        "input_filename": "inflation.csv",
                        "output_filename": "report.txt",
                    },
                    "files": {
                        "inflation.csv": (
                            "Date,Inflation\n"
                            "2013-02-01,0.82\n"
                            "2013-03-01,0.3\n"
                        )
                    },
                    "expected": {"maximum": 0.82, "months": ["Feb"]},
                    "expected_files": {"report.txt": "Maximum inflation: 0.82\nMonths: Feb\n"},
                },
                {
                    "input": {
                        "year": 1995,
                        "input_filename": "inflation.csv",
                        "output_filename": "report.txt",
                    },
                    "files": {
                        "inflation.csv": (
                            "Date,Inflation\n"
                            "1995-01-01,0.4\n"
                            "1995-02-01,0.4\n"
                            "1995-03-01,0.2\n"
                        )
                    },
                    "expected": {"maximum": 0.4, "months": ["Jan", "Feb"]},
                    "expected_files": {"report.txt": "Maximum inflation: 0.4\nMonths: Jan, Feb\n"},
                    "hidden": True,
                },
            ],
            reference_solution=(
                "import csv\n"
                "\n"
                "def maximum_inflation(year, input_filename, output_filename):\n"
                "    month_names = [\"Jan\", \"Feb\", \"Mar\", \"Apr\", \"May\", \"Jun\", \"Jul\", \"Aug\", \"Sep\", \"Oct\", \"Nov\", \"Dec\"]\n"
                "    selected = []\n"
                "    with open(input_filename, newline=\"\", encoding=\"utf-8\") as csv_file:\n"
                "        reader = csv.DictReader(csv_file)\n"
                "        for row in reader:\n"
                "            row_year, row_month, _ = row[\"Date\"].split(\"-\")\n"
                "            if int(row_year) == year:\n"
                "                selected.append((float(row[\"Inflation\"]), month_names[int(row_month) - 1]))\n"
                "    maximum = max(value for value, _ in selected)\n"
                "    months = [month for value, month in selected if value == maximum]\n"
                "    with open(output_filename, \"w\", encoding=\"utf-8\") as output_file:\n"
                "        output_file.write(f\"Maximum inflation: {maximum}\\n\")\n"
                "        output_file.write(f\"Months: {', '.join(months)}\\n\")\n"
                "    return {\"maximum\": maximum, \"months\": months}\n"
            ),
        ),
        Question(
            title="Good Square",
            description=(
                "Write a function that receives a square matrix. If it contains duplicates, return the sorted duplicate values. "
                "If all values are distinct, sort all values and refill the square column by column from left to right."
            ),
            topic="matrices",
            difficulty="standard",
            function_signature="analyse_square(square)",
            starter_code="def analyse_square(square):\n    # write your code here\n    pass\n",
            test_cases=[
                {"input": {"square": [[1, 1], [0, 1]]}, "expected": {"is_good": False, "duplicates": [1], "ordered_square": None}},
                {"input": {"square": [[24, 48], [26, 2]]}, "expected": {"is_good": True, "duplicates": [], "ordered_square": [[2, 26], [24, 48]]}},
                {
                    "input": {"square": [[49, 97, 53], [5, 33, 65], [62, 51, 38]]},
                    "expected": {"is_good": True, "duplicates": [], "ordered_square": [[5, 49, 62], [33, 51, 65], [38, 53, 97]]},
                },
                {
                    "input": {"square": [[3, 3, 0], [2, 4, 3], [3, 2, 3]]},
                    "expected": {"is_good": False, "duplicates": [2, 3], "ordered_square": None},
                    "hidden": True,
                },
            ],
            reference_solution=(
                "def analyse_square(square):\n"
                "    seen = set()\n"
                "    duplicates = set()\n"
                "    for row in square:\n"
                "        for value in row:\n"
                "            if value in seen:\n"
                "                duplicates.add(value)\n"
                "            seen.add(value)\n"
                "    if duplicates:\n"
                "        return {\"is_good\": False, \"duplicates\": sorted(duplicates), \"ordered_square\": None}\n"
                "    n = len(square)\n"
                "    values = sorted(value for row in square for value in row)\n"
                "    ordered = [[0] * n for _ in range(n)]\n"
                "    index = 0\n"
                "    for column in range(n):\n"
                "        for row in range(n):\n"
                "            ordered[row][column] = values[index]\n"
                "            index += 1\n"
                "    return {\"is_good\": True, \"duplicates\": [], \"ordered_square\": ordered}\n"
            ),
        ),
        Question(
            title="Digit Pyramid",
            description=(
                "Write a function that returns a right-aligned pyramid of digits as a list of strings. "
                "The first row has one digit, the second row has three digits, and so on. Digits continue modulo 10."
            ),
            topic="patterns",
            difficulty="standard",
            function_signature="digit_pyramid(height)",
            starter_code="def digit_pyramid(height):\n    # write your code here\n    pass\n",
            test_cases=[
                {"input": {"height": 1}, "expected": ["0"]},
                {"input": {"height": 4}, "expected": ["   0", "  123", " 45678", "9012345"]},
                {"input": {"height": 6}, "expected": ["     0", "    123", "   45678", "  9012345", " 678901234", "56789012345"]},
                {"input": {"height": 2}, "expected": [" 0", "123"], "hidden": True},
            ],
            reference_solution=(
                "def digit_pyramid(height):\n"
                "    rows = []\n"
                "    current = 0\n"
                "    for row_number in range(1, height + 1):\n"
                "        row = \" \" * (height - row_number)\n"
                "        for _ in range(2 * row_number - 1):\n"
                "            row += str(current % 10)\n"
                "            current += 1\n"
                "        rows.append(row)\n"
                "    return rows\n"
            ),
        ),
        Question(
            title="Two Word Letter Cover",
            description=(
                "Write a function that receives a string of distinct uppercase letters and a dictionary filename. "
                "Return all alphabetically ordered pairs of words that together use every given letter exactly once."
            ),
            topic="sets and words",
            difficulty="standard",
            function_signature="word_pairs_using_all_letters(letters, dictionary_filename)",
            starter_code="def word_pairs_using_all_letters(letters, dictionary_filename):\n    # write your code here\n    pass\n",
            test_cases=[
                {
                    "input": {"letters": "ONESIX", "dictionary_filename": "dictionary.txt"},
                    "files": {"dictionary.txt": "ION\nSEX\nONE\nSIX\nNO\nEXIT\n"},
                    "expected": [["ION", "SEX"], ["ONE", "SIX"]],
                },
                {
                    "input": {"letters": "GRIHWSNYP", "dictionary_filename": "dictionary.txt"},
                    "files": {"dictionary.txt": "SPRING\nWHY\nGRIN\nHYP\n"},
                    "expected": [["SPRING", "WHY"]],
                },
                {
                    "input": {"letters": "ABCDEFGH", "dictionary_filename": "dictionary.txt"},
                    "files": {"dictionary.txt": "BAD\nFACE\nHIGH\n"},
                    "expected": [],
                },
                {
                    "input": {"letters": "ABCD", "dictionary_filename": "dictionary.txt"},
                    "files": {"dictionary.txt": "AB\nCD\nAC\nBD\nAA\n"},
                    "expected": [["AB", "CD"], ["AC", "BD"]],
                    "hidden": True,
                },
            ],
            reference_solution=(
                "def word_pairs_using_all_letters(letters, dictionary_filename):\n"
                "    target = set(letters)\n"
                "    valid_words = []\n"
                "    with open(dictionary_filename, encoding=\"utf-8\") as dictionary_file:\n"
                "        words = [line.strip().upper() for line in dictionary_file if line.strip()]\n"
                "    for word in words:\n"
                "        word_set = set(word)\n"
                "        if len(word_set) == len(word) and word_set <= target:\n"
                "            valid_words.append(word)\n"
                "    pairs = set()\n"
                "    for i, first in enumerate(valid_words):\n"
                "        first_set = set(first)\n"
                "        for second in valid_words[i + 1:]:\n"
                "            second_set = set(second)\n"
                "            if first_set.isdisjoint(second_set) and first_set | second_set == target:\n"
                "                pairs.add(tuple(sorted([first, second])))\n"
                "    return [list(pair) for pair in sorted(pairs)]\n"
            ),
        ),
    ]
