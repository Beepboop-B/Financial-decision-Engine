const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function fetchHealth() {
  const res = await fetch(`${BASE_URL}/health`);
  if (!res.ok) throw new Error('Failed to fetch health');
  return res.json();
}

export async function fetchUser(userId: string) {
  const res = await fetch(`${BASE_URL}/users/${userId}`);
  if (!res.ok) throw new Error('User not found');
  return res.json();
}

export async function fetchUserPurchases(userId: string) {
  const res = await fetch(`${BASE_URL}/users/${userId}/purchases`);
  if (!res.ok) throw new Error('Failed to fetch purchases');
  return res.json();
}

export async function onboardUser(data: any) {
  const res = await fetch(`${BASE_URL}/users/onboarding`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error('Failed to onboard user');
  return res.json();
}

export async function fetchRequests() {
  const res = await fetch(`${BASE_URL}/requests`);
  if (!res.ok) throw new Error('Failed to fetch requests');
  return res.json();
}

export async function fetchRequestDetail(id: string) {
  const res = await fetch(`${BASE_URL}/requests/${id}`);
  if (!res.ok) throw new Error('Failed to fetch request detail');
  return res.json();
}

export async function createRequest(data: any) {
  const res = await fetch(`${BASE_URL}/requests`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error('Failed to create request');
  return res.json();
}

export async function evaluateRequest(id: string) {
  const res = await fetch(`${BASE_URL}/requests/${id}/evaluate`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to evaluate request');
  return res.json();
}

export async function fetchTrace(id: string) {
  const res = await fetch(`${BASE_URL}/requests/${id}/trace`);
  if (!res.ok) throw new Error('Failed to fetch trace');
  return res.json();
}

export async function fetchEvidence(id: string) {
  const res = await fetch(`${BASE_URL}/requests/${id}/evidence`);
  if (!res.ok) throw new Error('Failed to fetch evidence');
  return res.json();
}

export async function fetchUsage() {
  const res = await fetch(`${BASE_URL}/usage`);
  if (!res.ok) throw new Error('Failed to fetch usage');
  return res.json();
}
