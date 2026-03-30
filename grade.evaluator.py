import csv
import sys
import os


def load_csv_data():
    """
    Prompts the user for a filename, checks if it exists,
    and extracts all fields into a list of dictionaries.
    """
    filename = input("Enter the name of the CSV file to process (e.g., grades.csv): ").strip()

    if not os.path.exists(filename):
        print(f"Error: The file '{filename}' was not found.")
        sys.exit(1)

    assignments = []

    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                print("Error: The CSV file is empty or has no headers.")
                sys.exit(1)

            for row in reader:
                assignments.append({
                    'assignment': row['assignment'],
                    'group': row['group'],
                    'score': float(row['score']),
                    'weight': float(row['weight'])
                })

        if not assignments:
            print("Error: The CSV file contains no grade data.")
            sys.exit(1)

        return assignments

    except KeyError as e:
        print(f"Error: Missing expected column {e} in the CSV file.")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: Invalid numeric value in the CSV file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        sys.exit(1)


def evaluate_grades(data):
    """
    Processes the grade data:
      a) Validates all scores are between 0 and 100
      b) Validates total weight = 100, Formative = 60, Summative = 40
      c) Calculates final grade and GPA
      d) Determines Pass/Fail (>= 50% in BOTH categories)
      e) Identifies failed formative assignments eligible for resubmission
      f) Prints the final decision and resubmission options
    """
    print("\n--- Processing Grades ---\n")

    # ── a) Score Validation ───────────────────────────────────────────────────
    invalid_scores = [
        a for a in data if not (0 <= a['score'] <= 100)
    ]
    if invalid_scores:
        print("ERROR: The following assignments have invalid scores (must be 0–100):")
        for a in invalid_scores:
            print(f"  - {a['assignment']}: {a['score']}")
        sys.exit(1)
    print("✔ All scores are valid (0–100).")

    # ── b) Weight Validation ──────────────────────────────────────────────────
    total_weight = sum(a['weight'] for a in data)
    formative_weight = sum(a['weight'] for a in data if a['group'].lower() == 'formative')
    summative_weight = sum(a['weight'] for a in data if a['group'].lower() == 'summative')

    weight_errors = []
    if round(total_weight, 2) != 100:
        weight_errors.append(f"Total weight = {total_weight} (expected 100)")
    if round(formative_weight, 2) != 60:
        weight_errors.append(f"Formative weight = {formative_weight} (expected 60)")
    if round(summative_weight, 2) != 40:
        weight_errors.append(f"Summative weight = {summative_weight} (expected 40)")

    if weight_errors:
        print("ERROR: Weight validation failed:")
        for err in weight_errors:
            print(f"  - {err}")
        sys.exit(1)
    print("✔ Weight distribution is valid (Total=100, Formative=60, Summative=40).")

    # ── c) Grade & GPA Calculation ────────────────────────────────────────────
    # Weighted score per assignment = (score / 100) * weight
    # Group score = sum of weighted scores within group (already out of group total weight)
    # To get a percentage within the group: sum(weighted) / group_total_weight * 100

    formative_assignments = [a for a in data if a['group'].lower() == 'formative']
    summative_assignments = [a for a in data if a['group'].lower() == 'summative']

    formative_weighted_sum = sum((a['score'] / 100) * a['weight'] for a in formative_assignments)
    summative_weighted_sum = sum((a['score'] / 100) * a['weight'] for a in summative_assignments)

    # Group percentages (score within the group, scaled to 100)
    formative_percentage = (formative_weighted_sum / formative_weight) * 100
    summative_percentage = (summative_weighted_sum / summative_weight) * 100

    # Overall final grade (out of 100, since total weight = 100)
    final_grade = formative_weighted_sum + summative_weighted_sum

    # GPA = (Total Grade / 100) * 5.0
    gpa = (final_grade / 100) * 5.0

    # ── d) Pass / Fail ────────────────────────────────────────────────────────
    formative_pass = formative_percentage >= 50
    summative_pass = summative_percentage >= 50
    overall_pass = formative_pass and summative_pass

    # ── e) Resubmission Logic ─────────────────────────────────────────────────
    failed_formative = [
        a for a in formative_assignments if a['score'] < 50
    ]
    resubmit_candidates = []
    if failed_formative:
        max_weight = max(a['weight'] for a in failed_formative)
        resubmit_candidates = [
            a for a in failed_formative if a['weight'] == max_weight
        ]

    # ── f) Print Report ───────────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("           GRADE REPORT")
    print("=" * 50)

    print("\n📋 Assignment Breakdown:")
    print(f"  {'Assignment':<38} {'Group':<12} {'Score':>6}  {'Weight':>7}  {'Weighted':>9}")
    print(f"  {'-'*38} {'-'*12} {'-'*6}  {'-'*7}  {'-'*9}")
    for a in data:
        weighted = (a['score'] / 100) * a['weight']
        print(f"  {a['assignment']:<38} {a['group']:<12} {a['score']:>6.1f}  {a['weight']:>6.1f}%  {weighted:>8.2f}")

    print(f"\n📊 Group Summaries:")
    print(f"  Formative  → Weighted Score: {formative_weighted_sum:.2f} / {formative_weight:.0f}  "
          f"({formative_percentage:.2f}%)  {'✔ PASS' if formative_pass else '✘ FAIL'}")
    print(f"  Summative  → Weighted Score: {summative_weighted_sum:.2f} / {summative_weight:.0f}  "
          f"({summative_percentage:.2f}%)  {'✔ PASS' if summative_pass else '✘ FAIL'}")

    print(f"\n🎯 Final Grade : {final_grade:.2f} / 100")
    print(f"   GPA         : {gpa:.2f} / 5.0")

    print("\n" + "=" * 50)
    if overall_pass:
        print("   🎉 FINAL STATUS: PASSED")
    else:
        print("   ❌ FINAL STATUS: FAILED")
        if not formative_pass:
            print(f"      Reason: Formative score ({formative_percentage:.2f}%) is below 50%")
        if not summative_pass:
            print(f"      Reason: Summative score ({summative_percentage:.2f}%) is below 50%")
    print("=" * 50)

    if resubmit_candidates:
        print("\n📝 Resubmission Eligible (failed formative with highest weight):")
        for a in resubmit_candidates:
            print(f"   - {a['assignment']}  (Score: {a['score']:.1f}, Weight: {a['weight']:.1f}%)")
    elif failed_formative:
        print("\n📝 Note: All failed formative assignments share the same weight. "
              "All are listed above.")
    else:
        print("\n📝 No formative resubmission required.")

    print()


if __name__ == "__main__":
    course_data = load_csv_data()
    evaluate_grades(course_data)