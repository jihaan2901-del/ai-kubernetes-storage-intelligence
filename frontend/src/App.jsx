import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid
} from "recharts";

const API = "http://localhost:8000";

export default function App() {

  const [pods, setPods] = useState([]);
  const [selectedPod, setSelectedPod] = useState(null);
  const [recommendation, setRecommendation] = useState(false);

  async function fetchPods() {

    const res = await fetch(`${API}/pods`);
    const data = await res.json();

    const updated = data.pods.map(p => ({
      ...p,
      history: [...p.history]
    }));

    setPods(updated);

    setSelectedPod(prev => {

      if (!prev) return updated[0] || null;

      const found = updated.find(p => p.name === prev.name);

      return found || updated[0] || null;

    });

  }

  async function checkRecommendation() {

    try {

      const res = await fetch(`${API}/recommendation`);
      const data = await res.json();

      setRecommendation(data.scale_down_recommended);

    } catch {}

  }

  async function proceedScaleDown() {

    await fetch(`${API}/scale-down`, {
      method: "POST"
    });

    setRecommendation(false);

  }

  async function stopPod(pod) {
    await fetch(`${API}/stop/${pod}`, { method: "POST" });
  }

  async function startPod(pod) {
    await fetch(`${API}/start/${pod}`, { method: "POST" });
  }

  async function deletePod(pod) {
    await fetch(`${API}/delete/${pod}`, { method: "POST" });
  }

  useEffect(() => {

    fetchPods();
    checkRecommendation();

    const interval = setInterval(() => {

      fetchPods();
      checkRecommendation();

    }, 3000);

    return () => clearInterval(interval);

  }, []);

  return (

    <div style={styles.page}>

      <h1 style={styles.title}>
        AI Kubernetes Storage Intelligence
      </h1>

      {/* AI RECOMMENDATION PANEL */}

      {recommendation && (

        <div style={styles.recommendationBox}>

          <h3>AI Recommendation</h3>

          <p>
            Storage has remained stable for 5 minutes.  
            It is recommended to scale down the cluster.
          </p>

          <button
            style={styles.scaleBtn}
            onClick={proceedScaleDown}
          >
            Proceed Scale Down
          </button>

        </div>

      )}

      <div style={styles.dashboard}>

        {/* SIDEBAR */}

        <div style={styles.sidebar}>

          <h3>Pods</h3>

          {pods.map(pod => {

            const usage = pod.used / pod.total;

            const health =
              usage > 0.8 ? "Critical"
              : usage > 0.5 ? "Warning"
              : "Healthy";

            const stateColor =
              pod.state === "ACTIVE"
                ? "#22c55e"
                : "#64748b";

            const label = (pod.label || pod.name.split("-")[0]).toUpperCase();

            return (

              <div
                key={pod.name}
                style={{
                  ...styles.podItem,
                  border:
                    selectedPod?.name === pod.name
                      ? "2px solid #38bdf8"
                      : "2px solid transparent"
                }}
                onClick={() => setSelectedPod(pod)}
              >

                <div style={styles.podHeader}>

                  <div>

                    <div style={styles.podLabel}>
                      {label}
                    </div>

                    <div style={styles.podName}>
                      {pod.name}
                    </div>

                  </div>

                  <div
                    style={{
                      background: stateColor,
                      padding: "4px 8px",
                      borderRadius: "6px",
                      fontSize: "11px",
                      color: "white"
                    }}
                  >
                    {pod.state}
                  </div>

                </div>

                <div
                  style={{
                    ...styles.status,
                    background:
                      health === "Critical" ? "#ef4444"
                      : health === "Warning" ? "#f59e0b"
                      : "#22c55e"
                  }}
                >
                  {health}
                </div>

                <div style={styles.actions}>

                  {pod.state === "ACTIVE" ? (

                    <button
                      style={styles.stopBtn}
                      onClick={(e)=>{
                        e.stopPropagation();
                        stopPod(pod.name);
                      }}
                    >
                      Stop
                    </button>

                  ) : (

                    <button
                      style={styles.startBtn}
                      onClick={(e)=>{
                        e.stopPropagation();
                        startPod(pod.name);
                      }}
                    >
                      Start
                    </button>

                  )}

                  <button
                    style={styles.deleteBtn}
                    onClick={(e)=>{
                      e.stopPropagation();
                      deletePod(pod.name);
                    }}
                  >
                    Delete
                  </button>

                </div>

              </div>

            );

          })}

        </div>

        {/* MAIN PANEL */}

        <div style={styles.main}>

          {selectedPod && (

            <>

              <h2>
                {(selectedPod.label || selectedPod.name.split("-")[0]).toUpperCase()}
              </h2>

              <div style={styles.metrics}>

                <Metric
                  title="Storage Used"
                  value={`${selectedPod.used.toFixed(2)} GB`}
                />

                <Metric
                  title="Remaining"
                  value={`${selectedPod.remaining.toFixed(2)} GB`}
                />

                <Metric
                  title="Prediction"
                  value={selectedPod.prediction}
                />

              </div>

              <div style={styles.chart}>

                <ResponsiveContainer width="100%" height="100%">

                  <LineChart
                    key={selectedPod.name + selectedPod.history.length}
                    data={selectedPod.history}
                  >

                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />

                    <XAxis
                      dataKey="timestamp"
                      tickFormatter={(t)=>
                        new Date(t * 1000).toLocaleTimeString()
                      }
                      stroke="#94a3b8"
                    />

                    <YAxis stroke="#94a3b8" />

                    <Tooltip
                      labelFormatter={(t)=>
                        new Date(t * 1000).toLocaleTimeString()
                      }
                    />

                    <Line
                      type="monotone"
                      dataKey="storage_used"
                      stroke="#38bdf8"
                      strokeWidth={3}
                      dot={false}
                      isAnimationActive={false}
                    />

                  </LineChart>

                </ResponsiveContainer>

              </div>

            </>

          )}

        </div>

      </div>

    </div>

  );

}

