import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"

export default function Jobs() {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [location, setLocation] = useState("")
  const [jobs, setJobs] = useState([])

  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const token = localStorage.getItem("token")

  useEffect(() => {
    if (!token) {
      navigate("/")
      return
    }

    setLoading(true)
    fetch("http://127.0.0.1:5000/jobs", {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => {
        if (res.status === 401 || res.status === 403) throw new Error("Not authorized")
        if (!res.ok) throw new Error("Request failed")
        return res.json()
      })
      .then(setJobs)
      .catch(() => navigate("/dashboard"))
      .finally(() => setLoading(false))
  }, [navigate, token])

  const createJob = () => {
    if (!title || !description || !location) {
      alert("Please fill title, description, and location.")
      return
    }

    setLoading(true)
    fetch("http://127.0.0.1:5000/jobs", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ title, description, location })
    })
      .then(res => {
        if (res.status === 401 || res.status === 403) throw new Error("Not authorized")
        if (!res.ok) throw new Error("Request failed")
        return res.json()
      })
      .then(() => {
        setTitle("")
        setDescription("")
        setLocation("")
        return fetch("http://127.0.0.1:5000/jobs", {
          headers: { Authorization: `Bearer ${token}` }
        })
      })
      .then(res => res.json())
      .then(setJobs)
      .catch(err => {
        console.error(err)
        alert("Could not create job.")
      })
      .finally(() => setLoading(false))
  }

  return (
    <div className="admin-page">
      <div className="admin-card">
        <div className="admin-header">
          <div className="admin-title-group">
            <div className="admin-badge">
              <span>●</span>
              Recruiter Jobs
            </div>
            <h2>My Job Posts</h2>
            <p>Create job descriptions and view what you’ve posted.</p>
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
          <div className="admin-section-header">
            <h3>Create Job</h3>
            <small>{loading ? "Working..." : "Add a new post"}</small>
          </div>

          <div className="admin-form" style={{ marginTop: 12 }}>
            <div className="admin-field" style={{ marginBottom: 10 }}>
              <label>Name/Title</label>
              <input
                value={title}
                onChange={e => setTitle(e.target.value)}
                style={{ width: "100%", padding: 8 }}
              />
            </div>

            <div className="admin-field" style={{ marginBottom: 10 }}>
              <label>Location</label>
              <input
                value={location}
                onChange={e => setLocation(e.target.value)}
                style={{ width: "100%", padding: 8 }}
              />
            </div>

            <div className="admin-field" style={{ marginBottom: 10 }}>
              <label>Description</label>
              <textarea
                value={description}
                onChange={e => setDescription(e.target.value)}
                rows={5}
                style={{ width: "100%", padding: 8 }}
              />
            </div>

            <button className="dashboard-btn" type="button" onClick={createJob} disabled={loading}>
              Create Job
            </button>
          </div>

          <div className="admin-section-header" style={{ marginTop: 26 }}>
            <h3>Existing Posts</h3>
            <small>{jobs.length} total</small>
          </div>

          {loading ? (
            <div className="admin-empty">Loading...</div>
          ) : jobs.length === 0 ? (
            <div className="admin-empty">No job posts yet.</div>
          ) : (
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Location</th>
                  <th>Created</th>
                  <th>Applications (Score)</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map(j => (
                  <tr key={j.id}>
                    <td data-label="Title">{j.title}</td>
                    <td data-label="Location">{j.location}</td>
                    <td data-label="Created">
                      {j.date_created ? new Date(j.date_created).toLocaleString() : "-"}
                    </td>
                    <td data-label="Applications (Score)">
                      {j.applications && j.applications.length > 0
                        ? j.applications.map(app => (
                            <div key={app.id}>
                              {app.candidate_name}: {app.match_score}%
                            </div>
                          ))
                        : "No applications"}
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

