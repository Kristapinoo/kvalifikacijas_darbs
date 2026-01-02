"""
Material Generation Routes
Handles test and study material generation using Claude API
"""
from flask import Blueprint, request, jsonify, session
from extensions import db
from models import Test, StudyMaterial, Assignment, Question, QuestionOption, QuestionType
from services.claude_api import get_claude_client
from services.parser import (
    validate_test_response,
    validate_study_material_response,
    clean_test_data,
    clean_study_material_data,
    ParserError
)
import json
import os
from werkzeug.utils import secure_filename
import PyPDF2
from docx import Document

generate_bp = Blueprint('generate', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(file):
    """
    Extract text content from uploaded file

    Args:
        file: FileStorage object from Flask

    Returns:
        str: Extracted text content

    Raises:
        ValueError: If file type is not supported or extraction fails
    """
    filename = secure_filename(file.filename)
    file_ext = filename.rsplit('.', 1)[1].lower()

    try:
        if file_ext == 'txt':
            return file.read().decode('utf-8')

        elif file_ext == 'pdf':
            pdf_reader = PyPDF2.PdfReader(file)
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text() + '\n'
            return text.strip()

        elif file_ext == 'docx':
            doc = Document(file)
            text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()

        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

    except Exception as e:
        raise ValueError(f"Failed to extract text from file: {str(e)}")

@generate_bp.route('/api/generate', methods=['POST'])
def generate_material():
    """
    Generate test or study material using Claude API

    Request (multipart/form-data or JSON):
        - material_type: "test" or "study_material" (required)
        - title: Material title (required)
        - content: Text content (required if no file)
        - file: Uploaded file (PDF, DOCX, TXT) (required if no content)
        - num_questions: Number of questions for tests (optional, default: 10)
        - difficulty: Test difficulty - "easy", "medium", "hard" (optional, default: "medium")

    Returns:
        JSON with generated material data and database ID
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    user_id = session['user_id']

    try:
        material_type = request.form.get('material_type')
        title = request.form.get('title')
        content = request.form.get('content')
        num_questions = request.form.get('num_questions', 10, type=int)
        difficulty = request.form.get('difficulty', 'medium')

        if not material_type:
            return jsonify({'error': 'material_type is required'}), 400

        if material_type not in ['test', 'study_material']:
            return jsonify({'error': 'material_type must be "test" or "study_material"'}), 400

        if not title or len(title.strip()) == 0:
            return jsonify({'error': 'title is required'}), 400

        if not content:
            if 'file' not in request.files:
                return jsonify({'error': 'Either content or file is required'}), 400

            file = request.files['file']

            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400

            if not allowed_file(file.filename):
                return jsonify({
                    'error': f'File type not allowed. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
                }), 400

            try:
                content = extract_text_from_file(file)
            except ValueError as e:
                return jsonify({'error': str(e)}), 400

        if not content or len(content.strip()) == 0:
            return jsonify({'error': 'Content cannot be empty'}), 400

        if material_type == 'test':
            if num_questions < 1 or num_questions > 50:
                return jsonify({'error': 'num_questions must be between 1 and 50'}), 400

            if difficulty not in ['easy', 'medium', 'hard']:
                return jsonify({'error': 'difficulty must be "easy", "medium", or "hard"'}), 400

        client = get_claude_client()

        if material_type == 'test':
            response = client.generate_test(
                content=content,
                num_questions=num_questions,
                difficulty=difficulty
            )

            validated_data = validate_test_response(response)
            cleaned_data = clean_test_data(validated_data)

            test_id = save_test_to_database(user_id, title, cleaned_data)

            return jsonify({
                'success': True,
                'message': 'Test generated successfully',
                'material_type': 'test',
                'id': test_id,
                'data': cleaned_data
            }), 201

        else:
            response = client.generate_study_material(content=content)

            validated_data = validate_study_material_response(response)
            cleaned_data = clean_study_material_data(validated_data)

            material_id = save_study_material_to_database(user_id, title, cleaned_data)

            return jsonify({
                'success': True,
                'message': 'Study material generated successfully',
                'material_type': 'study_material',
                'id': material_id,
                'data': cleaned_data
            }), 201

    except ParserError as e:
        print(f"❌ ParserError: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to parse Claude API response',
            'details': str(e)
        }), 500
    except Exception as e:
        print(f"❌ Generation Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to generate material',
            'details': str(e)
        }), 500

def save_test_to_database(user_id, title, test_data):
    """
    Save generated test to database

    Args:
        user_id (int): User ID
        title (str): Test title
        test_data (dict): Cleaned test data from Claude

    Returns:
        int: Test ID
    """
    test = Test(user_id=user_id, title=title)
    db.session.add(test)
    db.session.flush()

    for assignment_data in test_data['assignments']:
        assignment = Assignment(
            test_id=test.id,
            title=assignment_data['title'],
            description=assignment_data['description'],
            max_points=assignment_data['max_points'],
            order_number=assignment_data['order_number']
        )
        db.session.add(assignment)
        db.session.flush()

        for question_data in assignment_data['questions']:
            question = Question(
                assignment_id=assignment.id,
                question_text=question_data['question_text'],
                question_type=QuestionType[question_data['question_type']],
                correct_answer=question_data['correct_answer'],
                points=question_data['points'],
                order_number=question_data['order_number']
            )
            db.session.add(question)
            db.session.flush()

            # Create question options (for multiple choice, true/false, etc.)
            if question_data.get('options'):
                for i, option_data in enumerate(question_data['options']):
                    option = QuestionOption(
                        question_id=question.id,
                        option_text=option_data['option_text'],
                        is_correct=option_data['is_correct'],
                        order_number=i + 1
                    )
                    db.session.add(option)

    db.session.commit()
    return test.id

def save_study_material_to_database(user_id, title, material_data):
    """
    Save generated study material to database

    Args:
        user_id (int): User ID
        title (str): Material title
        material_data (dict): Cleaned material data from Claude

    Returns:
        int: Study material ID
    """
    # Store material_data as JSON string
    material = StudyMaterial(
        user_id=user_id,
        title=title,
        content=json.dumps(material_data, ensure_ascii=False)
    )
    db.session.add(material)
    db.session.commit()

    return material.id
