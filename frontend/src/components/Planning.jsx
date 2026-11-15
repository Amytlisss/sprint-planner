import { useState } from 'react';
import { calculateSprint } from '../api';

export default function Planning() {
  const [startDate, setStartDate] = useState('2026-11-16');
  const [endDate, setEndDate] = useState('2026-11-29');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCalculate = async () => {
    setLoading(true);
    try {
      const data = await calculateSprint({
        name: 'Sprint 1',
        start_date: startDate,
        end_date: endDate,
        focus_factor: 0.8,
      });
      setResult(data);
    } catch (error) {
      console.error('Ошибка:', error);
      alert('Ошибка при расчёте. Проверьте, что добавлены сотрудники и задачи.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Планирование спринта</h2>
      
      <div style={{ display: 'flex', gap: '20px', marginBottom: '24px' }}>
        <div className="form-group" style={{ flex: 1 }}>
          <label>Дата начала</label>
          <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
        </div>
        <div className="form-group" style={{ flex: 1 }}>
          <label>Дата окончания</label>
          <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
        </div>
      </div>

      <button className="btn" onClick={handleCalculate} disabled={loading}>
        {loading ? 'Расчёт...' : 'Рассчитать спринт'}
      </button>

      {result && (
        <div className="result">
          <h3>Результат расчёта</h3>
          <p><strong>Ёмкость команды:</strong> {result.total_capacity_hours.toFixed(1)} часов</p>
          <p><strong>Запланировано:</strong> {result.planned_hours.toFixed(1)} часов</p>
          <p><strong>Выбранные задачи (ID):</strong> {result.selected_tasks.join(', ') || 'нет'}</p>
          <p><strong>Пропущенные задачи (ID):</strong> {result.skipped_tasks.join(', ') || 'нет'}</p>
        </div>
      )}
    </div>
  );
}