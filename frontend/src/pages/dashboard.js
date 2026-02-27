import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"

export default function Dashboard() {
  const [role, setRole] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    const token = localStorage.getItem("token")

    if (!token) {
      navigate("/")
      return
    }

    fetch("http://127.0.0.1:5000/profile", {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => setRole(data.role))
      .catch(() => navigate("/"))
  }, [navigate])

  const logout = () => {
    localStorage.removeItem("token")
    navigate("/")
  }

  return (
    <div>
      <h2>Dashboard</h2>

      <button onClick={logout}>Logout</button>

      <br /><br />

      {role === "admin" && (
        <button onClick={() => navigate("/admin")}>
          Go to Admin Panel
        </button>
      )}
    </div>
  )
}