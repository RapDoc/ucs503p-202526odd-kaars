import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import ResumeUpload from "./pages/ResumeUpload";
import JobGrid from "./components/JobGrid";
import jobs from "./components/jobs";
import NotFound from "./pages/NotFound";
import RecommendedJobs from "./pages/RecommendedJobs";

const App = () => {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/joblistings" element={<JobGrid jobs={jobs} />} />
        <Route path="/" element={<ResumeUpload />} />
        <Route path="/recommendedjobs" element={<RecommendedJobs />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
