"""
Student Grade Analyzer

Features & decisions (short):
- Students stored as list of dicts: {"name": str, "grades": [int, ...]}
- Names compared case-insensitively to avoid duplicates.
- Grade input accepts:
    * single integer per prompt (e.g. 95)
    * multiple grades separated by commas or spaces (e.g. "95, 88" or "95 88")
    * 'done' (or variants) to finish entering grades
    * floats that are exact integers (e.g. "95.0") are accepted and converted to int
- Invalid tokens are reported and skipped; valid grades (0..100 inclusive) are appended.
- Reporting:
    * per-student average (N/A if no grades)
    * summary: max average, min average, overall average of student averages
- Top performer:
    * uses max(..., key=lambda s: avg) while excluding students without grades
- Defensive programming: many checks, clear messages, try/except where appropriate.
- Performance: all operations are linear O(n) relative to number of students/grades,
  which is optimal for this interactive tool.
"""

from typing import List, Dict, Optional, Tuple


def calculate_average(grades: List[int]) -> Optional[float]:
    """Return average of grades or None if no grades."""
    if not grades:
        return None
    return sum(grades) / len(grades)


def find_student(students: List[Dict], name: str) -> Optional[Dict]:
    """
    Find a student by name (case-insensitive).
    Returns the student dict or None if not found.
    """
    target = name.strip().lower()
    for student in students:
        if student.get("name", "").strip().lower() == target:
            return student
    return None


def parse_grade_token(token: str) -> Tuple[Optional[int], Optional[str]]:
    """
    Parse a single token representing a grade or a control word.
    Returns (grade_int, None) on success, (None, 'done') if token is a done sentinel,
    or (None, 'invalid') if token is invalid.
    """
    tok = token.strip()
    if not tok:
        return None, "skip"

    lowered = tok.lower()
    if lowered in {"done", "d", "stop", "exit"}:
        return None, "done"

    # Allow integer tokens, and floats if they represent an integer (e.g. "95.0")
    try:
        # Prefer integer parse
        if "." in tok or "e" in tok.lower():
            # try float -> ensure it's an integer value
            valf = float(tok)
            if not valf.is_integer():
                return None, "invalid"
            val = int(valf)
        else:
            val = int(tok)
    except ValueError:
        return None, "invalid"

    if 0 <= val <= 100:
        return val, None
    else:
        return None, "out_of_range"


def add_student(students: List[Dict]) -> None:
    """Prompt for a new student name and add them if not present."""
    name = input("Enter student name: ").strip()
    if not name:
        print("Name cannot be empty. Aborting add.")
        return

    if find_student(students, name):
        print(f"Student '{name}' already exists.")
        return

    students.append({"name": name, "grades": []})
    print(f"Student '{name}' added successfully.")


def add_grades(students: List[Dict]) -> None:
    """Prompt for a student's name and accept grade inputs."""
    if not students:
        print("There are no students yet. Add a student first.")
        return

    name = input("Enter student name: ").strip()
    if not name:
        print("Empty name entered. Aborting.")
        return

    student = find_student(students, name)
    if not student:
        print(f"Student '{name}' not found.")
        return

    print(
        "Enter grades for student. Acceptable input formats:"
        "\n - single integer per prompt (e.g. 95)"
        "\n - multiple grades separated by commas or spaces (e.g. '95, 88' or '95 88')"
        "\n - 'done' to finish (also 'd', 'stop', 'exit')"
    )

    while True:
        try:
            line = input("Enter grade(s) or 'done': ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nInput interrupted. Ending grade entry.")
            break

        if not line:
            # empty line -> treat as finish signal
            print("Empty input treated as 'done'.")
            break

        # split tokens by commas first, then by whitespace if commas absent
        if "," in line:
            tokens = [t for part in line.split(",") for t in part.split()]
        else:
            tokens = line.split()

        finished = False
        for token in tokens:
            grade, status = parse_grade_token(token)
            if status == "done":
                finished = True
                break
            if status == "skip":
                continue
            if status == "invalid":
                print(f"Invalid token '{token}': not an integer. Please enter a number.")
                continue
            if status == "out_of_range":
                print(f"Grade out of range (0..100): '{token}'. Skipping.")
                continue
            # valid grade
            student["grades"].append(grade)

        if finished:
            print("Finished entering grades for student.")
            break

    # summary for this student after adding
    num_added = len(student["grades"])
    print(f"Student '{student['name']}' now has {num_added} grade(s).")


def show_report(students: List[Dict]) -> None:
    """Display a per-student report and overall statistics."""
    if not students:
        print("No students to report.")
        return

    print("\n--- Student Report ---")
    averages: List[float] = []
    for student in students:
        avg = calculate_average(student.get("grades", []))
        if avg is None:
            print(f"{student['name']}'s average grade is N/A.")
        else:
            print(f"{student['name']}'s average is {avg:.2f}.")
            averages.append(avg)

    if not averages:
        print("\nNo grades recorded for any student. No overall statistics.")
        return

    # overall statistics computed from student averages (matches example behavior)
    max_avg = max(averages)
    min_avg = min(averages)
    overall_avg = sum(averages) / len(averages)

    print("---------------------")
    print("\n--- Summary ---")
    print(f"Max Average: {max_avg:.2f}")
    print(f"Min Average: {min_avg:.2f}")
    print(f"Overall Average: {overall_avg:.2f}")


def find_top_student(students: List[Dict]) -> None:
    """Find and print the student with the highest average using max + lambda."""
    # Build list of (student, avg) for students with at least one grade
    graded = []
    for student in students:
        avg = calculate_average(student.get("grades", []))
        if avg is not None:
            graded.append((student, avg))

    if not graded:
        print("No graded students available to determine a top performer.")
        return

    # Use max with lambda; we are safe because graded is non-empty
    top_student, top_avg = max(graded, key=lambda pair: pair[1])
    print(
        f"The student with the highest average is {top_student['name']} with a grade of {top_avg:.2f}."
    )


def main() -> None:
    """Main interactive loop for the Student Grade Analyzer."""
    students: List[Dict] = []

    menu = (
        "\n--- Student Grade Analyzer ---\n"
        "1. Add a new student\n"
        "2. Add grades for a student\n"
        "3. Generate a full report\n"
        "4. Find top student\n"
        "5. Exit program\n"
    )

    while True:
        print(menu)
        try:
            choice_raw = input("Enter your choice: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nInput interrupted. Exiting program.")
            break

        if not choice_raw:
            print("Empty choice. Please enter a number 1-5.")
            continue

        try:
            choice = int(choice_raw)
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 5.")
            continue

        if choice == 1:
            add_student(students)
        elif choice == 2:
            add_grades(students)
        elif choice == 3:
            show_report(students)
        elif choice == 4:
            find_top_student(students)
        elif choice == 5:
            print("Exiting program.")
            break
        else:
            print("Choice out of range. Enter a number from 1 to 5.")


if __name__ == "__main__":
    main()
