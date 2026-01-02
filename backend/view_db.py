"""
Database viewer utility
Run this to see all data in the database
"""
from app import app
from extensions import db
from models import User, Test, StudyMaterial, Assignment, Question, QuestionOption
from tabulate import tabulate

def view_database():
    """Display all database contents in a readable format"""
    with app.app_context():
        print("\n" + "="*80)
        print("DATABASE CONTENTS")
        print("="*80)

        # Users table
        print("\nUSERS TABLE")
        print("-" * 80)
        users = User.query.all()
        if users:
            user_data = []
            for user in users:
                user_data.append([
                    user.id,
                    user.email,
                    user.password_hash[:20] + "...",  # Show first 20 chars
                    user.created_at.strftime("%Y-%m-%d %H:%M:%S")
                ])
            print(tabulate(user_data, headers=["ID", "Email", "Password Hash (truncated)", "Created At"], tablefmt="grid"))
        else:
            print("  No users found")

        # Tests table
        print("\nTESTS TABLE")
        print("-" * 80)
        tests = Test.query.all()
        if tests:
            test_data = []
            for test in tests:
                test_data.append([
                    test.id,
                    test.user_id,
                    test.title,
                    test.created_at.strftime("%Y-%m-%d %H:%M:%S")
                ])
            print(tabulate(test_data, headers=["ID", "User ID", "Title", "Created At"], tablefmt="grid"))
        else:
            print("  No tests found")

        # Study Materials table
        print("\nSTUDY MATERIALS TABLE")
        print("-" * 80)
        materials = StudyMaterial.query.all()
        if materials:
            material_data = []
            for material in materials:
                content_preview = str(material.content)[:50] + "..." if material.content else "None"
                material_data.append([
                    material.id,
                    material.user_id,
                    material.title,
                    content_preview,
                    material.created_at.strftime("%Y-%m-%d %H:%M:%S")
                ])
            print(tabulate(material_data, headers=["ID", "User ID", "Title", "Content (preview)", "Created At"], tablefmt="grid"))
        else:
            print("  No study materials found")

        # Assignments table
        print("\nASSIGNMENTS TABLE")
        print("-" * 80)
        assignments = Assignment.query.all()
        if assignments:
            assignment_data = []
            for assignment in assignments:
                assignment_data.append([
                    assignment.id,
                    assignment.test_id,
                    assignment.title,
                    assignment.description[:30] + "..." if assignment.description and len(assignment.description) > 30 else assignment.description,
                    assignment.max_points,
                    assignment.order_number
                ])
            print(tabulate(assignment_data, headers=["ID", "Test ID", "Title", "Description", "Max Points", "Order"], tablefmt="grid"))
        else:
            print("  No assignments found")

        # Questions table
        print("\nQUESTIONS TABLE")
        print("-" * 80)
        questions = Question.query.all()
        if questions:
            question_data = []
            for question in questions:
                question_data.append([
                    question.id,
                    question.assignment_id,
                    question.question_text[:40] + "..." if len(question.question_text) > 40 else question.question_text,
                    question.question_type.value,
                    question.correct_answer[:20] + "..." if question.correct_answer and len(question.correct_answer) > 20 else question.correct_answer,
                    question.points,
                    question.order_number
                ])
            print(tabulate(question_data, headers=["ID", "Assignment ID", "Question Text", "Type", "Correct Answer", "Points", "Order"], tablefmt="grid"))
        else:
            print("  No questions found")

        # Question Options table
        print("\nQUESTION OPTIONS TABLE")
        print("-" * 80)
        options = QuestionOption.query.all()
        if options:
            option_data = []
            for option in options:
                option_data.append([
                    option.id,
                    option.question_id,
                    option.option_text[:40] + "..." if len(option.option_text) > 40 else option.option_text,
                    "✓" if option.is_correct else "✗",
                    option.order_number
                ])
            print(tabulate(option_data, headers=["ID", "Question ID", "Option Text", "Correct", "Order"], tablefmt="grid"))
        else:
            print("  No question options found")

        print("\n" + "="*80)
        print(f"Total Users: {len(users)}")
        print(f"Total Tests: {len(tests)}")
        print(f"Total Study Materials: {len(materials)}")
        print(f"Total Assignments: {len(assignments)}")
        print(f"Total Questions: {len(questions)}")
        print(f"Total Question Options: {len(options)}")
        print("="*80 + "\n")

if __name__ == '__main__':
    view_database()
