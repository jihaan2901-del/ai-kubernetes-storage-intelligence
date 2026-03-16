const API = "http://localhost:8000";

export async function fetchPods() {
  const res = await fetch(`${API}/pods`);
  return res.json();
}

export async function stopPod(pod) {
  await fetch(`${API}/stop/${pod}`, {
    method: "POST"
  });
}

export async function startPod(pod) {
  await fetch(`${API}/start/${pod}`, {
    method: "POST"
  });
}

export async function deletePod(pod) {
  await fetch(`${API}/delete/${pod}`, {
    method: "POST"
  });
}

export async function getRecommendation(){
  const res = await fetch("http://localhost:8000/recommendation");
  return res.json();
}

export async function scaleDown(){
  await fetch("http://localhost:8000/scale-down",{
    method:"POST"
  });
}