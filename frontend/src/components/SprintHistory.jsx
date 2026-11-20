import { useState, useEffect } from 'react';
import { getSprints } from '../api';

const API_BASE = 'http://localhost:8000';

export default function SprintHistory() {
  const [sprints, setSprints] = useState([]);

  useEffect(() => {
    loadSprints();
  }, []);

  const loadSprints = async () => {
    const data = await getSprints();
    setSprints(data);
  };

  const handleExport = (sprintId) => {
    window.open(`${API_BASE}/sprints/${sprintId}/export`, '_blank');
  };

  return (
    <div className="card">
      <h2>История спринтов</h2>
      
      {sprints.length === 0 ? (
        <p style={{ color: '#7a7268' }}>Пока не было рассчитано ни одного спринта.</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Название</th>
              <th>Период</th>
              <th>Емкость (ч)</th>
              <th>Запланировано (ч)</th>
              <th>Загрузка</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {sprints.map((s) => {
              const loadPercent = s.total_capacity_hours > 0 
                ? Math.round((s.planned_hours / s.total_capacity_hours) * 100) 
                : 0;
              
              return (
                <tr key={s.id}>
                  <td>{s.name}</td>
                  <td>{s.start_date} — {s.end_date}</td>
                  <td>{s.total_capacity_hours.toFixed(1)}</td>
                  <td>{s.planned_hours.toFixed(1)}</td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{ flex: 1, height: '8px', backgroundColor: '#e0d8cc', borderRadius: '4px', overflow: 'hidden' }}>
                        <div 
                          style={{ 
                            width: `${Math.min(loadPercent, 100)}%`, 
                            height: '100%', 
                            backgroundColor: loadPercent > 90 ? '#c0392b' : '#27ae60' 
                          }} 
                        />
                      </div>
                      <span style={{ fontSize: '12px', minWidth: '40px' }}>{loadPercent}%</span>
                    </div>
                  </td>
                  <td>
                    <button 
                      onClick={() => handleExport(s.id)}
                      style={{ color: '#c4956a', background: 'none', border: '1px solid #c4956a', borderRadius: '4px', padding: '4px 8px', cursor: 'pointer' }}
                    >
                      Скачать CSV
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}