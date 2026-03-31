import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"

export default function JobFeed() {
  const [jobs, setJobs] = useState([])
  const [uploadingId, setUploadingId] = useState(null)
  const navigate = useNavigate()

  const token = localStorage.getItem("token")

  useEffect(() => {
    if (!token) {
      navigate("/")
      return
    }

    fetch("http://127.0.0.1:5000/jobs-feed", {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => {
        if (res.status === 401 || res.status === 403) throw new Error("Not authorized")
        if (!res.ok) throw new Error("Request failed")
        return res.json()
      })
      .then(setJobs)
      .catch(err => {
        console.error(err)
        navigate("/dashboard")
      })
  }, [navigate, token])

  const handleApply = (jobId, file) => {
    if (!file) {
      alert("Please choose a PDF file.")
      return
    }

    if (file.type !== "application/pdf") {
      alert("Only PDF files are allowed.")
      return
    }

    const formData = new FormData()
    formData.append("job_id", jobId)
    formData.append("resume", file)

    setUploadingId(jobId)

    fetch("http://127.0.0.1:5000/apply", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: formData
    })
      .then(res => {
        if (!res.ok) throw new Error("Application failed")
        return res.json()
      })
      .then(() => {
        alert("Application submitted!")
      })
      .catch(err => {
        console.error(err)
        alert("Could not submit application.")
      })
      .finally(() => setUploadingId(null))
  }

  return (
    <div className="admin-page">
      <div className="admin-card">
        <div className="admin-header">
          <div className="admin-title-group">
            <div className="admin-badge">
              <span>●</span>
              Active Roles
            </div>
            <p>Browse all jobs and upload your resume as a candidate.</p>
          </div>
          <button
            className="admin-back-btn"
            type="button"
            onClick={() => navigate("/dashboard")}
          >
            <span>←</span>
            Back to dashboard
          </button>
        </div>

        <div className="admin-content">
          {jobs.length === 0 ? (
            <div className="admin-empty">No jobs available yet.</div>
          ) : (
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Location</th>
                  <th>Description</th>
                  <th>Apply</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map(j => (
                  <tr key={j.id}>
                    <td data-label="Title">{j.title}</td>
                    <td data-label="Location">{j.location}</td>
                    <td data-label="Description">{j.description}</td>
                    <td data-label="Apply">
                      <input
                        type="file"
                        accept="application/pdf"
                        onChange={e => handleApply(j.id, e.target.files[0])}
                        disabled={uploadingId === j.id}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  )
}

