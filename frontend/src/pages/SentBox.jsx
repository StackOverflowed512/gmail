import React, { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { Link } from "react-router";

function SentBox() {
    const [searchQuery, setSearchQuery] = useState("");
    const { sent, sentMails, fetchingMail } = useAuth();
    const [filteredEmails, setFilteredEmails] = useState([]);
    const [page, setPage] = useState(1);

    // Function to decode email subjects
    const decodeSubject = (subject) => {
        try {
            return decodeURIComponent(
                subject
                    .replace(/=\?UTF-8\?Q\?/gi, "")
                    .replace(/_/g, " ")
                    .replace(/=([0-9A-F]{2})/gi, "%$1")
            );
        } catch {
            return subject;
        }
    };

    // Search & filter emails
    useEffect(() => {
        if (sent) {
            setFilteredEmails(
                sent.filter((email) =>
                    email.subject.toLowerCase().includes(searchQuery.toLowerCase())
                )
            );
        }
    }, [searchQuery, sent]);

    useEffect(() => {
        sentMails({
            page: page,
            per_page: 10,
        });
    }, [page]);

    return (
        <div className="grid grid-row-12 grid-cols-1 h-[90%] bg-[#181818] text-white">
            {/* Search Bar */}
            <div className="p-4 row-span-1 bg-[#1E1E1E] shadow-lg">
                <input
                    type="text"
                    placeholder="Search sent emails..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full px-4 py-2 bg-[#2D2D2D] text-white placeholder-[#B3B3B3] border border-[#333333] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#4A4A4A] hover:bg-[#3D3D3D] transition-colors"
                />
                <div className="flex gap-2 items-center">
                    <button
                        className="bg-[#4A4A4A] text-white px-4 py-2 rounded-lg mt-2 hover:bg-[#5A5A5A] transition-colors"
                        disabled={page === 1}
                        onClick={() => {
                            if (page > 1) {
                                setPage(page - 1);
                            }
                        }}
                    >
                        Previous page
                    </button>
                    <button
                        className="bg-[#4A4A4A] text-white px-4 py-2 rounded-lg mt-2 hover:bg-[#5A5A5A] transition-colors"
                        onClick={() => {
                            setPage(page + 1);
                        }}
                    >
                        Next page
                    </button>
                </div>
            </div>

            {/* Sent Email List */}
            <div className="row-span-8 overflow-y-scroll">
                {filteredEmails.length > 0 && fetchingMail && (
                    <p className="text-center text-gray-500">Loading...</p>
                )}
                <div className="p-6 rounded-lg flex flex-col gap-2">
                    {filteredEmails.length > 0 ? (
                        filteredEmails.map((email) => (
                            <Link
                                to={`/dashboard/sent/${email.uid}`}
                                key={email.uid}
                                className="p-3 w-full cursor-pointer border border-accent rounded-2xl"
                            >
                                <p className="text-sm text-gray-400">{email.date}</p>
                                <h3 className="font-semibold text-gray-100">
                                    {decodeSubject(email.subject)}
                                </h3>
                                <p className="text-gray-300">To: {email.to}</p>
                            </Link>
                        ))
                    ) : fetchingMail ? (
                        <p className="text-center text-gray-500">Loading...</p>
                    ) : (
                        <p className="text-center text-gray-500">No sent emails found.</p>
                    )}
                </div>
            </div>
        </div>
    );
}

export default SentBox;