import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import EventPage from "./pages/EventPage";
import NotFound from "./pages/NotFound";
import EventDetail from "./pages/EventDetail";
import LoginPage from "./pages/LoginPage";
import MyPage from "./pages/MyPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
	<Route path="/login" element={<LoginPage />} />
        <Route path="/events" element={<EventPage />} />
	<Route path="/events/:id" element={<EventDetail />} />
        <Route path="*" element={<NotFound />} />
	<Route path="/mypage/:user_id" element={<MyPage />} />
      </Routes>
    </Router>
  );
}

export default App;
