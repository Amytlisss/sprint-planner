import { useState, useEffect } from 'react';
import { getMembers, createMember } from '../api';

export default function Team() {
  const [members, setMembers] = useState([]);
  const [name, setName] = useState('');
  const [role, setRole] = useState('');
  const [hours, setHours] = useState(8);

  useEffect(() => {
    loadMembers();
  }, []);

  const loadMembers = async () => {
    const data = await getMembers();
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
        <button className="btn" onClick={handleAdd} style={{ marginTop: '24px' }}>
          Добавить
        </button>
      </div>

      <table className="table">
        <thead>
          <tr>
            <th>Имя</th>
            <th>Роль</th>
            <th>Часов в день</th>
          </tr>
        </thead>
        <tbody>
          {members.map((m) => (
            <tr key={m.id}>
              <td>{m.name}</td>
              <td>{m.role}</td>
              <td>{m.hours_per_day}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}