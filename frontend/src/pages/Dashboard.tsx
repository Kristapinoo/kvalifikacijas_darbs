/**
 * Dashboard Page
 * Displays user's materials (tests and study materials)
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../api/axios';

interface Material {
  id: number;
  title: string;
  type: 'test' | 'study_material';
  created_at: string;
}

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [materials, setMaterials] = useState<Material[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deletingId, setDeletingId] = useState<number | null>(null);

  useEffect(() => {
    fetchMaterials();
  }, []);

  const fetchMaterials = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await api.get('/api/materials');
      setMaterials(response.data.materials);
    } catch {
      setError('Neizdevās ielādēt materiālus');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number, type: 'test' | 'study_material') => {
    if (!window.confirm('Vai tiešām vēlaties dzēst šo materiālu?')) {
      return;
    }

    try {
      setDeletingId(id);
      await api.delete(`/api/materials/${id}?type=${type}`);
      setMaterials(materials.filter(m => m.id !== id));
    } catch {
      alert('Neizdevās dzēst materiālu');
    } finally {
      setDeletingId(null);
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

  const getMaterialTypeLabel = (type: string) => {
    return type === 'test' ? 'Tests' : 'Mācību materiāls';
  };

  const getMaterialTypeColor = (type: string) => {
    return type === 'test' ? '#6c757d' : '#495057';
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
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
          <div>
            <h1 style={{ margin: 0, fontSize: '24px' }}>Mani materiāli</h1>
            <p style={{ margin: '5px 0 0', color: '#666' }}>
              Sveiki, {user?.email}
            </p>
          </div>
          <button
            onClick={logout}
            style={{
              padding: '10px 20px',
              backgroundColor: '#dc3545',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 'bold'
            }}
          >
            Atteikties
          </button>
        </div>
      </header>

      <div style={{ padding: '0 40px' }}>
        <div style={{ marginBottom: '30px' }}>
          <button
            onClick={() => navigate('/create')}
            style={{
              padding: '12px 24px',
              backgroundColor: '#6c757d',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: 'bold'
            }}
          >
            + Izveidot jaunu materiālu
          </button>
        </div>

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

        {loading && (
          <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
            Ielādē materiālus...
          </div>
        )}

        {!loading && materials.length === 0 && (
          <div style={{
            backgroundColor: 'white',
            padding: '60px 40px',
            borderRadius: '8px',
            textAlign: 'center',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            <h2 style={{ color: '#666', marginBottom: '15px' }}>Nav materiālu</h2>
            <p style={{ color: '#999', marginBottom: '30px' }}>
              Izveidojiet savu pirmo testu vai mācību materiālu, lai sāktu
            </p>
            <button
              onClick={() => navigate('/create')}
              style={{
                padding: '12px 24px',
                backgroundColor: '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '16px',
                fontWeight: 'bold'
              }}
            >
              + Izveidot jaunu materiālu
            </button>
          </div>
        )}

        {!loading && materials.length > 0 && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: '20px',
            marginBottom: '40px'
          }}>
            {materials.map((material) => (
              <div
                key={`${material.type}-${material.id}`}
                style={{
                  backgroundColor: 'white',
                  borderRadius: '8px',
                  padding: '20px',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                  position: 'relative',
                  cursor: 'pointer',
                  transition: 'transform 0.2s, box-shadow 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = '0 4px 8px rgba(0,0,0,0.15)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
                }}
                onClick={() => navigate(`/materials/${material.id}?type=${material.type}`)}
              >
                {/* Type Badge */}
                <div style={{
                  display: 'inline-block',
                  padding: '4px 12px',
                  backgroundColor: getMaterialTypeColor(material.type),
                  color: 'white',
                  borderRadius: '12px',
                  fontSize: '12px',
                  fontWeight: 'bold',
                  marginBottom: '12px'
                }}>
                  {getMaterialTypeLabel(material.type)}
                </div>

                {/* Title */}
                <h3 style={{
                  margin: '0 0 10px',
                  fontSize: '18px',
                  color: '#333',
                  wordBreak: 'break-word'
                }}>
                  {material.title}
                </h3>

                {/* Date */}
                <p style={{
                  margin: '0 0 15px',
                  fontSize: '14px',
                  color: '#999'
                }}>
                  Izveidots: {formatDate(material.created_at)}
                </p>

                {/* Actions */}
                <div style={{
                  display: 'flex',
                  gap: '10px',
                  marginTop: '15px',
                  paddingTop: '15px',
                  borderTop: '1px solid #eee'
                }}>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(material.id, material.type);
                    }}
                    disabled={deletingId === material.id}
                    style={{
                      flex: 1,
                      padding: '8px 16px',
                      backgroundColor: deletingId === material.id ? '#ccc' : '#dc3545',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: deletingId === material.id ? 'not-allowed' : 'pointer',
                      fontSize: '14px'
                    }}
                  >
                    {deletingId === material.id ? 'Dzēš...' : 'Dzēst'}
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/materials/${material.id}?type=${material.type}`);
                    }}
                    style={{
                      flex: 1,
                      padding: '8px 16px',
                      backgroundColor: '#6c757d',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '14px'
                    }}
                  >
                    Skatīt
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
