import React, { useState, useEffect } from "react";
import { Trash, Plus, Loader2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Settings() {
    const [accounts, setAccounts] = useState([]);
    const [isAddingAccount, setIsAddingAccount] = useState(false);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const [newAccount, setNewAccount] = useState({
        email: "",
        password: "",
        custom_smtp_host: "",
        custom_smtp_port: "",
        custom_imap_host: "",
        custom_imap_port: "",
        useCustomServer: false,
    });

    const { login } = useAuth();

    useEffect(() => {
        // Load saved accounts from localStorage
        const savedAccounts = JSON.parse(
            localStorage.getItem("savedAccounts") || "[]"
        );
        setAccounts(savedAccounts);
    }, []);

    const handleAddAccount = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        try {
            const result = await login(newAccount.email, newAccount.password, {
                ...(newAccount.useCustomServer && {
                    custom_smtp_host: newAccount.custom_smtp_host,
                    custom_smtp_port: parseInt(newAccount.custom_smtp_port),
                    custom_imap_host: newAccount.custom_imap_host,
                    custom_imap_port: parseInt(newAccount.custom_imap_port),
                }),
            });

            if (result.success) {
                const accountToSave = {
                    email: newAccount.email,
                    password: newAccount.password,
                    ...(newAccount.useCustomServer && {
                        custom_smtp_host: newAccount.custom_smtp_host,
                        custom_smtp_port: newAccount.custom_smtp_port,
                        custom_imap_host: newAccount.custom_imap_host,
                        custom_imap_port: newAccount.custom_imap_port,
                    }),
                };

                const updatedAccounts = [...accounts, accountToSave];
                setAccounts(updatedAccounts);
                localStorage.setItem(
                    "savedAccounts",
                    JSON.stringify(updatedAccounts)
                );

                // Reset form
                setNewAccount({
                    email: "",
                    password: "",
                    custom_smtp_host: "",
                    custom_smtp_port: "",
                    custom_imap_host: "",
                    custom_imap_port: "",
                    useCustomServer: false,
                });
                setIsAddingAccount(false);
            } else {
                setError(result.error || "Failed to add account");
            }
        } catch (err) {
            setError("An error occurred while adding the account");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleRemoveAccount = (email) => {
        const confirmed = window.confirm(
            `Are you sure you want to remove ${email}?`
        );
        if (confirmed) {
            const updatedAccounts = accounts.filter(
                (account) => account.email !== email
            );
            setAccounts(updatedAccounts);
            localStorage.setItem(
                "savedAccounts",
                JSON.stringify(updatedAccounts)
            );
        }
    };

    return (
        <div className="p-6 bg-[#181818] min-h-[90%] text-white">
            <div className="max-w-4xl mx-auto">
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-2xl font-bold">Email Accounts</h1>
                    <button
                        onClick={() => setIsAddingAccount(!isAddingAccount)}
                        className="flex items-center gap-2 bg-blue-600 px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        <Plus size={20} />
                        <span>Add Account</span>
                    </button>
                </div>

                {error && (
                    <div className="mb-4 p-4 bg-red-500/10 border border-red-500 text-red-500 rounded-lg">
                        {error}
                    </div>
                )}

                {/* Add Account Form */}
                {isAddingAccount && (
                    <div className="mb-6 p-6 bg-[#232323] rounded-lg">
                        <h2 className="text-xl font-semibold mb-4">
                            Add New Email Account
                        </h2>
                        <form onSubmit={handleAddAccount} className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium mb-1">
                                        Email
                                    </label>
                                    <input
                                        type="email"
                                        value={newAccount.email}
                                        onChange={(e) =>
                                            setNewAccount({
                                                ...newAccount,
                                                email: e.target.value,
                                            })
                                        }
                                        className="w-full p-2 bg-[#1E1E1E] border border-[#333] rounded-lg"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">
                                        Password
                                    </label>
                                    <input
                                        type="password"
                                        value={newAccount.password}
                                        onChange={(e) =>
                                            setNewAccount({
                                                ...newAccount,
                                                password: e.target.value,
                                            })
                                        }
                                        className="w-full p-2 bg-[#1E1E1E] border border-[#333] rounded-lg"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="flex items-center gap-2">
                                <input
                                    type="checkbox"
                                    id="useCustomServer"
                                    checked={newAccount.useCustomServer}
                                    onChange={(e) =>
                                        setNewAccount({
                                            ...newAccount,
                                            useCustomServer: e.target.checked,
                                        })
                                    }
                                    className="rounded border-gray-300"
                                />
                                <label htmlFor="useCustomServer">
                                    Use Custom Mail Server
                                </label>
                            </div>

                            {newAccount.useCustomServer && (
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium mb-1">
                                            SMTP Host
                                        </label>
                                        <input
                                            type="text"
                                            value={newAccount.custom_smtp_host}
                                            onChange={(e) =>
                                                setNewAccount({
                                                    ...newAccount,
                                                    custom_smtp_host:
                                                        e.target.value,
                                                })
                                            }
                                            className="w-full p-2 bg-[#1E1E1E] border border-[#333] rounded-lg"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-1">
                                            SMTP Port
                                        </label>
                                        <input
                                            type="number"
                                            value={newAccount.custom_smtp_port}
                                            onChange={(e) =>
                                                setNewAccount({
                                                    ...newAccount,
                                                    custom_smtp_port:
                                                        e.target.value,
                                                })
                                            }
                                            className="w-full p-2 bg-[#1E1E1E] border border-[#333] rounded-lg"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-1">
                                            IMAP Host
                                        </label>
                                        <input
                                            type="text"
                                            value={newAccount.custom_imap_host}
                                            onChange={(e) =>
                                                setNewAccount({
                                                    ...newAccount,
                                                    custom_imap_host:
                                                        e.target.value,
                                                })
                                            }
                                            className="w-full p-2 bg-[#1E1E1E] border border-[#333] rounded-lg"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-1">
                                            IMAP Port
                                        </label>
                                        <input
                                            type="number"
                                            value={newAccount.custom_imap_port}
                                            onChange={(e) =>
                                                setNewAccount({
                                                    ...newAccount,
                                                    custom_imap_port:
                                                        e.target.value,
                                                })
                                            }
                                            className="w-full p-2 bg-[#1E1E1E] border border-[#333] rounded-lg"
                                        />
                                    </div>
                                </div>
                            )}

                            <div className="flex justify-end gap-2">
                                <button
                                    type="button"
                                    onClick={() => setIsAddingAccount(false)}
                                    className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="flex items-center gap-2 bg-blue-600 px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                                >
                                    {loading ? (
                                        <>
                                            <Loader2
                                                size={20}
                                                className="animate-spin"
                                            />
                                            <span>Adding...</span>
                                        </>
                                    ) : (
                                        <>
                                            <Plus size={20} />
                                            <span>Add Account</span>
                                        </>
                                    )}
                                </button>
                            </div>
                        </form>
                    </div>
                )}

                {/* Accounts List */}
                <div className="space-y-4">
                    {accounts.map((account) => (
                        <div
                            key={account.email}
                            className="flex items-center justify-between p-4 bg-[#232323] rounded-lg"
                        >
                            <div>
                                <h3 className="font-medium">{account.email}</h3>
                                {account.custom_smtp_host && (
                                    <p className="text-sm text-gray-400">
                                        Custom Server:{" "}
                                        {account.custom_smtp_host}
                                    </p>
                                )}
                            </div>
                            <button
                                onClick={() =>
                                    handleRemoveAccount(account.email)
                                }
                                className="p-2 text-gray-400 hover:text-red-500 transition-colors"
                                title="Remove Account"
                            >
                                <Trash size={20} />
                            </button>
                        </div>
                    ))}

                    {accounts.length === 0 && !isAddingAccount && (
                        <p className="text-center text-gray-400 py-8">
                            No email accounts configured. Click "Add Account" to
                            get started.
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
}
