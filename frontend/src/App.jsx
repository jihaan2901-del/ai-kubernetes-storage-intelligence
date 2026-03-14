import { useEffect, useState } from "react";
import { fetchPods } from "./api";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid
} from "recharts";

export default function App() {

  const [pods, setPods] = useState([]);
  const [selectedPod, setSelectedPod] = useState(null);

  async function load() {
    try {

      const data = await fetchPods();

      const updatedPods = data.pods.map(p => ({
        ...p,
        history: [...p.history]
      }));

      setPods(updatedPods);

      setSelectedPod(prev => {
        if (!prev) return updatedPods[0] || null;
        const updated = updatedPods.find(p => p.name === prev.name);
        return updated || prev;
      });

    } catch (err) {
      console.error(err);
    }
  }

  useEffect(() => {

    load();

    const interval = setInterval(() => {
      load();
    }, 3000);

    return () => clearInterval(interval);

  }, []);

  return (

    <div style={styles.page}>

      <h1 style={styles.title}>AI Kubernetes Storage Intelligence</h1>

      <div style={styles.dashboard}>

        {/* LEFT SIDEBAR */}
        <div style={styles.sidebar}>

          <h3>Pods</h3>

          {pods.map(pod => {

            const usage = pod.used / pod.total;

            const status =
              usage > 0.8 ? "Critical"
              : usage > 0.5 ? "Warning"
              : "Healthy";

            return (

              <div
                key={pod.name}
                style={{
                  ...styles.podItem,
                  background:
                    selectedPod?.name === pod.name
                      ? "#334155"
                      : "transparent"
                }}
                onClick={() => setSelectedPod(pod)}
              >

                <span>{pod.name}</span>

                <span style={{
                  ...styles.status,
                  background:
                    status==="Critical" ? "#ef4444"
                    : status==="Warning" ? "#f59e0b"
                    : "#22c55e"
                }}>
                  {status}
                </span>

              </div>

            );

          })}

        </div>


        {/* RIGHT PANEL */}

        <div style={styles.main}>

          {selectedPod && (

            <>
              <h2>{selectedPod.name}</h2>

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

              {/* GRAPH */}

              <div style={styles.chart}>

                <ResponsiveContainer width="100%" height="100%">

                  <LineChart
                    key={selectedPod.name + selectedPod.history.length}
                    data={selectedPod.history}
                  >

                    <CartesianGrid strokeDasharray="3 3" />

                    <XAxis
                      dataKey="timestamp"
                      tickFormatter={(t)=>
                        new Date(t * 1000).toLocaleTimeString()
                      }
                    />

                    <YAxis />

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
    width:"100vw",
    boxSizing:"border-box",
    color:"#e2e8f0",
    fontFamily:"Inter, sans-serif"
  },

  title:{
    marginBottom:"25px"
  },

  dashboard:{
    display:"flex",
    width:"100%",
    height:"80vh",
    gap:"20px"
  },

  sidebar:{
    width:"260px",
    minWidth:"260px",
    background:"#1e293b",
    padding:"20px",
    borderRadius:"10px",
    overflowY:"auto"
  },

  podItem:{
    display:"flex",
    justifyContent:"space-between",
    padding:"10px",
    marginTop:"10px",
    borderRadius:"6px",
    cursor:"pointer",
    transition:"0.2s"
  },

  status:{
    color:"white",
    padding:"3px 8px",
    borderRadius:"5px",
    fontSize:"12px"
  },

  main:{
    flex:1,
    width:"100%",
    background:"#1e293b",
    padding:"25px",
    borderRadius:"10px",
    display:"flex",
    flexDirection:"column"
  },

  metrics:{
    display:"flex",
    gap:"20px",
    marginBottom:"25px"
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