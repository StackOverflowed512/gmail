import React, { createContext, useContext, useState, useEffect } from "react";

const HistoryContext = createContext();

export const useHistory = () => useContext(HistoryContext);

export const HistoryProvider = ({ children }) => {
    const [emailHistory, setEmailHistory] = useState({});

    // Load history from localStorage on mount
    useEffect(() => {
        const savedHistory = localStorage.getItem("emailHistory");
        if (savedHistory) {
            setEmailHistory(JSON.parse(savedHistory));
        }
    }, []);

    // Save history to localStorage whenever it changes
    useEffect(() => {
        localStorage.setItem("emailHistory", JSON.stringify(emailHistory));
    }, [emailHistory]);

    const updateHistory = (email, data) => {
        setEmailHistory((prev) => ({
            ...prev,
            [email]: {
                issues: [...(prev[email]?.issues || []), data.issue],
                replies: [...(prev[email]?.replies || []), data.reply],
                lastInteraction: new Date().toISOString(),
            },
        }));
    };

    const getHistory = (email) => {
        return (
            emailHistory[email] || {
                issues: [],
                replies: [],
                lastInteraction: null,
            }
        );
    };

    return (
        <HistoryContext.Provider value={{ updateHistory, getHistory }}>
            {children}
        </HistoryContext.Provider>
    );
};
