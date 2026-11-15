const API_BASE = 'http://localhost:8000';

export async function getMembers() {
  const response = await fetch(`${API_BASE}/members`);
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

export async function getTasks() {
  const response = await fetch(`${API_BASE}/tasks`);
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