/**
 * Material View Page
 * Displays and allows editing of tests and study materials
 */
import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, useParams } from 'react-router-dom';
import api from '../api/axios';

interface QuestionOption {
  id: number;
  option_text: string;
  is_correct: boolean;
  order_number: number;
}

interface Question {
  id: number;
  question_text: string;
  question_type: string;
  correct_answer: string;
  points: number;
  order_number: number;
  options?: QuestionOption[];
}

interface Assignment {
  id: number;
  title: string;
  description: string;
  max_points: number;
  order_number: number;
  questions: Question[];
}

interface TestData {
  id: number;
  title: string;
  created_at: string;
  assignments: Assignment[];
}

interface StudyMaterialData {
  id: number;
  title: string;
  created_at: string;
  summary: string;
  terms: Array<{ name: string; definition: string }>;
}

const MaterialView: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { id: materialId } = useParams();
  const materialType = searchParams.get('type') as 'test' | 'study_material';

  const [testData, setTestData] = useState<TestData | null>(null);
  const [studyMaterialData, setStudyMaterialData] = useState<StudyMaterialData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editMode, setEditMode] = useState(false);
  const [saving, setSaving] = useState(false);

  // State for AI question generation
  const [showAIDialog, setShowAIDialog] = useState(false);
  const [selectedAssignmentId, setSelectedAssignmentId] = useState<number | null>(null);
  const [aiNumQuestions, setAiNumQuestions] = useState(3);
  const [aiDifficulty, setAiDifficulty] = useState<'easy' | 'medium' | 'hard'>('medium');
  const [generatingQuestions, setGeneratingQuestions] = useState(false);

  useEffect(() => {
    if (materialId && materialType) {
      fetchMaterial();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchMaterial = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await api.get(`/api/materials/${materialId}?type=${materialType}`);

      if (materialType === 'test') {
        setTestData(response.data);
      } else {
        const { id, title, created_at, content } = response.data;
        setStudyMaterialData({
          id,
          title,
          created_at,
          summary: content?.summary || '',
          terms: content?.terms || []
        });
      }
    } catch (err) {
      const error = err as { response?: { data?: { error?: string } } };
      setError(error.response?.data?.error || 'Neizdevās ielādēt materiālu');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!editMode) {
      setEditMode(true);
      return;
    }

    try {
      setSaving(true);

      let data;
      if (materialType === 'test') {
        data = { type: 'test', ...testData };
      } else {
        data = {
          type: 'study_material',
          title: studyMaterialData?.title,
          content: {
            summary: studyMaterialData?.summary || '',
            terms: studyMaterialData?.terms || []
          }
        };
      }

      await api.put(`/api/materials/${materialId}`, data);

      // Reload data from server to get real database IDs
      await fetchMaterial();

      setEditMode(false);
      alert('Izmaiņas saglabātas veiksmīgi!');
    } catch (err) {
      const error = err as { response?: { data?: { error?: string } } };
      alert(error.response?.data?.error || 'Neizdevās saglabāt izmaiņas');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Vai tiešām vēlaties dzēst šo materiālu?')) {
      return;
    }

    try {
      await api.delete(`/api/materials/${materialId}?type=${materialType}`);
      navigate('/dashboard');
    } catch {
      alert('Neizdevās dzēst materiālu');
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const updateQuestion = (assignmentId: number, questionId: number, field: string, value: unknown) => {
    if (!testData) return;

    const updatedAssignments = testData.assignments.map(assignment => {
      if (assignment.id === assignmentId) {
        const updatedQuestions = assignment.questions.map(q => {
          if (q.id === questionId) {
            const updated = { ...q, [field]: value };

            // When changing question type, adjust options accordingly
            if (field === 'question_type') {
              const optionTypes = ['multiple_choice', 'true_false', 'matching'];
              const newType = value as string;
              const oldType = q.question_type;

              if (!optionTypes.includes(newType)) {
                // Clear options for non-option question types
                updated.options = [];
                updated.correct_answer = '';
              } else if (newType === 'true_false' && oldType !== 'true_false') {
                // Set up true/false options (only if not already true/false)
                updated.options = [
                  { id: Date.now(), option_text: 'Patiess', is_correct: false, order_number: 1 },
                  { id: Date.now() + 1, option_text: 'Nepatiess', is_correct: false, order_number: 2 }
                ];
              } else if (newType === 'multiple_choice' && oldType !== 'multiple_choice') {
                // When changing TO multiple choice, ensure 4 options
                const currentOptions = updated.options || [];
                if (currentOptions.length < 4) {
                  // Expand to 4 options
                  const newOptions = [...currentOptions];
                  const lettersNeeded = 4 - currentOptions.length;
                  const startLetter = currentOptions.length;

                  for (let i = 0; i < lettersNeeded; i++) {
                    const letter = String.fromCharCode(65 + startLetter + i); // A, B, C, D
                    newOptions.push({
                      id: Date.now() + i,
                      option_text: `Variants ${letter}`,
                      is_correct: false,
                      order_number: startLetter + i + 1
                    });
                  }
                  updated.options = newOptions;
                } else if (currentOptions.length === 0) {
                  // No options at all, create 4
                  updated.options = [
                    { id: Date.now(), option_text: 'Variants A', is_correct: false, order_number: 1 },
                    { id: Date.now() + 1, option_text: 'Variants B', is_correct: false, order_number: 2 },
                    { id: Date.now() + 2, option_text: 'Variants C', is_correct: false, order_number: 3 },
                    { id: Date.now() + 3, option_text: 'Variants D', is_correct: false, order_number: 4 }
                  ];
                }
              } else if (newType === 'matching' && oldType !== 'matching') {
                // When changing TO matching, create pairs format
                // For matching, we'll use option_text format: "LeftItem|RightItem"
                const currentOptions = updated.options || [];
                if (currentOptions.length < 3) {
                  // Create 3 default matching pairs
                  updated.options = [
                    { id: Date.now(), option_text: 'Vienums 1|Atbilstība 1', is_correct: true, order_number: 1 },
                    { id: Date.now() + 1, option_text: 'Vienums 2|Atbilstība 2', is_correct: true, order_number: 2 },
                    { id: Date.now() + 2, option_text: 'Vienums 3|Atbilstība 3', is_correct: true, order_number: 3 }
                  ];
                }
              }
            }

            return updated;
          }
          return q;
        });

        // Auto-calculate max_points when question points change
        const maxPoints = field === 'points'
          ? updatedQuestions.reduce((sum, q) => sum + (q.points || 0), 0)
          : assignment.max_points;

        return {
          ...assignment,
          questions: updatedQuestions,
          max_points: maxPoints
        };
      }
      return assignment;
    });

    setTestData({
      ...testData,
      assignments: updatedAssignments
    });
  };

  const updateOption = (assignmentId: number, questionId: number, optionId: number, field: string, value: unknown) => {
    if (!testData) return;

    const updatedAssignments = testData.assignments.map(assignment => {
      if (assignment.id === assignmentId) {
        const updatedQuestions = assignment.questions.map(q => {
          if (q.id === questionId && q.options) {
            const updatedOptions = q.options.map(opt =>
              opt.id === optionId ? { ...opt, [field]: value } : opt
            );
            return { ...q, options: updatedOptions };
          }
          return q;
        });

        return {
          ...assignment,
          questions: updatedQuestions
        };
      }
      return assignment;
    });

    setTestData({
      ...testData,
      assignments: updatedAssignments
    });
  };

  const updateAssignment = (assignmentId: number, field: string, value: unknown) => {
    if (!testData) return;

    setTestData({
      ...testData,
      assignments: testData.assignments.map(assignment =>
        assignment.id === assignmentId ? { ...assignment, [field]: value } : assignment
      )
    });
  };

  const deleteAssignment = (assignmentId: number) => {
    if (!testData) return;
    if (!window.confirm('Vai tiešām vēlaties dzēst šo uzdevumu?')) return;

    setTestData({
      ...testData,
      assignments: testData.assignments.filter(a => a.id !== assignmentId)
    });
  };

  const deleteQuestion = (assignmentId: number, questionId: number) => {
    if (!testData) return;
    if (!window.confirm('Vai tiešām vēlaties dzēst šo jautājumu?')) return;

    const updatedAssignments = testData.assignments.map(assignment => {
      if (assignment.id === assignmentId) {
        const updatedQuestions = assignment.questions.filter(q => q.id !== questionId);
        // Recalculate max_points
        const maxPoints = updatedQuestions.reduce((sum, q) => sum + (q.points || 0), 0);

        return {
          ...assignment,
          questions: updatedQuestions,
          max_points: maxPoints
        };
      }
      return assignment;
    });

    setTestData({
      ...testData,
      assignments: updatedAssignments
    });
  };

  const moveAssignmentUp = (assignmentId: number) => {
    if (!testData) return;

    const index = testData.assignments.findIndex(a => a.id === assignmentId);
    if (index <= 0) return;

    const newAssignments = [...testData.assignments];
    [newAssignments[index - 1], newAssignments[index]] = [newAssignments[index], newAssignments[index - 1]];

    newAssignments.forEach((assignment, idx) => {
      assignment.order_number = idx + 1;
    });

    setTestData({ ...testData, assignments: newAssignments });
  };

  const moveAssignmentDown = (assignmentId: number) => {
    if (!testData) return;

    const index = testData.assignments.findIndex(a => a.id === assignmentId);
    if (index < 0 || index >= testData.assignments.length - 1) return;

    const newAssignments = [...testData.assignments];
    [newAssignments[index], newAssignments[index + 1]] = [newAssignments[index + 1], newAssignments[index]];

    newAssignments.forEach((assignment, idx) => {
      assignment.order_number = idx + 1;
    });

    setTestData({ ...testData, assignments: newAssignments });
  };

  const moveQuestionUp = (assignmentId: number, questionId: number) => {
    if (!testData) return;

    const updatedAssignments = testData.assignments.map(assignment => {
      if (assignment.id === assignmentId) {
        const index = assignment.questions.findIndex(q => q.id === questionId);
        if (index <= 0) return assignment;

        const newQuestions = [...assignment.questions];
        [newQuestions[index - 1], newQuestions[index]] = [newQuestions[index], newQuestions[index - 1]];

        newQuestions.forEach((question, idx) => {
          question.order_number = idx + 1;
        });

        return { ...assignment, questions: newQuestions };
      }
      return assignment;
    });

    setTestData({ ...testData, assignments: updatedAssignments });
  };

  const moveQuestionDown = (assignmentId: number, questionId: number) => {
    if (!testData) return;

    const updatedAssignments = testData.assignments.map(assignment => {
      if (assignment.id === assignmentId) {
        const index = assignment.questions.findIndex(q => q.id === questionId);
        if (index < 0 || index >= assignment.questions.length - 1) return assignment;

        const newQuestions = [...assignment.questions];
        [newQuestions[index], newQuestions[index + 1]] = [newQuestions[index + 1], newQuestions[index]];

        newQuestions.forEach((question, idx) => {
          question.order_number = idx + 1;
        });

        return { ...assignment, questions: newQuestions };
      }
      return assignment;
    });

    setTestData({ ...testData, assignments: updatedAssignments });
  };

  const addAssignment = () => {
    if (!testData) return;

    const newAssignment: Assignment = {
      id: Date.now(),
      title: 'Jauns uzdevums',
      description: 'Uzdevuma apraksts',
      max_points: 0,
      order_number: testData.assignments.length + 1,
      questions: []
    };

    setTestData({
      ...testData,
      assignments: [...testData.assignments, newAssignment]
    });
  };

  const addQuestion = (assignmentId: number) => {
    if (!testData) return;

    const updatedAssignments = testData.assignments.map(assignment => {
      if (assignment.id === assignmentId) {
        const newQuestion: Question = {
          id: Date.now(),
          question_text: 'Jautājuma teksts',
          question_type: 'multiple_choice',
          correct_answer: '',
          points: 1,
          order_number: assignment.questions.length + 1,
          options: [
            { id: Date.now() + 1, option_text: 'Variants A', is_correct: false, order_number: 1 },
            { id: Date.now() + 2, option_text: 'Variants B', is_correct: false, order_number: 2 },
            { id: Date.now() + 3, option_text: 'Variants C', is_correct: false, order_number: 3 },
            { id: Date.now() + 4, option_text: 'Variants D', is_correct: false, order_number: 4 }
          ]
        };

        return {
          ...assignment,
          questions: [...assignment.questions, newQuestion]
        };
      }
      return assignment;
    });

    setTestData({ ...testData, assignments: updatedAssignments });
  };

  const updateStudyMaterial = (field: string, value: unknown) => {
    if (!studyMaterialData) return;
    setStudyMaterialData({ ...studyMaterialData, [field]: value });
  };

  const updateTerm = (index: number, field: 'name' | 'definition', value: string) => {
    if (!studyMaterialData) return;
    const newTerms = [...studyMaterialData.terms];
    newTerms[index] = { ...newTerms[index], [field]: value };
    setStudyMaterialData({ ...studyMaterialData, terms: newTerms });
  };

  const addTerm = () => {
    if (!studyMaterialData) return;
    const newTerm = { name: 'New Term', definition: 'Definition of the new term' };
    setStudyMaterialData({
      ...studyMaterialData,
      terms: [...studyMaterialData.terms, newTerm]
    });
  };

  const deleteTerm = (index: number) => {
    if (!studyMaterialData) return;
    if (!window.confirm('Vai tiešām vēlaties dzēst šo terminu?')) return;

    const newTerms = studyMaterialData.terms.filter((_, i) => i !== index);
    setStudyMaterialData({ ...studyMaterialData, terms: newTerms });
  };

  const handleExportPDF = (includeAnswers: boolean = true) => {
    const type = materialType;
    const includeAnswersParam = type === 'test' ? `&include_answers=${includeAnswers}` : '';
    const url = `http://localhost:5000/api/export/pdf/${materialId}?type=${type}${includeAnswersParam}`;

    window.open(url, '_blank');
  };

  const handleExportDOCX = (includeAnswers: boolean = true) => {
    const type = materialType;
    const includeAnswersParam = type === 'test' ? `&include_answers=${includeAnswers}` : '';
    const url = `http://localhost:5000/api/export/docx/${materialId}?type=${type}${includeAnswersParam}`;

    window.open(url, '_blank');
  };

  const handleRequestMoreQuestions = async () => {
    if (!selectedAssignmentId || !testData) return;

    // Find the assignment
    const assignment = testData.assignments.find(a => a.id === selectedAssignmentId);
    if (!assignment) return;

    try {
      setGeneratingQuestions(true);

      // Check if assignment is new (has temporary ID from Date.now())
      // If so, save the test first to get real database IDs
      let actualAssignmentId = selectedAssignmentId;
      let currentTestData = testData;

      if (selectedAssignmentId > 100000) {
        // Save the test first
        const data = { type: 'test', ...testData };
        await api.put(`/api/materials/${materialId}`, data);

        // Reload to get real IDs
        const reloadResponse = await api.get(`/api/materials/${materialId}?type=${materialType}`);
        currentTestData = reloadResponse.data;

        // Find the assignment by title (since ID changed)
        const savedAssignment = currentTestData.assignments.find(
          (a: Assignment) => a.title === assignment.title && a.description === assignment.description
        );

        if (!savedAssignment) {
          alert('Neizdevās atrast saglabāto uzdevumu');
          setGeneratingQuestions(false);
          setShowAIDialog(false);
          setSelectedAssignmentId(null);
          return;
        }

        actualAssignmentId = savedAssignment.id;
      }

      // Prepare request with the actual (possibly updated) assignment ID
      const response = await api.post(`/api/materials/${materialId}/generate-questions`, {
        assignment_id: actualAssignmentId,
        assignment_title: assignment.title,
        assignment_description: assignment.description,
        num_questions: aiNumQuestions,
        difficulty: aiDifficulty
      });

      // Add jauni jautājumi to the assignment
      const newQuestions = response.data.questions;
      const updatedAssignments = currentTestData.assignments.map(a => {
        if (a.id === actualAssignmentId) {
          // Calculate new max_points including the jauni jautājumi
          const allQuestions = [...a.questions, ...newQuestions];
          const newMaxPoints = allQuestions.reduce((sum, q) => sum + (q.points || 0), 0);

          return {
            ...a,
            questions: allQuestions,
            max_points: newMaxPoints
          };
        }
        return a;
      });

      setTestData({
        ...currentTestData,
        assignments: updatedAssignments
      });

      setShowAIDialog(false);
      setSelectedAssignmentId(null);
      alert(`Veiksmīgi pievienoti ${newQuestions.length} jauni jautājumi!`);
    } catch (err) {
      const error = err as { response?: { data?: { error?: string } } };
      alert(error.response?.data?.error || 'Failed to generate questions. Please try again.');
    } finally {
      setGeneratingQuestions(false);
    }
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center', color: '#666' }}>Ielādē materiālu...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ color: '#c33', marginBottom: '20px' }}>{error}</div>
          <button onClick={() => navigate('/dashboard')} style={{ padding: '10px 20px' }}>
            Atpakaļ uz sākumlapu
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f5f5f5', paddingBottom: '40px' }}>
      <header style={{
        backgroundColor: 'white',
        borderBottom: '1px solid #ddd',
        padding: '20px',
        marginBottom: '30px',
        position: 'sticky',
        top: 0,
        zIndex: 100
      }}>
        <div style={{
          padding: '0 40px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '10px'
        }}>
          <div style={{ flex: 1 }}>
            <h1 style={{ margin: 0, fontSize: '24px' }}>
              {materialType === 'test' ? testData?.title : studyMaterialData?.title}
            </h1>
            <p style={{ margin: '5px 0 0', color: '#666', fontSize: '14px' }}>
              Izveidots: {formatDate(materialType === 'test' ? testData?.created_at || '' : studyMaterialData?.created_at || '')}
            </p>
          </div>
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            <button
              onClick={handleDelete}
              style={{
                padding: '10px 20px',
                backgroundColor: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Dzēst
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              style={{
                padding: '10px 20px',
                backgroundColor: '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Atpakaļ
            </button>

            {materialType === 'test' ? (
              <>
                <button
                  onClick={() => handleExportPDF(true)}
                  disabled={editMode}
                  title={editMode ? 'Saglabājiet izmaiņas pirms eksportēšanas' : ''}
                  style={{
                    padding: '8px 12px',
                    backgroundColor: editMode ? '#999' : '#17a2b8',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: editMode ? 'not-allowed' : 'pointer',
                    fontSize: '13px',
                    opacity: editMode ? 0.6 : 1
                  }}
                >
                  PDF (Atbildes)
                </button>
                <button
                  onClick={() => handleExportPDF(false)}
                  disabled={editMode}
                  title={editMode ? 'Saglabājiet izmaiņas pirms eksportēšanas' : ''}
                  style={{
                    padding: '8px 12px',
                    backgroundColor: editMode ? '#999' : '#6610f2',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: editMode ? 'not-allowed' : 'pointer',
                    fontSize: '13px',
                    opacity: editMode ? 0.6 : 1
                  }}
                >
                  PDF (Skolēniem)
                </button>
                <button
                  onClick={() => handleExportDOCX(false)}
                  disabled={editMode}
                  title={editMode ? 'Saglabājiet izmaiņas pirms eksportēšanas' : ''}
                  style={{
                    padding: '8px 12px',
                    backgroundColor: editMode ? '#999' : '#fd7e14',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: editMode ? 'not-allowed' : 'pointer',
                    fontSize: '13px',
                    opacity: editMode ? 0.6 : 1
                  }}
                >
                  DOCX (Skolēniem)
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => handleExportPDF()}
                  disabled={editMode}
                  title={editMode ? 'Saglabājiet izmaiņas pirms eksportēšanas' : ''}
                  style={{
                    padding: '8px 12px',
                    backgroundColor: editMode ? '#999' : '#17a2b8',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: editMode ? 'not-allowed' : 'pointer',
                    fontSize: '13px',
                    opacity: editMode ? 0.6 : 1
                  }}
                >
                  Eksportēt PDF
                </button>
                <button
                  onClick={() => handleExportDOCX()}
                  disabled={editMode}
                  title={editMode ? 'Saglabājiet izmaiņas pirms eksportēšanas' : ''}
                  style={{
                    padding: '8px 12px',
                    backgroundColor: editMode ? '#999' : '#20c997',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: editMode ? 'not-allowed' : 'pointer',
                    fontSize: '13px',
                    opacity: editMode ? 0.6 : 1
                  }}
                >
                  Eksportēt DOCX
                </button>
              </>
            )}

            <button
              onClick={handleSave}
              disabled={saving}
              style={{
                padding: '10px 20px',
                backgroundColor: editMode ? '#28a745' : '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: saving ? 'not-allowed' : 'pointer',
                fontWeight: 'bold'
              }}
            >
              {saving ? 'Saglabā...' : editMode ? 'Saglabāt izmaiņas' : 'Rediģēt'}
            </button>
          </div>
        </div>
      </header>

      <div style={{ padding: '0 40px' }}>
        {materialType === 'test' && testData && (
          <div>
            {testData.assignments.map((assignment, assignmentIndex) => (
              <div
                key={assignment.id}
                style={{
                  backgroundColor: 'white',
                  borderRadius: '8px',
                  padding: '25px',
                  marginBottom: '25px',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }}
              >
                <div style={{ marginBottom: '20px', paddingBottom: '15px', borderBottom: '2px solid #333' }}>
                  {editMode ? (
                    <input
                      type="text"
                      value={assignment.title}
                      onChange={(e) => updateAssignment(assignment.id, 'title', e.target.value)}
                      style={{
                        width: '100%',
                        fontSize: '20px',
                        fontWeight: 'bold',
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '4px',
                        marginBottom: '10px'
                      }}
                    />
                  ) : (
                    <h2 style={{ margin: '0 0 10px', fontSize: '20px', color: '#000' }}>
                      {assignment.title}
                    </h2>
                  )}

                  {editMode ? (
                    <textarea
                      value={assignment.description}
                      onChange={(e) => updateAssignment(assignment.id, 'description', e.target.value)}
                      rows={2}
                      style={{
                        width: '100%',
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '4px',
                        fontFamily: 'inherit'
                      }}
                    />
                  ) : (
                    <p style={{ margin: 0, color: '#666' }}>{assignment.description}</p>
                  )}

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px' }}>
                    <p style={{ margin: 0, color: '#666', fontSize: '14px' }}>
                      Maksimālie punkti: {assignment.max_points}
                    </p>
                    {editMode && (
                      <div style={{ display: 'flex', gap: '10px' }}>
                        <div style={{ display: 'flex', gap: '5px' }}>
                          <button
                            onClick={() => moveAssignmentUp(assignment.id)}
                            disabled={assignmentIndex === 0}
                            style={{
                              padding: '5px 10px',
                              backgroundColor: assignmentIndex === 0 ? '#ccc' : '#6c757d',
                              color: 'white',
                              border: 'none',
                              borderRadius: '4px',
                              cursor: assignmentIndex === 0 ? 'not-allowed' : 'pointer',
                              fontSize: '12px'
                            }}
                          >
                            ↑
                          </button>
                          <button
                            onClick={() => moveAssignmentDown(assignment.id)}
                            disabled={assignmentIndex === testData.assignments.length - 1}
                            style={{
                              padding: '5px 10px',
                              backgroundColor: assignmentIndex === testData.assignments.length - 1 ? '#ccc' : '#6c757d',
                              color: 'white',
                              border: 'none',
                              borderRadius: '4px',
                              cursor: assignmentIndex === testData.assignments.length - 1 ? 'not-allowed' : 'pointer',
                              fontSize: '12px'
                            }}
                          >
                            ↓
                          </button>
                        </div>
                        <button
                          onClick={() => deleteAssignment(assignment.id)}
                          style={{
                            padding: '5px 12px',
                            backgroundColor: '#dc3545',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontSize: '12px'
                          }}
                        >
                          Dzēst uzdevumu
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                {assignment.questions.map((question, questionIndex) => (
                  <div
                    key={question.id}
                    style={{
                      padding: '20px',
                      marginBottom: '15px',
                      backgroundColor: '#f8f9fa',
                      borderRadius: '6px',
                      borderLeft: '4px solid #333'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '12px' }}>
                      <div style={{ flex: 1 }}>
                        <span style={{ fontWeight: 'bold', color: '#000' }}>
                          Jautājums {questionIndex + 1}
                        </span>
                        {editMode ? (
                          <select
                            value={question.question_type}
                            onChange={(e) => updateQuestion(assignment.id, question.id, 'question_type', e.target.value)}
                            style={{
                              marginLeft: '10px',
                              padding: '4px 8px',
                              border: '1px solid #ddd',
                              borderRadius: '4px',
                              fontSize: '13px'
                            }}
                          >
                            <option value="multiple_choice">Multiple Choice</option>
                            <option value="short_answer">Short Answer</option>
                            <option value="long_answer">Long Answer</option>
                            <option value="true_false">True/False</option>
                            <option value="matching">Matching</option>
                            <option value="fill_in_blank">Fill in Blank</option>
                          </select>
                        ) : (
                          <span style={{ marginLeft: '10px', fontSize: '14px', color: '#666' }}>
                            ({question.question_type.replace('_', ' ')})
                          </span>
                        )}
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                          <span style={{ fontSize: '14px', color: '#666' }}>Punkti:</span>
                          {editMode ? (
                            <input
                              type="number"
                              value={question.points}
                              onChange={(e) => updateQuestion(assignment.id, question.id, 'points', parseInt(e.target.value) || 0)}
                              min="0"
                              style={{
                                width: '60px',
                                padding: '4px 8px',
                                border: '1px solid #ddd',
                                borderRadius: '4px'
                              }}
                            />
                          ) : (
                            <span style={{ fontWeight: 'bold' }}>{question.points}</span>
                          )}
                        </div>
                        {editMode && (
                          <div style={{ display: 'flex', gap: '5px' }}>
                            <button
                              onClick={() => moveQuestionUp(assignment.id, question.id)}
                              disabled={questionIndex === 0}
                              style={{
                                padding: '4px 8px',
                                backgroundColor: questionIndex === 0 ? '#ccc' : '#6c757d',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: questionIndex === 0 ? 'not-allowed' : 'pointer',
                                fontSize: '11px'
                              }}
                            >
                              ↑
                            </button>
                            <button
                              onClick={() => moveQuestionDown(assignment.id, question.id)}
                              disabled={questionIndex === assignment.questions.length - 1}
                              style={{
                                padding: '4px 8px',
                                backgroundColor: questionIndex === assignment.questions.length - 1 ? '#ccc' : '#6c757d',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: questionIndex === assignment.questions.length - 1 ? 'not-allowed' : 'pointer',
                                fontSize: '11px'
                              }}
                            >
                              ↓
                            </button>
                            <button
                              onClick={() => deleteQuestion(assignment.id, question.id)}
                              style={{
                                padding: '4px 10px',
                                backgroundColor: '#dc3545',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                fontSize: '11px'
                              }}
                            >
                              Dzēst
                            </button>
                          </div>
                        )}
                      </div>
                    </div>

                    {editMode ? (
                      <textarea
                        value={question.question_text}
                        onChange={(e) => updateQuestion(assignment.id, question.id, 'question_text', e.target.value)}
                        rows={3}
                        style={{
                          width: '100%',
                          padding: '10px',
                          border: '1px solid #ddd',
                          borderRadius: '4px',
                          fontFamily: 'inherit',
                          marginBottom: '12px'
                        }}
                      />
                    ) : (
                      <p style={{ margin: '0 0 12px', fontSize: '15px', lineHeight: '1.5' }}>
                        {question.question_text}
                      </p>
                    )}


                    {question.options && question.options.length > 0 && ['multiple_choice', 'true_false'].includes(question.question_type) && (
                      <div style={{ marginBottom: '12px' }}>
                        <div style={{ fontWeight: 'bold', marginBottom: '8px', fontSize: '14px' }}>Varianti:</div>
                        {question.options.map((option, optionIndex) => (
                          <div
                            key={option.id}
                            style={{
                              padding: '8px 12px',
                              marginBottom: '6px',
                              backgroundColor: option.is_correct ? '#d4edda' : 'white',
                              border: '1px solid #ddd',
                              borderRadius: '4px',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '8px'
                            }}
                          >
                            <span style={{ fontWeight: 'bold', minWidth: '20px' }}>
                              {String.fromCharCode(65 + optionIndex)}.
                            </span>
                            {editMode ? (
                              <input
                                type="text"
                                value={option.option_text}
                                onChange={(e) => updateOption(assignment.id, question.id, option.id, 'option_text', e.target.value)}
                                style={{
                                  flex: 1,
                                  padding: '6px 10px',
                                  border: '1px solid #ddd',
                                  borderRadius: '4px',
                                  fontSize: '14px'
                                }}
                              />
                            ) : (
                              <span style={{ flex: 1 }}>{option.option_text}</span>
                            )}
                            {option.is_correct && (
                              <span style={{ color: '#28a745', fontWeight: 'bold', fontSize: '14px' }}>✓ Pareizi</span>
                            )}
                          </div>
                        ))}
                      </div>
                    )}


                    {question.question_type === 'matching' && question.options && question.options.length > 0 && (
                      <div style={{ marginBottom: '12px' }}>
                        <div style={{ fontWeight: 'bold', marginBottom: '8px', fontSize: '14px' }}>Saskaņo pārus:</div>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>

                          <div style={{ fontWeight: 'bold', padding: '8px', backgroundColor: '#f0f0f0', borderRadius: '4px' }}>
                            Kreisā puse
                          </div>

                          <div style={{ fontWeight: 'bold', padding: '8px', backgroundColor: '#f0f0f0', borderRadius: '4px' }}>
                            Labā puse
                          </div>


                          {question.options.map((option) => {
                            const parts = option.option_text.split('|');
                            const leftPart = parts[0] || '';
                            const rightPart = parts[1] || '';

                            return (
                              <React.Fragment key={option.id}>

                                <div style={{ padding: '8px 12px', backgroundColor: '#e3f2fd', border: '1px solid #90caf9', borderRadius: '4px' }}>
                                  {editMode ? (
                                    <input
                                      type="text"
                                      value={leftPart}
                                      onChange={(e) => {
                                        const newText = `${e.target.value}|${rightPart}`;
                                        updateOption(assignment.id, question.id, option.id, 'option_text', newText);
                                      }}
                                      style={{
                                        width: '100%',
                                        padding: '4px 8px',
                                        border: '1px solid #90caf9',
                                        borderRadius: '4px',
                                        fontSize: '14px'
                                      }}
                                      placeholder="Kreisā vienība"
                                    />
                                  ) : (
                                    <span>{leftPart}</span>
                                  )}
                                </div>


                                <div style={{ padding: '8px 12px', backgroundColor: '#fff3e0', border: '1px solid #ffb74d', borderRadius: '4px' }}>
                                  {editMode ? (
                                    <input
                                      type="text"
                                      value={rightPart}
                                      onChange={(e) => {
                                        const newText = `${leftPart}|${e.target.value}`;
                                        updateOption(assignment.id, question.id, option.id, 'option_text', newText);
                                      }}
                                      style={{
                                        width: '100%',
                                        padding: '4px 8px',
                                        border: '1px solid #ffb74d',
                                        borderRadius: '4px',
                                        fontSize: '14px'
                                      }}
                                      placeholder="Labā vienība"
                                    />
                                  ) : (
                                    <span>{rightPart}</span>
                                  )}
                                </div>
                              </React.Fragment>
                            );
                          })}
                        </div>
                      </div>
                    )}


                    {question.question_type !== 'matching' && (
                      <div style={{
                        padding: '10px',
                        backgroundColor: '#d4edda',
                        border: '1px solid #c3e6cb',
                        borderRadius: '4px'
                      }}>
                        <span style={{ fontWeight: 'bold', color: '#155724' }}>Pareizā atbilde: </span>
                        {editMode ? (
                          <input
                            type="text"
                            value={question.correct_answer}
                            onChange={(e) => updateQuestion(assignment.id, question.id, 'correct_answer', e.target.value)}
                            style={{
                              width: '300px',
                              padding: '4px 8px',
                              border: '1px solid #c3e6cb',
                              borderRadius: '4px',
                              marginLeft: '8px'
                            }}
                          />
                        ) : (
                          <span style={{ color: '#155724' }}>{question.correct_answer}</span>
                        )}
                      </div>
                    )}
                  </div>
                ))}


                {editMode && (
                  <div style={{ marginTop: '20px', paddingTop: '15px', borderTop: '1px solid #ddd' }}>
                    <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                      <button
                        onClick={() => addQuestion(assignment.id)}
                        style={{
                          padding: '12px 20px',
                          backgroundColor: '#28a745',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '14px',
                          fontWeight: 'bold'
                        }}
                      >
                        + Pievienot jautājumu manuāli
                      </button>
                      <button
                        onClick={() => {
                          setSelectedAssignmentId(assignment.id);
                          setShowAIDialog(true);
                        }}
                        style={{
                          padding: '12px 20px',
                          backgroundColor: '#17a2b8',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '14px',
                          fontWeight: 'bold'
                        }}
                      >
                        Ģenerēt ar MI
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}


            {editMode && (
              <div style={{
                backgroundColor: 'white',
                borderRadius: '8px',
                padding: '25px',
                marginTop: '25px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                textAlign: 'center'
              }}>
                <button
                  onClick={addAssignment}
                  style={{
                    padding: '12px 24px',
                    backgroundColor: '#28a745',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '16px',
                    fontWeight: 'bold'
                  }}
                >
                  + Pievienot uzdevumu
                </button>
              </div>
            )}
          </div>
        )}


        {materialType === 'study_material' && studyMaterialData && (
          <div style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '30px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>

            <div style={{ marginBottom: '30px' }}>
              <h2 style={{ margin: '0 0 15px', fontSize: '20px', color: '#000' }}>Kopsavilkums</h2>
              {editMode ? (
                <textarea
                  value={studyMaterialData.summary}
                  onChange={(e) => updateStudyMaterial('summary', e.target.value)}
                  style={{
                    width: '100%',
                    minHeight: '200px',
                    padding: '12px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    fontSize: '14px',
                    lineHeight: '1.6',
                    fontFamily: 'inherit',
                    resize: 'vertical'
                  }}
                  placeholder="Ievadiet kopsavilkumu..."
                />
              ) : (
                <div
                  style={{
                    margin: 0,
                    fontSize: '15px',
                    lineHeight: '1.6',
                    color: '#333',
                    whiteSpace: 'pre-wrap'
                  }}
                >
                  {studyMaterialData.summary}
                </div>
              )}
            </div>


            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                <h2 style={{ margin: 0, fontSize: '20px', color: '#000' }}>Galvenie termini</h2>
                {editMode && (
                  <button
                    onClick={addTerm}
                    style={{
                      padding: '8px 15px',
                      backgroundColor: '#28a745',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '14px',
                      fontWeight: 'bold'
                    }}
                  >
                    + Pievienot terminu
                  </button>
                )}
              </div>
              {studyMaterialData.terms.map((term, index) => (
                <div
                  key={index}
                  style={{
                    padding: '15px',
                    marginBottom: '15px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '6px',
                    borderLeft: '4px solid #333',
                    position: 'relative'
                  }}
                >
                  {editMode ? (
                    <>
                      <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
                        <input
                          type="text"
                          value={term.name}
                          onChange={(e) => updateTerm(index, 'name', e.target.value)}
                          style={{
                            flex: 1,
                            padding: '8px',
                            border: '1px solid #ddd',
                            borderRadius: '4px',
                            fontWeight: 'bold'
                          }}
                        />
                        <button
                          onClick={() => deleteTerm(index)}
                          style={{
                            padding: '8px 15px',
                            backgroundColor: '#dc3545',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontSize: '14px'
                          }}
                        >
                          Dzēst
                        </button>
                      </div>
                      <textarea
                        value={term.definition}
                        onChange={(e) => updateTerm(index, 'definition', e.target.value)}
                        rows={2}
                        style={{
                          width: '100%',
                          padding: '8px',
                          border: '1px solid #ddd',
                          borderRadius: '4px',
                          fontFamily: 'inherit'
                        }}
                      />
                    </>
                  ) : (
                    <>
                      <div style={{ fontWeight: 'bold', marginBottom: '8px', color: '#000' }}>
                        {term.name}
                      </div>
                      <div style={{ color: '#555', lineHeight: '1.5' }}>
                        {term.definition}
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* AI Jautājums Generation Dialog */}
        {showAIDialog && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}>
            <div style={{
              backgroundColor: 'white',
              borderRadius: '8px',
              padding: '30px',
              maxWidth: '500px',
              width: '90%',
              boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
            }}>
              <h2 style={{ margin: '0 0 20px', fontSize: '20px' }}>Pieprasīt vairāk jautājumus no MI</h2>

              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
                  Jautājumu skaits
                </label>
                <input
                  type="number"
                  value={aiNumQuestions}
                  onChange={(e) => setAiNumQuestions(Math.max(1, Math.min(20, parseInt(e.target.value) || 1)))}
                  min="1"
                  max="20"
                  style={{
                    width: '100%',
                    padding: '10px',
                    fontSize: '15px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    boxSizing: 'border-box'
                  }}
                />
                <p style={{ margin: '5px 0 0', fontSize: '13px', color: '#666' }}>
                  No 1 līdz 20 jautājumiem
                </p>
              </div>

              <div style={{ marginBottom: '25px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
                  Grūtības līmenis
                </label>
                <select
                  value={aiDifficulty}
                  onChange={(e) => setAiDifficulty(e.target.value as 'easy' | 'medium' | 'hard')}
                  style={{
                    width: '100%',
                    padding: '10px',
                    fontSize: '15px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    boxSizing: 'border-box'
                  }}
                >
                  <option value="easy">Viegls</option>
                  <option value="medium">Vidējs</option>
                  <option value="hard">Grūts</option>
                </select>
              </div>

              <div style={{ display: 'flex', gap: '10px' }}>
                <button
                  onClick={() => {
                    setShowAIDialog(false);
                    setSelectedAssignmentId(null);
                  }}
                  disabled={generatingQuestions}
                  style={{
                    padding: '12px 20px',
                    backgroundColor: '#6c757d',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: generatingQuestions ? 'not-allowed' : 'pointer',
                    fontSize: '15px'
                  }}
                >
                  Atcelt
                </button>
                <button
                  onClick={handleRequestMoreQuestions}
                  disabled={generatingQuestions}
                  style={{
                    flex: 1,
                    padding: '12px',
                    backgroundColor: generatingQuestions ? '#ccc' : '#17a2b8',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: generatingQuestions ? 'not-allowed' : 'pointer',
                    fontSize: '15px',
                    fontWeight: 'bold'
                  }}
                >
                  {generatingQuestions ? (
                    <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                      <span style={{
                        display: 'inline-block',
                        width: '14px',
                        height: '14px',
                        border: '2px solid #ffffff',
                        borderTop: '2px solid transparent',
                        borderRadius: '50%',
                        animation: 'spin 1s linear infinite'
                      }}></span>
                      Ģenerē...
                    </span>
                  ) : 'Ģenerēt jautājumus'}
                </button>
              </div>

              {/* CSS Animation for spinner */}
              <style>{`
                @keyframes spin {
                  0% { transform: rotate(0deg); }
                  100% { transform: rotate(360deg); }
                }
              `}</style>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MaterialView;
