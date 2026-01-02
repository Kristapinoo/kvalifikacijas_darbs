"""
Materials CRUD Routes
Handles viewing, updating, and deleting tests and study materials
"""
from flask import Blueprint, request, jsonify, session
from extensions import db
from models import Test, StudyMaterial, Assignment, Question, QuestionOption, QuestionType, User
import json

materials_bp = Blueprint('materials', __name__)

@materials_bp.route('/api/materials', methods=['GET'])
def get_all_materials():
    """
    Get all materials (tests + study materials) for logged-in user

    Returns:
        JSON array with all materials
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    user_id = session['user_id']

    try:
        tests = Test.query.filter_by(user_id=user_id).order_by(Test.created_at.desc()).all()

        study_materials = StudyMaterial.query.filter_by(user_id=user_id).order_by(StudyMaterial.created_at.desc()).all()

        materials = []


        for test in tests:
            materials.append({
                'id': test.id,
                'type': 'test',
                'title': test.title,
                'created_at': test.created_at.isoformat(),
                'assignments_count': len(test.assignments),
                'total_questions': sum(len(a.questions) for a in test.assignments)
            })


        for material in study_materials:
            content_data = json.loads(material.content) if material.content else {}
            materials.append({
                'id': material.id,
                'type': 'study_material',
                'title': material.title,
                'created_at': material.created_at.isoformat(),
                'terms_count': len(content_data.get('terms', []))
            })

        materials.sort(key=lambda x: x['created_at'], reverse=True)

        return jsonify({
            'success': True,
            'materials': materials,
            'total': len(materials)
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch materials',
            'details': str(e)
        }), 500

@materials_bp.route('/api/materials/<int:material_id>', methods=['GET'])
def get_material(material_id):
    """
    Get specific material by ID (with full details)

    Args:
        material_id: Material ID

    Query params:
        type: "test" or "study_material" (required)

    Returns:
        JSON with complete material data
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    user_id = session['user_id']
    material_type = request.args.get('type')

    if not material_type or material_type not in ['test', 'study_material']:
        return jsonify({'error': 'type parameter required ("test" or "study_material")'}), 400

    try:
        if material_type == 'test':
            test = Test.query.filter_by(id=material_id, user_id=user_id).first()

            if not test:
                return jsonify({'error': 'Test not found'}), 404


            assignments_data = []
            for assignment in test.assignments:
                questions_data = []
                for question in assignment.questions:
                    options_data = [
                        {
                            'id': opt.id,
                            'option_text': opt.option_text,
                            'is_correct': opt.is_correct,
                            'order_number': opt.order_number
                        }
                        for opt in question.options
                    ]

                    questions_data.append({
                        'id': question.id,
                        'question_text': question.question_text,
                        'question_type': question.question_type.value,
                        'correct_answer': question.correct_answer,
                        'points': question.points,
                        'order_number': question.order_number,
                        'options': options_data
                    })

                assignments_data.append({
                    'id': assignment.id,
                    'title': assignment.title,
                    'description': assignment.description,
                    'max_points': assignment.max_points,
                    'order_number': assignment.order_number,
                    'questions': questions_data
                })

            return jsonify({
                'success': True,
                'type': 'test',
                'id': test.id,
                'title': test.title,
                'created_at': test.created_at.isoformat(),
                'assignments': assignments_data
            }), 200

        else:  # study_material
            material = StudyMaterial.query.filter_by(id=material_id, user_id=user_id).first()

            if not material:
                return jsonify({'error': 'Study material not found'}), 404


            content_data = json.loads(material.content) if material.content else {}

            return jsonify({
                'success': True,
                'type': 'study_material',
                'id': material.id,
                'title': material.title,
                'created_at': material.created_at.isoformat(),
                'content': content_data
            }), 200

    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch material',
            'details': str(e)
        }), 500

