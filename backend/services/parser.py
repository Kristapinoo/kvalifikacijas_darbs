"""
JSON Parser and Validator
Validates and processes JSON responses from Claude API
"""
from models import QuestionType

class ParserError(Exception):
    """Custom exception for parsing errors"""
    pass

def validate_test_response(data):
    """
    Validate test JSON response from Claude

    Args:
        data (dict): JSON response from Claude

    Returns:
        dict: Validated and cleaned data

    Raises:
        ParserError: If data structure is invalid
    """
    if not isinstance(data, dict):
        raise ParserError("Response must be a JSON object")

    if 'assignments' not in data:
        raise ParserError("Response missing 'assignments' field")

    if not isinstance(data['assignments'], list):
        raise ParserError("'assignments' must be a list")

    if len(data['assignments']) == 0:
        raise ParserError("Response must contain at least one assignment")

    for i, assignment in enumerate(data['assignments']):
        _validate_assignment(assignment, i)

    return data

def validate_study_material_response(data):
    """
    Validate study material JSON response from Claude

    Args:
        data (dict): JSON response from Claude

    Returns:
        dict: Validated and cleaned data

    Raises:
        ParserError: If data structure is invalid
    """
    if not isinstance(data, dict):
        raise ParserError("Response must be a JSON object")

    if 'summary' not in data:
        raise ParserError("Response missing 'summary' field")

    if 'terms' not in data:
        raise ParserError("Response missing 'terms' field")

    if not isinstance(data['summary'], str):
        raise ParserError("'summary' must be a string")

    if not isinstance(data['terms'], list):
        raise ParserError("'terms' must be a list")

    if len(data['summary'].strip()) == 0:
        raise ParserError("'summary' cannot be empty")

    for i, term in enumerate(data['terms']):
        _validate_term(term, i)

    return data

def _validate_assignment(assignment, index):
    """Validate a single assignment"""
    required_fields = ['title', 'description', 'max_points', 'questions']

    for field in required_fields:
        if field not in assignment:
            raise ParserError(f"Assignment {index} missing required field: '{field}'")

    if not isinstance(assignment['title'], str):
        raise ParserError(f"Assignment {index} 'title' must be a string")

    if not isinstance(assignment['description'], str):
        raise ParserError(f"Assignment {index} 'description' must be a string")

    if not isinstance(assignment['max_points'], (int, float)):
        raise ParserError(f"Assignment {index} 'max_points' must be a number")

    if not isinstance(assignment['questions'], list):
        raise ParserError(f"Assignment {index} 'questions' must be a list")

    if len(assignment['questions']) == 0:
        raise ParserError(f"Assignment {index} must contain at least one question")

    for j, question in enumerate(assignment['questions']):
        _validate_question(question, index, j)

def _validate_question(question, assignment_index, question_index):
    """Validate a single question"""
    required_fields = ['question_text', 'question_type', 'correct_answer', 'points']

    for field in required_fields:
        if field not in question:
            raise ParserError(
                f"Assignment {assignment_index}, Question {question_index} "
                f"missing required field: '{field}'"
            )

    if not isinstance(question['question_text'], str):
        raise ParserError(
            f"Assignment {assignment_index}, Question {question_index} "
            f"'question_text' must be a string"
        )

    if not isinstance(question['question_type'], str):
        raise ParserError(
            f"Assignment {assignment_index}, Question {question_index} "
            f"'question_type' must be a string"
        )

    # Validate question type is valid
    valid_types = [qt.value for qt in QuestionType]
    if question['question_type'] not in valid_types:
        raise ParserError(
            f"Assignment {assignment_index}, Question {question_index} "
            f"invalid 'question_type': '{question['question_type']}'. "
            f"Must be one of: {', '.join(valid_types)}"
        )

    if not isinstance(question['correct_answer'], str):
        raise ParserError(
            f"Assignment {assignment_index}, Question {question_index} "
            f"'correct_answer' must be a string"
        )

    if not isinstance(question['points'], (int, float)):
        raise ParserError(
            f"Assignment {assignment_index}, Question {question_index} "
            f"'points' must be a number"
        )

    # Validate options field exists (even if empty for some question types)
    if 'options' not in question:
        # Add empty options if not present
        question['options'] = []

    if not isinstance(question['options'], list):
        raise ParserError(
            f"Assignment {assignment_index}, Question {question_index} "
            f"'options' must be a list"
        )

    # For multiple_choice and true_false, validate options
    if question['question_type'] in ['multiple_choice', 'true_false', 'matching']:
        if len(question['options']) == 0:
            raise ParserError(
                f"Assignment {assignment_index}, Question {question_index} "
                f"question type '{question['question_type']}' requires options"
            )

def _validate_term(term, index):
    """Validate a single term"""
    required_fields = ['name', 'definition']

    for field in required_fields:
        if field not in term:
            raise ParserError(f"Term {index} missing required field: '{field}'")

    if not isinstance(term['name'], str):
        raise ParserError(f"Term {index} 'name' must be a string")

    if not isinstance(term['definition'], str):
        raise ParserError(f"Term {index} 'definition' must be a string")

    if len(term['name'].strip()) == 0:
        raise ParserError(f"Term {index} 'name' cannot be empty")

    if len(term['definition'].strip()) == 0:
        raise ParserError(f"Term {index} 'definition' cannot be empty")

def clean_test_data(data):
    """
    Clean and normalize test data for database insertion

    Args:
        data (dict): Validated test data

    Returns:
        dict: Cleaned data ready for database
    """
    # Ensure proper order numbers for assignments
    for i, assignment in enumerate(data['assignments']):
        assignment['order_number'] = i + 1

        # Ensure proper order numbers for questions
        for j, question in enumerate(assignment['questions']):
            question['order_number'] = j + 1

            question['points'] = float(question['points'])

            # Ensure options is a list (empty for non-multiple-choice)
            if 'options' not in question:
                question['options'] = []

            # Normalize options format: convert strings to objects
            normalized_options = []
            correct_answer = question.get('correct_answer', '')

            for option in question['options']:
                if isinstance(option, str):
                    # Claude returned simple string - convert to object
                    normalized_options.append({
                        'option_text': option,
                        'is_correct': option == correct_answer
                    })
                elif isinstance(option, dict):
                    # Already in correct format
                    if 'option_text' not in option:
                        # Handle legacy format if needed
                        option['option_text'] = option.get('text', str(option))
                    if 'is_correct' not in option:
                        option['is_correct'] = option.get('option_text') == correct_answer
                    normalized_options.append(option)

            question['options'] = normalized_options

        # Convert max_points to int/float
        assignment['max_points'] = float(assignment['max_points'])

    return data

def clean_study_material_data(data):
    """
    Clean and normalize study material data for database insertion

    Args:
        data (dict): Validated study material data

    Returns:
        dict: Cleaned data ready for database (as JSON)
    """
    data['summary'] = data['summary'].strip()

    for term in data['terms']:
        term['name'] = term['name'].strip()
        term['definition'] = term['definition'].strip()

    return data
