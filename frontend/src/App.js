// import React, { useState } from "react";
// import axios from "axios";

// function App() {
//   const [file, setFile] = useState(null);
//   const [data, setData] = useState(null);
//   const [loading, setLoading] = useState(false);

//   const handleUpload = async () => {
//     if (!file) {
//       alert("Please upload a BRD file");
//       return;
//     }

//     const formData = new FormData();
//     formData.append("file", file);

//     setLoading(true);

//     try {
//       const res = await axios.post("http://localhost:8000/generate", formData);
//       setData(res.data);
//     } catch (error) {
//       console.error(error);
//       alert("Error generating test cases");
//     }

//     setLoading(false);
//   };

//   const openJira = () => {
//   window.open(
//     "https://jira.gosi.ins/secure/XrayCSVSetupPage!default.jspa?externalSystem=com.xpandit.plugins.xray:XrayBulkCSVImporter",
//     "_blank"
//   );
// };

//   return (
//     <div style={styles.page}>
//       <div style={styles.card}>
//         <h1 style={styles.title}>🚀 BRD Test Case Generator</h1>
//         <p style={styles.subtitle}>
//           Upload your BRD and generate test cases instantly
//         </p>

//         <div style={styles.uploadBox}>
//           <input
//             type="file"
//             accept=".txt"
//             onChange={(e) => setFile(e.target.files[0])}
//           />
//         </div>

//         <button style={styles.button} onClick={handleUpload}>
//           Generate Test Cases
//         </button>

//         {loading && <p style={styles.loading}>⏳ Generating...</p>}
//       </div>

//       {data && (
//         <div style={styles.resultCard}>
//           <h2>📌 Feature: {data.feature_name}</h2>
//           <p><strong>Test Set:</strong> {data.testset_key}</p>

//           <p style={{ marginBottom: "10px" }}>
//             Download file and upload in Jira → Xray Import
//           </p>

//           <div style={styles.tableContainer}>
//             <table style={styles.table}>
//               <thead>
//                 <tr>
//                   <th>Summary</th>
//                   <th>Description</th>
//                   <th>Steps</th>
//                   <th>Priority</th>
//                 </tr>
//               </thead>
//               <tbody>
//                 {data.preview.map((row, index) => (
//                   <tr key={index}>
//                     <td>{row.Summary}</td>
//                     <td>{row.Description}</td>
//                     <td>{row.Steps}</td>
//                     <td>{row.Priority}</td>
//                   </tr>
//                 ))}
//               </tbody>
//             </table>
//           </div>

//           <div style={styles.actions}>
//             <a
//   href={`http://localhost:8000/output/${data.feature_name}.csv`}
//   download={`${data.feature_name}.csv`}
//   style={styles.downloadBtn}
// >
//   ⬇ CSV
// </a>

// <a
//   href={`http://localhost:8000/output/${data.feature_name}.xlsx`}
//   download={`${data.feature_name}.xlsx`}
//   style={styles.downloadBtn}
// >
//   ⬇ Excel
// </a>

//             <button style={styles.jiraBtn} onClick={openJira}>
//               🚀 Open Jira
//             </button>
//           </div>
//         </div>
//       )}
//     </div>
//   );
// }

// const styles = {
//   page: {
//     fontFamily: "Arial, sans-serif",
//     background: "#f4f6f8",
//     minHeight: "100vh",
//     padding: "40px",
//   },
//   card: {
//     maxWidth: "600px",
//     margin: "0 auto",
//     background: "#fff",
//     padding: "30px",
//     borderRadius: "12px",
//     boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
//     textAlign: "center",
//   },
//   resultCard: {
//     marginTop: "30px",
//     background: "#fff",
//     padding: "20px",
//     borderRadius: "12px",
//     boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
//   },
//   title: {
//     marginBottom: "10px",
//   },
//   subtitle: {
//     color: "#666",
//     marginBottom: "20px",
//   },
//   uploadBox: {
//     marginBottom: "20px",
//   },
//   button: {
//     background: "#007bff",
//     color: "#fff",
//     border: "none",
//     padding: "10px 20px",
//     borderRadius: "6px",
//     cursor: "pointer",
//   },
//   loading: {
//     marginTop: "10px",
//   },
//   tableContainer: {
//     overflowX: "auto",
//     marginTop: "20px",
//   },
//   table: {
//     width: "100%",
//     borderCollapse: "collapse",
//   },
//   actions: {
//     marginTop: "20px",
//     display: "flex",
//     gap: "10px",
//   },
//   downloadBtn: {
//     padding: "10px 15px",
//     background: "#28a745",
//     color: "#fff",
//     textDecoration: "none",
//     borderRadius: "6px",
//   },
//   jiraBtn: {
//     padding: "10px 15px",
//     background: "#ff9800",
//     color: "#fff",
//     border: "none",
//     borderRadius: "6px",
//     cursor: "pointer",
//   },
// };

// export default App;