@materials_bp.route('/api/materials/<int:material_id>', methods=['PUT'])
def update_material(material_id):
    """
    Update material (test or study material)

    Args:
        material_id: Material ID

    Request body (JSON):
        - type: "test" or "study_material"
        - title: New title (optional)
        - For tests: assignments array with questions
        - For study materials: content object

    Returns:
        JSON with success message
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    user_id = session['user_id']

    try:
        data = request.get_json()

        if not data or 'type' not in data:
            return jsonify({'error': 'type is required'}), 400

        material_type = data['type']

        if material_type == 'test':
            test = Test.query.filter_by(id=material_id, user_id=user_id).first()

            if not test:
                return jsonify({'error': 'Test not found'}), 404


            if 'title' in data and data['title']:
                test.title = data['title']

            if 'assignments' in data:
                # Delete existing assignments (CASCADE will delete questions and options)
                for assignment in test.assignments:
                    db.session.delete(assignment)


                for assignment_data in data['assignments']:
                    assignment = Assignment(
                        test_id=test.id,
                        title=assignment_data['title'],
                        description=assignment_data.get('description', ''),
                        max_points=assignment_data.get('max_points', 0),
                        order_number=assignment_data.get('order_number', 1)
                    )
                    db.session.add(assignment)
                    db.session.flush()


                    for question_data in assignment_data.get('questions', []):
                        question = Question(
                            assignment_id=assignment.id,
                            question_text=question_data['question_text'],
                            question_type=QuestionType[question_data['question_type']],
                            correct_answer=question_data.get('correct_answer', ''),
                            points=question_data.get('points', 0),
                            order_number=question_data.get('order_number', 1)
                        )
                        db.session.add(question)
                        db.session.flush()


                        for option_data in question_data.get('options', []):
                            option = QuestionOption(
                                question_id=question.id,
                                option_text=option_data['option_text'],
                                is_correct=option_data.get('is_correct', False),
                                order_number=option_data.get('order_number', 1)
                            )
                            db.session.add(option)

            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Test updated successfully',
                'id': test.id
            }), 200

        else:  # study_material
            material = StudyMaterial.query.filter_by(id=material_id, user_id=user_id).first()

            if not material:
                return jsonify({'error': 'Study material not found'}), 404


            if 'title' in data and data['title']:
                material.title = data['title']


            if 'content' in data:
                material.content = json.dumps(data['content'], ensure_ascii=False)

            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Study material updated successfully',
                'id': material.id
            }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to update material',
            'details': str(e)
        }), 500

@materials_bp.route('/api/materials/<int:material_id>', methods=['DELETE'])
def delete_material(material_id):
    """
    Delete material (test or study material)

    Args:
        material_id: Material ID

    Query params:
        type: "test" or "study_material" (required)

    Returns:
        JSON with success message
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    user_id = session['user_id']
    material_type = request.args.get('type')

    if not material_type or material_type not in ['test', 'study_material']:
        return jsonify({'error': 'type parameter required ("test" or "study_material")'}), 400

    try:
        if material_type == 'test':
            test = Test.query.filter_by(id=material_id, user_id=user_id).first()

            if not test:
                return jsonify({'error': 'Test not found'}), 404

            db.session.delete(test)  # CASCADE will delete assignments, questions, options
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Test deleted successfully'
            }), 200

        else:  # study_material
            material = StudyMaterial.query.filter_by(id=material_id, user_id=user_id).first()

            if not material:
                return jsonify({'error': 'Study material not found'}), 404

            db.session.delete(material)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Study material deleted successfully'
            }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to delete material',
            'details': str(e)
        }), 500

