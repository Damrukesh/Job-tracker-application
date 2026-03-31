import { BrowserRouter, Routes, Route } from "react-router-dom"
import Login from "./pages/login"
import Signup from "./pages/signup"
import Dashboard from "./pages/dashboard"
import Admin from "./pages/admin"
import Jobs from "./pages/jobs"
import JobFeed from "./pages/jobFeed"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/jobs" element={<Jobs />} />
        <Route path="/jobs-feed" element={<JobFeed />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App