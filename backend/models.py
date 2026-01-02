from extensions import db
from datetime import datetime
import enum

# Enum for question types
class QuestionType(enum.Enum):
    multiple_choice = 'multiple_choice'
    short_answer = 'short_answer'
    long_answer = 'long_answer'
    true_false = 'true_false'
    matching = 'matching'
    fill_in_blank = 'fill_in_blank'

# 1. USERS table
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    tests = db.relationship('Test', backref='user', cascade='all, delete-orphan', lazy=True)
    study_materials = db.relationship('StudyMaterial', backref='user', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

# 2. TESTS table
class Test(db.Model):
    __tablename__ = 'tests'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    assignments = db.relationship('Assignment', backref='test', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f'<Test {self.title}>'

# 3. STUDY_MATERIALS table
class StudyMaterial(db.Model):
    __tablename__ = 'study_materials'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)  # JSON: {summary: "...", terms: [{name, definition}]}
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<StudyMaterial {self.title}>'

# 4. ASSIGNMENTS table
class Assignment(db.Model):
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    max_points = db.Column(db.Integer, default=0)
    order_number = db.Column(db.Integer, nullable=False)

    # Relationships
    questions = db.relationship('Question', backref='assignment', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f'<Assignment {self.title}>'

# 5. QUESTIONS table
class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id', ondelete='CASCADE'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.Enum(QuestionType), nullable=False)
    correct_answer = db.Column(db.Text)
    points = db.Column(db.Integer, default=1)
    order_number = db.Column(db.Integer, nullable=False)

    # Relationships
    options = db.relationship('QuestionOption', backref='question', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f'<Question {self.question_text[:50]}>'

# 6. QUESTION_OPTIONS table (only for multiple_choice questions)
class QuestionOption(db.Model):
    __tablename__ = 'question_options'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    option_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    order_number = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<QuestionOption {self.option_text[:30]}>'
