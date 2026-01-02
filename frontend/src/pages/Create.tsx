/**
 * Create Material Page
 * Form to generate tests or study materials
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';

const Create: React.FC = () => {
  const navigate = useNavigate();

  const [materialType, setMaterialType] = useState<'test' | 'study_material'>('test');
  const [title, setTitle] = useState('');
  const [inputMethod, setInputMethod] = useState<'text' | 'file'>('text');
  const [content, setContent] = useState('');
  const [file, setFile] = useState<File | null>(null);

  // Test-specific options
  const [numQuestions, setNumQuestions] = useState(10);
  const [difficulty, setDifficulty] = useState<'easy' | 'medium' | 'hard'>('medium');

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      // Validate file type
      const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
      if (!validTypes.includes(selectedFile.type) && !selectedFile.name.match(/\.(pdf|docx|txt)$/i)) {
        setError('Lūdzu augšupielādējiet PDF, DOCX vai TXT failu');
        return;
      }
      setFile(selectedFile);
      setError('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!title.trim()) {
      setError('Lūdzu ievadiet nosaukumu');
      return;
    }

    if (inputMethod === 'text' && !content.trim()) {
      setError('Lūdzu ievadiet saturu');
      return;
    }

    if (inputMethod === 'file' && !file) {
      setError('Lūdzu izvēlieties failu');
      return;
    }

    try {
      setLoading(true);

      // Create FormData for file upload
      const formData = new FormData();
      formData.append('material_type', materialType);
      formData.append('title', title.trim());

      if (inputMethod === 'text') {
        formData.append('content', content.trim());
      } else {
        formData.append('file', file!);
      }

      // Add test-specific options
      if (materialType === 'test') {
        formData.append('num_questions', numQuestions.toString());
        formData.append('difficulty', difficulty);
      }

      const response = await api.post('/api/generate', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const materialId = response.data.id;
      navigate(`/materials/${materialId}?type=${materialType}`);
    } catch (err) {
      const error = err as { response?: { data?: { error?: string } } };
      setError(error.response?.data?.error || 'Neizdevās ģenerēt materiālu. Lūdzu mēģiniet vēlreiz.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      {/* Header */}
      <header style={{
        backgroundColor: 'white',
        borderBottom: '1px solid #ddd',
        padding: '20px',
        marginBottom: '30px'
      }}>
        <div style={{
          padding: '0 40px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <h1 style={{ margin: 0, fontSize: '24px' }}>Izveidot jaunu materiālu</h1>
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
            Atpakaļ uz sākumlapu
          </button>
        </div>
      </header>

      {/* Form */}
      <div style={{ padding: '0 40px' }}>
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          padding: '30px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          {/* Error Message */}
          {error && (
            <div style={{
              backgroundColor: '#fee',
              color: '#c33',
              padding: '15px',
              borderRadius: '4px',
              marginBottom: '20px'
            }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {/* Material Type */}
            <div style={{ marginBottom: '25px' }}>
              <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold', fontSize: '16px' }}>
                Materiāla tips
              </label>
              <div style={{ display: 'flex', gap: '15px' }}>
                <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                  <input
                    type="radio"
                    value="test"
                    checked={materialType === 'test'}
                    onChange={(e) => setMaterialType(e.target.value as 'test')}
                    disabled={loading}
                    style={{ marginRight: '8px', cursor: 'pointer' }}
                  />
                  <span style={{ fontSize: '15px' }}>Tests (ar jautājumiem)</span>
                </label>
                <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                  <input
                    type="radio"
                    value="study_material"
                    checked={materialType === 'study_material'}
                    onChange={(e) => setMaterialType(e.target.value as 'study_material')}
                    disabled={loading}
                    style={{ marginRight: '8px', cursor: 'pointer' }}
                  />
                  <span style={{ fontSize: '15px' }}>Mācību materiāls (kopsavilkums un termini)</span>
                </label>
              </div>
            </div>

            {/* Title */}
            <div style={{ marginBottom: '25px' }}>
              <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold', fontSize: '16px' }}>
                Nosaukums
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                disabled={loading}
                placeholder="Piemēram, Otrā pasaules kara vēstures tests"
                style={{
                  width: '100%',
                  padding: '12px',
                  fontSize: '15px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  boxSizing: 'border-box'
                }}
              />
            </div>

            {/* Input Method */}
            <div style={{ marginBottom: '25px' }}>
              <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold', fontSize: '16px' }}>
                Satura avots
              </label>
              <div style={{ display: 'flex', gap: '15px', marginBottom: '15px' }}>
                <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                  <input
                    type="radio"
                    value="text"
                    checked={inputMethod === 'text'}
                    onChange={(e) => setInputMethod(e.target.value as 'text')}
                    disabled={loading}
                    style={{ marginRight: '8px', cursor: 'pointer' }}
                  />
                  <span style={{ fontSize: '15px' }}>Ievadīt tekstu</span>
                </label>
                <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                  <input
                    type="radio"
                    value="file"
                    checked={inputMethod === 'file'}
                    onChange={(e) => setInputMethod(e.target.value as 'file')}
                    disabled={loading}
                    style={{ marginRight: '8px', cursor: 'pointer' }}
                  />
                  <span style={{ fontSize: '15px' }}>Augšupielādēt failu (PDF, DOCX, TXT)</span>
                </label>
              </div>

              {/* Text Input */}
              {inputMethod === 'text' && (
                <textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  disabled={loading}
                  placeholder="Ielīmējiet vai ierakstiet saturu, no kura vēlaties ģenerēt materiālus..."
                  rows={10}
                  style={{
                    width: '100%',
                    padding: '12px',
                    fontSize: '15px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    boxSizing: 'border-box',
                    fontFamily: 'inherit',
                    resize: 'vertical'
                  }}
                />
              )}

              {/* File Upload */}
              {inputMethod === 'file' && (
                <div>
                  <input
                    type="file"
                    onChange={handleFileChange}
                    disabled={loading}
                    accept=".pdf,.docx,.txt"
                    style={{
                      width: '100%',
                      padding: '12px',
                      fontSize: '15px',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      boxSizing: 'border-box',
                      cursor: 'pointer'
                    }}
                  />
                  {file && (
                    <p style={{ marginTop: '10px', color: '#666', fontSize: '14px' }}>
                      Izvēlēts: {file.name} ({(file.size / 1024).toFixed(1)} KB)
                    </p>
                  )}
                </div>
              )}
            </div>

            {/* Test Options (only shown for tests) */}
            {materialType === 'test' && (
              <>
                {/* Number of Questions */}
                <div style={{ marginBottom: '25px' }}>
                  <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold', fontSize: '16px' }}>
                    Jautājumu skaits
                  </label>
                  <input
                    type="number"
                    value={numQuestions}
                    onChange={(e) => setNumQuestions(Math.max(1, Math.min(50, parseInt(e.target.value) || 1)))}
                    disabled={loading}
                    min="1"
                    max="50"
                    style={{
                      width: '150px',
                      padding: '12px',
                      fontSize: '15px',
                      border: '1px solid #ddd',
                      borderRadius: '4px'
                    }}
                  />
                  <p style={{ marginTop: '5px', color: '#666', fontSize: '14px' }}>
                    No 1 līdz 50 jautājumiem
                  </p>
                </div>

                {/* Difficulty */}
                <div style={{ marginBottom: '25px' }}>
                  <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold', fontSize: '16px' }}>
                    Grūtības līmenis
                  </label>
                  <select
                    value={difficulty}
                    onChange={(e) => setDifficulty(e.target.value as 'easy' | 'medium' | 'hard')}
                    disabled={loading}
                    style={{
                      width: '200px',
                      padding: '12px',
                      fontSize: '15px',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      cursor: 'pointer'
                    }}
                  >
                    <option value="easy">Viegls</option>
                    <option value="medium">Vidējs</option>
                    <option value="hard">Grūts</option>
                  </select>
                </div>
              </>
            )}

            {/* Submit Button */}
            <div style={{ marginTop: '30px', display: 'flex', gap: '15px' }}>
              <button
                type="button"
                onClick={() => navigate('/dashboard')}
                disabled={loading}
                style={{
                  padding: '15px 30px',
                  fontSize: '16px',
                  backgroundColor: '#6c757d',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: loading ? 'not-allowed' : 'pointer'
                }}
              >
                Atcelt
              </button>
              <button
                type="submit"
                disabled={loading}
                style={{
                  flex: 1,
                  padding: '15px',
                  fontSize: '16px',
                  backgroundColor: loading ? '#ccc' : '#28a745',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontWeight: 'bold'
                }}
              >
                {loading ? (
                  <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
                    <span style={{
                      display: 'inline-block',
                      width: '16px',
                      height: '16px',
                      border: '3px solid #ffffff',
                      borderTop: '3px solid transparent',
                      borderRadius: '50%',
                      animation: 'spin 1s linear infinite'
                    }}></span>
                    Ģenerē... (tas var aizņemt 10-30 sekundes)
                    <style>{`
                      @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                      }
                    `}</style>
                  </span>
                ) : 'Ģenerēt materiālu'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Create;
