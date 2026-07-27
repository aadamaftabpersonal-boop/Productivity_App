import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Reviewer from "./pages/Reviewer";
import Contests from "./pages/Contests";
import Weakness from "./pages/Weakness";
import Leaderboard from "./pages/Leaderboard";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/reviewer" element={<ProtectedRoute><Reviewer /></ProtectedRoute>} />
      <Route path="/contests" element={<ProtectedRoute><Contests /></ProtectedRoute>} />
      <Route path="/weakness" element={<ProtectedRoute><Weakness /></ProtectedRoute>} />
      <Route path="/leaderboard" element={<ProtectedRoute><Leaderboard /></ProtectedRoute>} />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}


export default App;