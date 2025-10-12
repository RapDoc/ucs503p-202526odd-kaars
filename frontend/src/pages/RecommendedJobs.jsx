import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import JobGrid from "../components/JobGrid";

const RecommendedJobs = () => {
    const [jobs, setJobs] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        const storedJobs = sessionStorage.getItem("recommendedJobs");
        if (storedJobs) {
            setJobs(JSON.parse(storedJobs));
        } else {
            // No jobs? Redirect back to home
            navigate("/");
        }
    }, [navigate]);

    return (
        <div className="min-h-screen bg-gray-50 py-10">
            <div className="container mx-auto px-4">
                <h1 className="text-4xl font-bold text-center mb-8 text-blue-600">
                    Recommended Jobs
                </h1>

                <JobGrid jobs={jobs} />
            </div>
        </div>
    );
};

export default RecommendedJobs;