import React, { useState } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [refinePrompt, setRefinePrompt] = useState("");
  const [refineLoading, setRefineLoading] = useState(false);

  // Upload and generate test cases
  const handleUpload = async () => {
    if (!file) {
      alert("Please upload a BRD file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);

    try {
      const res = await axios.post("http://localhost:8000/generate", formData);
      setData(res.data);
    } catch (error) {
      console.error(error);
      alert("Error generating test cases");
    }

    setLoading(false);
  };

  // Open Jira link
  const openJira = () => {
    window.open(
      "https://jira.gosi.ins/secure/XrayCSVSetupPage!default.jspa?externalSystem=com.xpandit.plugins.xray:XrayBulkCSVImporter",
      "_blank"
    );
  };

  // Refine test cases with user prompt
  const handleRefine = async () => {
    if (!refinePrompt) {
      alert("Enter refinement instructions");
      return;
    }
  
    if (!data || !data.feature_name) {
      alert("Please generate test cases first.");
      return;
    }
  
    setRefineLoading(true);
  
    try {
      console.log("Sending refine request:", {
        feature_name: data.feature_name,
        prompt: refinePrompt,
      });
  
      const res = await axios.post("http://localhost:8000/refine", {
        feature_name: data.feature_name,
        prompt: refinePrompt,
      });
  
      console.log("Refine response:", res.data);
  
      const newData = res.data;
  
      setData({
        ...data,
        preview: newData.preview || [],
        version: newData.version,
        csv_file: newData.csv_file,
        excel_file: newData.excel_file,
      });
  
      alert(`Refined to version v${newData.version}`);
      setRefinePrompt("");
    } catch (err) {
      console.error("Refine error:", err.response ? err.response.data : err.message);
      alert("Error refining test cases");
    } finally {
      setRefineLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h1 style={styles.title}>🚀 BRD Test Case Generator</h1>
        <p style={styles.subtitle}>
          Upload your BRD and generate test cases instantly
        </p>

        <div style={styles.uploadBox}>
          <input
            type="file"
            accept=".txt"
            onChange={(e) => setFile(e.target.files[0])}
          />
        </div>

        <button style={styles.button} onClick={handleUpload}>
          Generate Test Cases
        </button>

        {loading && <p style={styles.loading}>⏳ Generating...</p>}
      </div>

      {data && (
        <div style={styles.resultCard}>
          <h2>📌 Feature: {data.feature_name}</h2>
          <p><strong>Test Set:</strong> {data.testset_key}</p>
          {data.version && <p><strong>Version:</strong> v{data.version}</p>}

          <p style={{ marginBottom: "10px" }}>
            Download file and upload in Jira → Xray Import
          </p>

          <div style={styles.tableContainer}>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th>Summary</th>
                  <th>Description</th>
                  <th>Steps</th>
                  <th>Priority</th>
                </tr>
              </thead>
              <tbody>
                {(data.preview || []).map((row, index) => (
                  <tr key={index}>
                    <td>{row.Summary}</td>
                    <td>{row.Description}</td>
                    <td>{row.Steps}</td>
                    <td>{row.Priority}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Refinement Section */}
          <div style={{ marginTop: "20px" }}>
            <textarea
              rows={3}
              cols={80}
              placeholder="Enter refinement instructions"
              value={refinePrompt}
              onChange={(e) => setRefinePrompt(e.target.value)}
            />
            <br />
            <button style={styles.button} onClick={handleRefine}>
              Refine Test Cases
            </button>
            {refineLoading && (
              <p style={{ marginTop: "10px", fontStyle: "italic" }}>
                ⏳ Refining test cases...
              </p>
            )}
          </div>

          {/* Download & Jira Buttons */}
          <div style={styles.actions}>
            {data.csv_file && (
              <a
                href={`http://localhost:8000/output/${data.feature_name}.csv`}
                download={`${data.feature_name}.csv`}
                style={styles.downloadBtn}
              >
                ⬇ CSV
              </a>
              
            )}

            {data.excel_file && (
              <a
                href={`http://localhost:8000/output/${data.feature_name}.xlsx`}
                download={`${data.feature_name}.xlsx`}
                style={styles.downloadBtn}
              >
                ⬇ Excel
              </a>
              
            )}

            <button style={styles.jiraBtn} onClick={openJira}>
              🚀 Open Jira
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

const styles = {
  page: {
    fontFamily: "Arial, sans-serif",
    background: "#f4f6f8",
    minHeight: "100vh",
    padding: "40px",
  },
  card: {
    maxWidth: "600px",
    margin: "0 auto",
    background: "#fff",
    padding: "30px",
    borderRadius: "12px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
    textAlign: "center",
  },
  resultCard: {
    marginTop: "30px",
    background: "#fff",
    padding: "20px",
    borderRadius: "12px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
  },
  title: { marginBottom: "10px" },
  subtitle: { color: "#666", marginBottom: "20px" },
  uploadBox: { marginBottom: "20px" },
  button: {
    background: "#007bff",
    color: "#fff",
    border: "none",
    padding: "10px 20px",
    borderRadius: "6px",
    cursor: "pointer",
    marginTop: "10px",
  },
  loading: { marginTop: "10px" },
  tableContainer: { overflowX: "auto", marginTop: "20px" },
  table: { width: "100%", borderCollapse: "collapse" },
  actions: { marginTop: "20px", display: "flex", gap: "10px" },
  downloadBtn: {
    padding: "10px 15px",
    background: "#28a745",
    color: "#fff",
    textDecoration: "none",
    borderRadius: "6px",
  },
  jiraBtn: {
    padding: "10px 15px",
    background: "#ff9800",
    color: "#fff",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
  },
};

export default App;