import { Routes, Route, Navigate } from "react-router-dom";

import Login from "./pages/login";
import Register from "./pages/register";
import Home from "./pages/home";
import Upload from "./pages/upload";
import Result from "./pages/result";

function App() {
  return (
    <Routes>

      {/* Login Page */}
      <Route path="/" element={<Login />} />

      {/* Register Page */}
      <Route path="/register" element={<Register />} />

      {/* Home Page */}
      <Route path="/home" element={<Home />} />

      {/* Upload Page */}
      <Route path="/upload" element={<Upload />} />

      {/* Result Page */}
      <Route path="/result" element={<Result />} />

      {/* Invalid Route */}
      <Route path="*" element={<Navigate to="/" replace />} />

    </Routes>
  );
}

export default App;