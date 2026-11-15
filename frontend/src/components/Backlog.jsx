import { useState, useEffect } from 'react';
import { getTasks, createTask } from '../api';

export default function Backlog() {
  const [tasks, setTasks] = useState([]);
  const [title, setTitle] = useState('');
  const [hours, setHours] = useState(10);
  const [priority, setPriority] = useState('high');

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    const data = await getTasks();
    setTasks(data);
  };

  const handleAdd = async () => {
    if (!title) return;
    await createTask({ title, estimated_hours: hours, priority });
    setTitle('');
    setHours(10);
    setPriority('high');
    loadTasks();
  };

  return (
    <div className="card">
      <h2>Бэклог задач</h2>
      
      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
        <div className="form-group" style={{ flex: 2 }}>
          <label>Название задачи</label>
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Написать API" />
        </div>
        <div className="form-group" style={{ width: '120px' }}>
          <label>Часов</label>
          <input type="number" value={hours} onChange={(e) => setHours(e.target.value)} min="1" />
        </div>
        <div className="form-group" style={{ width: '150px' }}>
          <label>Приоритет</label>
          <select value={priority} onChange={(e) => setPriority(e.target.value)}>
            <option value="high">Высокий</option>
            <option value="medium">Средний</option>
            <option value="low">Низкий</option>
          </select>
        </div>
        <button className="btn" onClick={handleAdd} style={{ marginTop: '24px' }}>
          Добавить
        </button>
      </div>

      <table className="table">
        <thead>
          <tr>
            <th>Название</th>
            <th>Часов</th>
            <th>Приоритет</th>
          </tr>
        </thead>
        <tbody>
          {tasks.map((t) => (
            <tr key={t.id}>
              <td>{t.title}</td>
              <td>{t.estimated_hours}</td>
              <td>{t.priority === 'high' ? '🔴 Высокий' : t.priority === 'medium' ? '🟡 Средний' : '🟢 Низкий'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}