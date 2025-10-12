import React from "react";
import JobCard from "./JobCard";

const JobGrid = ({ jobs }) => {
    return (
        <div className="container mx-auto px-4 py-10">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {jobs.map((job, idx) => (
                    <JobCard key={idx} job={job} />
                ))}
            </div>
        </div>
    );
};

export default JobGrid;