@materials_bp.route('/api/materials/<int:material_id>/generate-questions', methods=['POST'])
def generate_additional_questions(material_id):
    """
    Generate additional questions for an existing assignment using Claude API

    Args:
        material_id: Test ID

    Request body (JSON):
        - assignment_id: Assignment ID (required)
        - assignment_title: Assignment title for context (required)
        - assignment_description: Assignment description for context (optional)
        - num_questions: Number of questions to generate (1-20, default: 3)
        - difficulty: "easy", "medium", or "hard" (default: "medium")

    Returns:
        JSON with generated questions array
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    user_id = session['user_id']

    try:
        data = request.get_json()

        if not data or 'assignment_id' not in data:
            return jsonify({'error': 'assignment_id is required'}), 400

        assignment_id = data['assignment_id']
        assignment_title = data.get('assignment_title', '')
        assignment_description = data.get('assignment_description', '')
        num_questions = data.get('num_questions', 3)
        difficulty = data.get('difficulty', 'medium')


        if num_questions < 1 or num_questions > 20:
            return jsonify({'error': 'num_questions must be between 1 and 20'}), 400

        if difficulty not in ['easy', 'medium', 'hard']:
            return jsonify({'error': 'difficulty must be "easy", "medium", or "hard"'}), 400

        test = Test.query.filter_by(id=material_id, user_id=user_id).first()
        if not test:
            return jsonify({'error': 'Test not found'}), 404

        # Verify assignment exists and belongs to this test
        assignment = Assignment.query.filter_by(id=assignment_id, test_id=test.id).first()
        if not assignment:
            return jsonify({'error': 'Assignment not found'}), 404

        from services.claude_api import get_claude_client
        from services.parser import validate_test_response, clean_test_data, ParserError

        try:
            client = get_claude_client()
        except Exception as e:
            return jsonify({'error': f'Failed to initialize AI client: {str(e)}'}), 500

        context = f"Assignment: {assignment_title}\n"
        if assignment_description:
            context += f"Description: {assignment_description}\n"

        try:
            response = client.generate_additional_questions(
                context=context,
                num_questions=num_questions,
                difficulty=difficulty
            )
        except Exception as e:
            return jsonify({'error': f'AI generation failed: {str(e)}'}), 500

        try:
            validated_data = validate_test_response(response)
            cleaned_data = clean_test_data(validated_data)
        except Exception as e:
            return jsonify({'error': f'Failed to process AI response: {str(e)}'}), 500

        # Get the questions from the first (and only) assignment in the response
        if not cleaned_data.get('assignments') or len(cleaned_data['assignments']) == 0:
            return jsonify({'error': 'No questions generated'}), 500

        generated_questions = cleaned_data['assignments'][0].get('questions', [])

        # Determine the starting order_number
        max_order = max([q.order_number for q in assignment.questions], default=0)

        created_questions = []
        for idx, question_data in enumerate(generated_questions):
            question = Question(
                assignment_id=assignment.id,
                question_text=question_data['question_text'],
                question_type=QuestionType[question_data['question_type']],
                correct_answer=question_data['correct_answer'],
                points=question_data['points'],
                order_number=max_order + idx + 1
            )
            db.session.add(question)
            db.session.flush()  # Get question ID

            # Create question options (for multiple choice, true/false, etc.)
            options_data = []
            if question_data.get('options'):
                for i, option_item in enumerate(question_data['options']):
                    # Handle both dict and string formats
                    if isinstance(option_item, dict):
                        option_text = option_item.get('option_text', '')
                        is_correct = option_item.get('is_correct', False)
                    else:
                        option_text = str(option_item)
                        is_correct = option_text == question_data['correct_answer']

                    option = QuestionOption(
                        question_id=question.id,
                        option_text=option_text,
                        is_correct=is_correct,
                        order_number=i + 1
                    )
                    db.session.add(option)
                    options_data.append({
                        'id': option.id,
                        'option_text': option_text,
                        'is_correct': is_correct,
                        'order_number': i + 1
                    })

            created_questions.append({
                'id': question.id,
                'question_text': question_data['question_text'],
                'question_type': question_data['question_type'],
                'correct_answer': question_data['correct_answer'],
                'points': question_data['points'],
                'order_number': max_order + idx + 1,
                'options': options_data
            })

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Successfully generated {len(created_questions)} questions',
            'questions': created_questions
        }), 201

    except ParserError as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to parse Claude API response',
            'details': str(e)
        }), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to generate questions',
            'details': str(e)
        }), 500
