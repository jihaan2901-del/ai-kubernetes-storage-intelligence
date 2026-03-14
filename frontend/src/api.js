export async function fetchPods() {
  const res = await fetch("http://localhost:8000/pods");
  return res.json();
}