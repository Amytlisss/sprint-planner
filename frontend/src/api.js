const API_BASE = 'http://localhost:8000';

export async function getMembers(includeInactive = false) {
  const response = await fetch(`${API_BASE}/members?include_inactive=${includeInactive}`);
  return response.json();
}

export async function createMember(data) {
  const response = await fetch(`${API_BASE}/members`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return response.json();
}

export async function updateMember(id, data) {
  const response = await fetch(`${API_BASE}/members/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return response.json();
}

export async function deleteMember(id) {
  const response = await fetch(`${API_BASE}/members/${id}`, {
    method: 'DELETE',
  });
  return response.json();
}

export async function reactivateMember(id) {
  const response = await fetch(`${API_BASE}/members/${id}/reactivate`, {
    method: 'POST',
  });
  return response.json();
}

export async function getTasks(includeInactive = false) {
  const response = await fetch(`${API_BASE}/tasks?include_inactive=${includeInactive}`);
  return response.json();
}

export async function createTask(data) {
  const response = await fetch(`${API_BASE}/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return response.json();
}

export async function updateTask(id, data) {
  const response = await fetch(`${API_BASE}/tasks/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return response.json();
}

export async function deleteTask(id) {
  const response = await fetch(`${API_BASE}/tasks/${id}`, {
    method: 'DELETE',
  });
  return response.json();
}

export async function reactivateTask(id) {
  const response = await fetch(`${API_BASE}/tasks/${id}/reactivate`, {
    method: 'POST',
  });
  return response.json();
}

export async function calculateSprint(data) {
  const response = await fetch(`${API_BASE}/sprints/calculate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return response.json();
}

export async function getSprints() {
  const response = await fetch(`${API_BASE}/sprints`);
  return response.json();
}

export async function getAbsences() {
  const response = await fetch(`${API_BASE}/absences`);
  return response.json();
}

export async function createAbsence(data) {
  const response = await fetch(`${API_BASE}/absences`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return response.json();
}

export async function deleteAbsence(id) {
  const response = await fetch(`${API_BASE}/absences/${id}`, {
    method: 'DELETE',
  });
  return response.json();
}