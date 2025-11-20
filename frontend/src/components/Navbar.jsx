import React, { useState } from "react";
import { NavLink } from "react-router-dom";

const Navbar = () => {
    const [open, setOpen] = useState(false);

    return (
        <div className="w-full bg-white shadow font-medium">
            <div className="flex items-center justify-between py-5 px-6 md:px-10">
                {/* Logo */}
                <NavLink to="/" className="text-3xl font-bold text-blue-600">
                    JobWise
                </NavLink>

                {/* Desktop Menu */}
                <ul className="hidden md:flex gap-10 text-gray-700">
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
                                    className={`w-2/4 h-[1.5px] bg-blue-600 border-none ${isActive
                                        ? "block"
                                        : "hidden group-hover:block"
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
                                    className={`w-2/4 h-[1.5px] bg-blue-600 border-none ${isActive
                                        ? "block"
                                        : "hidden group-hover:block"
                                        }`}
                                />
                            </>
                        )}
                    </NavLink>
                </ul>

                {/* Hamburger Button (Mobile) */}
                <button
                    className="md:hidden text-3xl text-gray-700"
                    onClick={() => setOpen(true)}
                >
                    ☰
                </button>
            </div>

            {/* Drawer Background Overlay */}
            {open && (
                <div
                    className="fixed inset-0 bg-opacity-40 z-30"
                    onClick={() => setOpen(false)}
                ></div>
            )}

            {/* Sliding Drawer */}
            <div
                className={`fixed top-0 right-0 h-full w-64 bg-blue-100 border-2 shadow-lg z-40 transform transition-transform duration-300 
                ${open ? "translate-x-0" : "translate-x-full"}`}
            >
                <div className="flex justify-between items-center p-5 border-b">
                    <h2 className="text-xl font-semibold">Menu</h2>
                    <button
                        className="text-3xl"
                        onClick={() => setOpen(false)}
                    >
                        ×
                    </button>
                </div>

                <div className="flex flex-col p-5 text-gray-800 gap-5 text-lg">
                    <NavLink
                        to="/joblistings"
                        onClick={() => setOpen(false)}
                    >
                        All Job Listings
                    </NavLink>

                    <NavLink
                        to="/"
                        onClick={() => setOpen(false)}
                    >
                        Jobs Recommendor
                    </NavLink>
                </div>
            </div>
        </div>
    );
};

export default Navbar;
