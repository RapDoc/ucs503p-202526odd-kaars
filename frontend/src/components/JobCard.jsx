import React from "react";
import { MapPin, Building2, Star } from "lucide-react"; // Star icon for score

const JobCard = ({ job }) => {
    const { job_title, company, location, skills, reason, score } = job; // include score

    return (
        <div className="p-6 bg-white rounded-lg shadow hover:shadow-lg transition-shadow flex flex-col h-full">
            {/* Job Title and Company */}
            <div className="mb-3">
                <h3 className="text-lg font-semibold text-gray-800">{job_title}</h3>
                <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
                    <Building2 className="w-4 h-4" />
                    <span>{company}</span>
                </div>
            </div>

            {/* Location */}
            <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                <div className="flex items-center gap-1">
                    <MapPin className="w-4 h-4" />
                    <span>{location}</span>
                </div>
            </div>

            {/* Optional Score */}
            {score !== undefined && (
                <div className="flex items-center gap-2 text-sm text-yellow-600 mb-3">
                    <Star className="w-4 h-4" />
                    <span>Score: {score}</span>
                </div>
            )}

            {/* Reason */}
            <p className="text-sm text-gray-500 mb-3">
                <strong>Skills:</strong> {reason}
            </p>

            {/* Skills */}
            <div className="flex flex-wrap gap-2 mb-3">
                {skills.map((skill, idx) => (
                    <span
                        key={idx}
                        className="px-2 py-1 text-xs font-medium bg-blue-100 text-green-800 rounded"
                    >
                        {skill}
                    </span>
                ))}
            </div>

            {/* View Details Button at bottom */}
            <button className="w-full py-2 mt-auto rounded-lg bg-blue-500 hover:bg-blue-600 text-white font-semibold transition-colors">
                View Details
            </button>
        </div>
    );
};

export default JobCard;
