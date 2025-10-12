import React from "react";
import { NavLink } from "react-router-dom";

const Navbar = () => {
    return (
        <div className="flex items-center justify-between py-5 px-10 bg-white shadow font-medium">
            {/* Logo */}
            <NavLink to="/" className="text-3xl font-bold text-blue-600">
                JobWise
            </NavLink>

            {/* Menu */}
            <ul className="flex gap-10 text-gray-700">
                <NavLink
                    to="/joblistings"
                    className="flex flex-col items-center gap-1 group"
                >
                    {({ isActive }) => (
                        <>
                            <p className="transition duration-200 group-hover:-translate-y-0.5">
                                All Job Listings
                            </p>
                            <hr
                                className={`w-2/4 h-[1.5px] bg-blue-600 border-none ${isActive ? "block" : "hidden group-hover:block"
                                    }`}
                            />
                        </>
                    )}
                </NavLink>

                <NavLink
                    to="/"
                    className="flex flex-col items-center gap-1 group"
                >
                    {({ isActive }) => (
                        <>
                            <p className="transition duration-200 group-hover:-translate-y-0.5">
                                Jobs Recommendor
                            </p>
                            <hr
                                className={`w-2/4 h-[1.5px] bg-blue-600 border-none ${isActive ? "block" : "hidden group-hover:block"
                                    }`}
                            />
                        </>
                    )}
                </NavLink>
            </ul>
        </div>
    );
};

export default Navbar;