function Metric({title,value}) {

  return (

    <div style={styles.metricBox}>

      <div style={styles.metricTitle}>{title}</div>

      <div style={styles.metricValue}>{value}</div>

    </div>

  );

}

const styles = {

  page:{
    padding:"30px",
    background:"#0f172a",
    minHeight:"100vh",
    color:"#e2e8f0",
    fontFamily:"Inter"
  },

  title:{
    marginBottom:"20px"
  },

  recommendationBox:{
    background:"#1e293b",
    padding:"20px",
    borderRadius:"10px",
    marginBottom:"20px",
    border:"2px solid #38bdf8"
  },

  scaleBtn:{
    background:"#38bdf8",
    border:"none",
    padding:"8px 16px",
    borderRadius:"6px",
    color:"white",
    cursor:"pointer",
    marginTop:"10px"
  },

  dashboard:{
    display:"flex",
    height:"80vh",
    gap:"20px"
  },

  sidebar:{
    width:"300px",
    background:"#1e293b",
    padding:"20px",
    borderRadius:"10px",
    overflowY:"auto"
  },

  podItem:{
    background:"#0f172a",
    padding:"12px",
    marginTop:"10px",
    borderRadius:"8px",
    cursor:"pointer",
    display:"flex",
    flexDirection:"column",
    gap:"6px"
  },

  podHeader:{
    display:"flex",
    justifyContent:"space-between"
  },

  podLabel:{
    fontWeight:"bold"
  },

  podName:{
    fontSize:"12px",
    color:"#94a3b8"
  },

  status:{
    color:"white",
    padding:"3px 8px",
    borderRadius:"5px",
    fontSize:"12px",
    width:"fit-content"
  },

  actions:{
    display:"flex",
    gap:"8px"
  },

  stopBtn:{
    background:"#f59e0b",
    border:"none",
    padding:"4px 8px",
    borderRadius:"5px",
    cursor:"pointer",
    color:"white"
  },

  startBtn:{
    background:"#22c55e",
    border:"none",
    padding:"4px 8px",
    borderRadius:"5px",
    cursor:"pointer",
    color:"white"
  },

  deleteBtn:{
    background:"#ef4444",
    border:"none",
    padding:"4px 8px",
    borderRadius:"5px",
    cursor:"pointer",
    color:"white"
  },

  main:{
    flex:1,
    background:"#1e293b",
    padding:"25px",
    borderRadius:"10px",
    display:"flex",
    flexDirection:"column"
  },

  metrics:{
    display:"flex",
    gap:"20px",
    marginBottom:"20px"
  },

  metricBox:{
    flex:1,
    background:"#334155",
    padding:"15px",
    borderRadius:"8px"
  },

  metricTitle:{
    fontSize:"12px",
    color:"#94a3b8"
  },

  metricValue:{
    fontSize:"22px",
    fontWeight:"bold"
  },

  chart:{
    flex:1,
    background:"#0f172a",
    padding:"15px",
    borderRadius:"10px"
  }

};