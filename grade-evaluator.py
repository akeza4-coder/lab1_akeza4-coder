def evaluate_grades(data):
    print("\n--- Processing Grades ---")
    
    if not data:
        print("Error: The CSV file is empty.")
        return

    total_weight = 0
    formative_weight = 0
    summative_weight = 0
    
    formative_score_weighted = 0
    summative_score_weighted = 0
    
    failed_formative = []

    for row in data:
        score = row['score']
        weight = row['weight']
        group = row['group']

        # a) Check if scores are 0-100
        if not (0 <= score <= 100):
            print(f"Warning: Invalid score found: {score}")

        # track weights and weighted scores
        total_weight += weight
        if group == 'Formative':
            formative_weight += weight
            formative_score_weighted += (score * (weight / 100))
            if score < 50:
                failed_formative.append(row)
        elif group == 'Summative':
            summative_weight += weight
            summative_score_weighted += (score * (weight / 100))

    # b) Validate total weights
    if total_weight != 100 or formative_weight != 60 or summative_weight != 40:
        print(f"Weight Error! Total: {total_weight}, Formative: {formative_weight}, Summative: {summative_weight}")
        print("Weights must be: Total=100, Formative=60, Summative=40.")
        return

    # c) Calculate Final Grade and GPA
    final_grade = formative_score_weighted + summative_score_weighted
    gpa = (final_grade / 100) * 5.0

    # d) Determine Pass/Fail status (Needs 50% of the category weight)
    # Formative needs 30/60; Summative needs 20/40
    passed_formative = formative_score_weighted >= 30
    passed_summative = summative_score_weighted >= 20

    print(f"Final Grade: {final_grade:.2f}%")
    print(f"GPA: {gpa:.2f}")

    if passed_formative and passed_summative:
        print("Status: PASSED")
    else:
        print("Status: FAILED")
        
        # e) Resubmission Logic
        if failed_formative:
            # Find the max weight among failed formatives
            max_w = max(item['weight'] for item in failed_formative)
            to_redo = [f"{i['assignment']} ({i['weight']} weight)" for i in failed_formative if i['weight'] == max_w]
            print(f"Eligible for resubmission: {', '.join(to_redo)}")