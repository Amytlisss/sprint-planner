import { useState, useEffect } from 'react';
import { getMembers, createMember, updateMember, deleteMember, reactivateMember } from '../api';

export default function Team() {
  const [members, setMembers] = useState([]);
  const [name, setName] = useState('');
  const [role, setRole] = useState('');
  const [hours, setHours] = useState(8);
  const [editingId, setEditingId] = useState(null);
  const [showInactive, setShowInactive] = useState(false);

  useEffect(() => {
    loadMembers();
  }, [showInactive]);

  const loadMembers = async () => {
    const data = await getMembers(showInactive);
    setMembers(data);
  };

  const handleAdd = async () => {
    if (!name || !role) return;
    await createMember({ name, role, hours_per_day: hours });
    setName('');
    setRole('');
    setHours(8);
    loadMembers();
  };

  const handleEdit = (member) => {
    setEditingId(member.id);
    setName(member.name);
    setRole(member.role);
    setHours(member.hours_per_day);
  };

  const handleUpdate = async () => {
    if (!name || !role) return;
    await updateMember(editingId, { name, role, hours_per_day: hours });
    setEditingId(null);
    setName('');
    setRole('');
    setHours(8);
    loadMembers();
  };

  const handleDelete = async (id) => {
    if (confirm('Деактивировать сотрудника?')) {
      await deleteMember(id);
      loadMembers();
    }
  };

  const handleReactivate = async (id) => {
    await reactivateMember(id);
    loadMembers();
  };

  const handleCancel = () => {
    setEditingId(null);
    setName('');
    setRole('');
    setHours(8);
  };

  return (
    <div className="card">
      <h2>Команда</h2>
      
      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
        <div className="form-group" style={{ flex: 1 }}>
          <label>Имя</label>
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Вася" />
        </div>
        <div className="form-group" style={{ flex: 1 }}>
          <label>Роль</label>
          <input value={role} onChange={(e) => setRole(e.target.value)} placeholder="Backend Dev" />
        </div>
        <div className="form-group" style={{ width: '120px' }}>
          <label>Часов в день</label>
          <input type="number" value={hours} onChange={(e) => setHours(e.target.value)} min="1" max="24" />
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
            <th>Имя</th>
            <th>Роль</th>
            <th>Часов в день</th>
            <th>Статус</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          {members.map((m) => (
            <tr key={m.id} style={{ opacity: m.is_active ? 1 : 0.5 }}>
              <td>{m.name}</td>
              <td>{m.role}</td>
              <td>{m.hours_per_day}</td>
              <td>{m.is_active ? 'Активен' : 'Неактивен'}</td>
              <td>
                {m.is_active ? (
                  <>
                    <button 
                      onClick={() => handleEdit(m)}
                      style={{ color: '#c4956a', background: 'none', border: 'none', cursor: 'pointer', marginRight: '12px' }}
                    >
                      Редактировать
                    </button>
                    <button 
                      onClick={() => handleDelete(m.id)}
                      style={{ color: '#c0392b', background: 'none', border: 'none', cursor: 'pointer' }}
                    >
                      Деактивировать
                    </button>
                  </>
                ) : (
                  <button 
                    onClick={() => handleReactivate(m.id)}
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
          Показать неактивных сотрудников
        </label>
      </div>
    </div>
  );
}