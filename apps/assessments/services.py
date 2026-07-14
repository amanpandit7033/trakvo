from .models import TestResult

def calculate_ranks(test):
    """
    Fetches all results for a test, orders by marks descending, and assigns rank.
    Handles ties using standard competition ranking.
    Returns a list of dictionaries with (student, marks, rank, result).
    """
    results = TestResult.objects.filter(test=test).select_related('student').order_by('-marks_obtained')
    
    ranked_results = []
    if not results:
        return ranked_results

    current_rank = 1
    actual_rank = 1
    previous_marks = results[0].marks_obtained

    for i, result in enumerate(results):
        if result.marks_obtained < previous_marks:
            current_rank = actual_rank
        
        ranked_results.append({
            'result': result,
            'student': result.student,
            'marks': result.marks_obtained,
            'rank': current_rank,
            'max_marks': test.max_marks
        })
        
        actual_rank += 1
        previous_marks = result.marks_obtained

    return ranked_results
