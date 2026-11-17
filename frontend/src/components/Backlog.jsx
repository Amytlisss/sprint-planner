import { useState, useEffect } from 'react';
import { getTasks, createTask, updateTask, deleteTask, reactivateTask } from '../api';

export default function Backlog() {
  const [tasks, setTasks] = useState([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [hours, setHours] = useState(10);
  const [priority, setPriority] = useState('high');
  const [editingId, setEditingId] = useState(null);
  const [showInactive, setShowInactive] = useState(false);

  useEffect(() => {
    loadTasks();
  }, [showInactive]);

  const loadTasks = async () => {
    const data = await getTasks(showInactive);
    setTasks(data);
  };

  const handleAdd = async () => {
    if (!title) return;
    await createTask({ title, description, estimated_hours: hours, priority });
    setTitle('');
    setDescription('');
    setHours(10);
    setPriority('high');
    loadTasks();
  };

  const handleEdit = (task) => {
    setEditingId(task.id);
    setTitle(task.title);
    setDescription(task.description || '');
    setHours(task.estimated_hours);
    setPriority(task.priority);
  };

  const handleUpdate = async () => {
    if (!title) return;
    await updateTask(editingId, { title, description, estimated_hours: hours, priority });
    setEditingId(null);
    setTitle('');
    setDescription('');
    setHours(10);
    setPriority('high');
    loadTasks();
  };

  const handleDelete = async (id) => {
    if (confirm('Деактивировать задачу?')) {
      await deleteTask(id);
      loadTasks();
    }
  };

  const handleReactivate = async (id) => {
    await reactivateTask(id);
    loadTasks();
  };

  const handleCancel = () => {
    setEditingId(null);
    setTitle('');
    setDescription('');
    setHours(10);
    setPriority('high');
  };

  return (
    <div className="card">
      <h2>Бэклог задач</h2>
      
      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px', flexWrap: 'wrap' }}>
        <div className="form-group" style={{ flex: 2, minWidth: '200px' }}>
          <label>Название задачи</label>
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Написать API" />
        </div>
        <div className="form-group" style={{ flex: 2, minWidth: '200px' }}>
          <label>Описание</label>
          <input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Описание задачи" />
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
        {editingId ? (
          <>
            <button className="btn" onClick={handleUpdate} style={{ marginTop: '24px', backgroundColor: '#c4956a' }}>
              Сохранить
            </button>
            <button className="btn" onClick={handleCancel} style={{ marginTop: '24px', backgroundColor: '#7a7268' }}>
              Отмена
            </button>
          </>
        ) : (
          <button className="btn" onClick={handleAdd} style={{ marginTop: '24px' }}>
            Добавить
          </button>
        )}
      </div>

      <table className="table">
        <thead>
          <tr>
            <th>Название</th>
            <th>Описание</th>
            <th>Часов</th>
            <th>Приоритет</th>
            <th>Статус</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          {tasks.map((t) => (
            <tr key={t.id} style={{ opacity: t.is_active ? 1 : 0.5 }}>
              <td>{t.title}</td>
              <td>{t.description}</td>
              <td>{t.estimated_hours}</td>
              <td>{t.priority === 'high' ? '🔴 Высокий' : t.priority === 'medium' ? '🟡 Средний' : '🟢 Низкий'}</td>
              <td>{t.is_active ? 'Активна' : 'Неактивна'}</td>
              <td>
                {t.is_active ? (
                  <>
                    <button 
                      onClick={() => handleEdit(t)}
                      style={{ color: '#c4956a', background: 'none', border: 'none', cursor: 'pointer', marginRight: '12px' }}
                    >
                      Редактировать
                    </button>
                    <button 
                      onClick={() => handleDelete(t.id)}
                      style={{ color: '#c0392b', background: 'none', border: 'none', cursor: 'pointer' }}
                    >
                      Деактивировать
                    </button>
                  </>
                ) : (
                  <button 
                    onClick={() => handleReactivate(t.id)}
                    style={{ color: '#27ae60', background: 'none', border: 'none', cursor: 'pointer' }}
                  >
                    Восстановить
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div style={{ marginTop: '16px' }}>
        <label style={{ cursor: 'pointer' }}>
          <input 
            type="checkbox" 
            checked={showInactive} 
            onChange={(e) => setShowInactive(e.target.checked)}
            style={{ marginRight: '8px' }}
          />
          Показать неактивные задачи
        </label>
      </div>
    </div>
  );
}