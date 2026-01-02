"""
Export Routes
Handles PDF and DOCX export for tests and study materials
"""
from flask import Blueprint, request, jsonify, session, send_file
from models import Test, StudyMaterial
from services.pdf_export import generate_test_pdf, generate_study_material_pdf
from services.docx_export import generate_test_docx, generate_study_material_docx
import json

export_bp = Blueprint('export', __name__)


@export_bp.route('/api/export/pdf/<int:material_id>', methods=['GET'])
def export_pdf(material_id):
    """
    Export material as PDF

    Args:
        material_id: Material ID

    Query params:
        type: "test" or "study_material" (required)
        include_answers: "true" or "false" (optional, default: "true", only for tests)

    Returns:
        PDF file
    """
    # Check authentication
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    user_id = session['user_id']
    material_type = request.args.get('type')
    include_answers = request.args.get('include_answers', 'true').lower() == 'true'

    if not material_type or material_type not in ['test', 'study_material']:
        return jsonify({'error': 'type parameter required ("test" or "study_material")'}), 400

    try:
        if material_type == 'test':
            # Get test
            test = Test.query.filter_by(id=material_id, user_id=user_id).first()

            if not test:
                return jsonify({'error': 'Test not found'}), 404

            # Format test data
            test_data = {
                'id': test.id,
                'title': test.title,
                'created_at': test.created_at.isoformat(),
                'assignments': []
            }

            for assignment in test.assignments:
                assignment_data = {
                    'id': assignment.id,
                    'title': assignment.title,
                    'description': assignment.description,
                    'max_points': assignment.max_points,
                    'questions': []
                }

                for question in assignment.questions:
                    question_data = {
                        'id': question.id,
                        'question_text': question.question_text,
                        'question_type': question.question_type.value,
                        'correct_answer': question.correct_answer,
                        'points': question.points,
                        'options': []
                    }

                    # Add options
                    for option in question.options:
                        question_data['options'].append({
                            'id': option.id,
                            'option_text': option.option_text,
                            'is_correct': option.is_correct
                        })

                    assignment_data['questions'].append(question_data)

                test_data['assignments'].append(assignment_data)

            pdf_buffer = generate_test_pdf(test_data, include_answers=include_answers)

            answer_suffix = "_with_answers" if include_answers else "_student_version"
            filename = f"{test.title.replace(' ', '_')}{answer_suffix}.pdf"

            return send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )

        else:  # study_material
            # Get study material
            material = StudyMaterial.query.filter_by(id=material_id, user_id=user_id).first()

            if not material:
                return jsonify({'error': 'Study material not found'}), 404

            content_data = json.loads(material.content) if material.content else {}

            # Format material data
            material_data = {
                'id': material.id,
                'title': material.title,
                'created_at': material.created_at.isoformat(),
                'content': content_data
            }

            pdf_buffer = generate_study_material_pdf(material_data)

            filename = f"{material.title.replace(' ', '_')}_study_material.pdf"

            return send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )

    except Exception as e:
        return jsonify({
            'error': 'Failed to generate PDF',
            'details': str(e)
        }), 500


@export_bp.route('/api/export/docx/<int:material_id>', methods=['GET'])
def export_docx(material_id):
    """
    Export material as DOCX

    Args:
        material_id: Material ID

    Query params:
        type: "test" or "study_material" (required)

    Returns:
        DOCX file (student version for tests)
    """
    # Check authentication
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    user_id = session['user_id']
    material_type = request.args.get('type')

    if not material_type or material_type not in ['test', 'study_material']:
        return jsonify({'error': 'type parameter required ("test" or "study_material")'}), 400

    try:
        if material_type == 'test':
            # Get test
            test = Test.query.filter_by(id=material_id, user_id=user_id).first()

            if not test:
                return jsonify({'error': 'Test not found'}), 404

            # Format test data
            test_data = {
                'id': test.id,
                'title': test.title,
                'created_at': test.created_at.isoformat(),
                'assignments': []
            }

            for assignment in test.assignments:
                assignment_data = {
                    'id': assignment.id,
                    'title': assignment.title,
                    'description': assignment.description,
                    'max_points': assignment.max_points,
                    'questions': []
                }

                for question in assignment.questions:
                    question_data = {
                        'id': question.id,
                        'question_text': question.question_text,
                        'question_type': question.question_type.value,
                        'correct_answer': question.correct_answer,
                        'points': question.points,
                        'options': []
                    }

                    # Add options
                    for option in question.options:
                        question_data['options'].append({
                            'id': option.id,
                            'option_text': option.option_text,
                            'is_correct': option.is_correct
                        })

                    assignment_data['questions'].append(question_data)

                test_data['assignments'].append(assignment_data)

            docx_buffer = generate_test_docx(test_data)

            filename = f"{test.title.replace(' ', '_')}_student_version.docx"

            return send_file(
                docx_buffer,
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                as_attachment=True,
                download_name=filename
            )

        else:  # study_material
            # Get study material
            material = StudyMaterial.query.filter_by(id=material_id, user_id=user_id).first()

            if not material:
                return jsonify({'error': 'Study material not found'}), 404

            content_data = json.loads(material.content) if material.content else {}

            # Format material data
            material_data = {
                'id': material.id,
                'title': material.title,
                'created_at': material.created_at.isoformat(),
                'content': content_data
            }

            docx_buffer = generate_study_material_docx(material_data)

            filename = f"{material.title.replace(' ', '_')}_study_material.docx"

            return send_file(
                docx_buffer,
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                as_attachment=True,
                download_name=filename
            )

    except Exception as e:
        return jsonify({
            'error': 'Failed to generate DOCX',
            'details': str(e)
        }), 500
