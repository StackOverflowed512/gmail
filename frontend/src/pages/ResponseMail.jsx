import React, { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router";
import { BrainCog, Send } from "lucide-react";
import { useHistory } from "../context/HistoryContext";

function ResponseMail() {
    const { uid } = useParams();
    const [mail, setMail] = useState();
    const bodyRef = useRef(null);
    const [response, setResponse] = useState("");
    const [isPending, startTransition] = React.useTransition();
    const [isPendingPredict, startTransitionPredict] = React.useTransition();
    const [isLoading, setIsLoading] = useState(false);
    const [isLoadingPredict, setIsLoadingPredict] = useState(false);
    const [predictedResponse, setPredictedResponse] = useState({});
    const [error, setError] = useState("");
    const navigate = useNavigate();
    const { getHistory, updateHistory } = useHistory();
    const [emailHistory, setEmailHistory] = useState(null);

    useEffect(() => {
        const fetcher = async () => {
            try {
                const res = await fetch(`/api/mail`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${localStorage.getItem(
                            "access_token"
                        )}`,
                    },
                    body: JSON.stringify({ uid }),
                });

                if (!res.ok) {
                    throw new Error(`Failed to fetch mail: ${res.statusText}`);
                }

                const data = await res.json();
                if (!data) {
                    throw new Error("No data received");
                }

                setMail(data);
                setError(""); // Clear any previous errors
            } catch (err) {
                console.error("Error fetching mail:", err);
                setError(err.message || "Failed to load email");
                setMail(null);
            }
        };

        if (uid) {
            fetcher();
        }
    }, [uid]);
    useEffect(() => {
        if (mail && mail.body) {
            const bodyElement = bodyRef.current;
            if (bodyElement) {
                bodyElement.innerHTML = mail.body.replace(
                    /(?:\r\n|\r|\n)(?=[^\s])/g,
                    "<br>"
                );
            }
        }
    }, [mail]);
    function htmlToPlainText(html) {
        // Remove style, script, head, and meta tags
        let plainText = html
            .replace(/<style[^>]*>.*?<\/style>/gis, "")
            .replace(/<script[^>]*>.*?<\/script>/gis, "")
            .replace(/<head[^>]*>.*?<\/head>/gis, "")
            .replace(/<meta[^>]*>/gis, "")
            .replace(/<!DOCTYPE[^>]*>/gis, "");

        // Replace HTML tags with appropriate plain text equivalents
        plainText = plainText
            .replace(/<br\s*\/?>/gi, "\n")
            .replace(/<p[^>]*>/gi, "\n")
            .replace(/<div[^>]*>/gi, "\n")
            .replace(/<td[^>]*>/gi, " ")
            .replace(/<tr[^>]*>/gi, "\n")
            .replace(/<li[^>]*>/gi, "\n• ");

        // Remove all remaining HTML tags
        plainText = plainText.replace(/<[^>]+>/g, "");

        // Replace HTML entities
        plainText = plainText
            .replace(/&nbsp;/gi, " ")
            .replace(/&amp;/gi, "&")
            .replace(/&lt;/gi, "<")
            .replace(/&gt;/gi, ">")
            .replace(/&quot;/gi, '"')
            .replace(/&#39;/gi, "'");

        // Collapse multiple whitespace and trim
        plainText = plainText
            .replace(/\s+/g, " ")
            .replace(/\n\s+/g, "\n")
            .trim();

        return plainText;
    }
    const getreplayfromAi = async () => {
        setIsLoading(true);
        setError("");
        setResponse("");

        try {
            if (!mail || !mail.body) {
                throw new Error("No email content to process");
            }

            const plainTextBody = htmlToPlainText(mail.body);
            const senderEmail = mail.from.match(/<([^>]+)>/)?.[1] || mail.from;
            const history = getHistory(senderEmail);

            const res = await fetch("/api/response", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    data: plainTextBody,
                    email: senderEmail, // Add sender's email
                    history: {
                        previousIssues: history.issues,
                        previousReplies: history.replies,
                        lastInteraction: history.lastInteraction,
                    },
                }),
            });

            // Handle streaming response
            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            let accumulatedResponse = "";

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                const text = decoder.decode(value);
                accumulatedResponse += text;
                setResponse((prev) => prev + text);
            }

            if (accumulatedResponse) {
                updateHistory(senderEmail, {
                    issue: plainTextBody,
                    reply: accumulatedResponse,
                });
            }
        } catch (err) {
            console.error("Error generating response:", err);
            setError(
                err.message || "Error generating response. Please try again."
            );
            setResponse("");
        } finally {
            setIsLoading(false);
        }
    };
    const mailsendHandler = async () => {
        const to = mail.from.match(/<([^>]+)>/)[1]; // Extract email address using regex
        const formattedResponse = response
            .replace(/(?:\r\n|\r|\n)/g, "<br>") // Replace newlines with <br> for line breaks
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>"); // Replace **text** with <strong>text</strong>
        const res = await fetch("/api/send", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${localStorage.getItem("access_token")}`,
            },
            body: JSON.stringify({
                to: to,
                subject: `Re: ${mail.subject}`,
                body: formattedResponse,
            }),
        });
        if (res.ok) {
            const data = await res.json();
            console.log("Mail sent:", data);
            setResponse("");
            setPredictedResponse({});
            setMail(null);
            bodyRef.current.innerHTML = ""; // Clear the mail body
            navigate("/dashboard/inbox"); // Redirect to the home page
        } else {
            console.error("Error sending mail:", res.statusText);
        }
    };

    const getPredictedReplayfromAi = async () => {
        setIsLoadingPredict(true);
        const res = await fetch("/api/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                original_email: mail.body,
                our_response: response,
            }),
        });

        if (!res.body) return;

        const reader = res.body.getReader();
        const decoder = new TextDecoder("utf-8");

        let finalText = "";

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value);
            finalText += chunk;
            setPredictedResponse((prev) => prev + chunk); // stream it to UI
        }

        // Extract percentage using regex
        const match = finalText.match(/(\d{1,3})%/);
        const probability = match ? Math.min(parseInt(match[1]), 100) : 80;

        setPredictedResponse({
            reply: finalText.trim(),
            probability: probability,
        });

        setIsLoadingPredict(false);
    };

    useEffect(() => {
        if (mail?.from) {
            const senderEmail = mail.from.match(/<([^>]+)>/)?.[1] || mail.from;
            const history = getHistory(senderEmail);
            setEmailHistory(history);
        }
    }, [mail, getHistory]);

    return (
        <div className="px-6 py-4 gap-4 grid grid-rows-4 grid-cols-2 bg-secondary h-[90%]">
            {error && (
                <div className="col-span-2 bg-red-500/10 border border-red-500 text-red-500 p-4 rounded-lg">
                    {error}
                </div>
            )}
            <div className="border row-span-4  overflow-hidden overflow-y-scroll w-full p-6 rounded-lg shadow-lg mb-6">
                {mail ? (
                    <div className="mx-auto flex flex-col items-center gap-0">
                        <p className="text-white w-full text-left">
                            From: {mail.from}
                        </p>
                        <h2 className="text-2xl font-semibold text-white w-full text-left">
                            {mail.subject}
                        </h2>
                        <p
                            id="mailBody"
                            ref={bodyRef}
                            className="whitespace-pre-wrap text-white/80 w-full top-0"
                        ></p>
                    </div>
                ) : (
                    <p className="text-gray-500">{error || "Loading..."}</p>
                )}
            </div>
            <div className="p-6 flex items-start flex-col row-span-2 col-start-2 rounded-lg shadow-lg bg-primary">
                <h3 className="text-xl font-semibold text-gray-100 mb-4">
                    Reply
                </h3>

                <div className="w-full flex-1 flex flex-col gap-4">
                    {/* AI Reply Button */}
                    <button
                        disabled={isLoading || !mail}
                        onClick={() => {
                            startTransition(() => {
                                getreplayfromAi();
                            });
                        }}
                        className={`
                            w-full py-2.5 px-4 rounded-lg flex items-center justify-center gap-2
                            ${
                                isLoading
                                    ? "animate-pulse bg-gray-400"
                                    : "bg-blue-500 hover:bg-blue-600 active:bg-blue-700"
                            }
                            text-white font-medium transition-colors
                        `}
                    >
                        <BrainCog
                            className={isLoading ? "animate-spin" : ""}
                            size={20}
                        />
                        <span>
                            {isLoading ? "Generating..." : "Get AI Reply"}
                        </span>
                    </button>

                    {/* Error Display */}
                    {error && (
                        <div className="w-full p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                            <p className="text-red-500 text-sm">{error}</p>
                        </div>
                    )}

                    {/* Response Text Area */}
                    <div className="flex-1 w-full">
                        <textarea
                            value={response}
                            onChange={(e) => setResponse(e.target.value)}
                            disabled={isLoading}
                            placeholder={
                                isLoading
                                    ? "Generating response..."
                                    : "AI response will appear here..."
                            }
                            className={`
                                w-full h-full min-h-[200px] p-4 
                                bg-[#1E1E1E] text-white/90 
                                placeholder-[#666666]
                                border border-[#333333] 
                                rounded-lg resize-none
                                focus:outline-none focus:ring-2 
                                focus:ring-blue-500/40
                                disabled:opacity-50
                                ${isLoading ? "animate-pulse" : ""}
                            `}
                        ></textarea>
                    </div>

                    {/* Send Button */}
                    <button
                        onClick={mailsendHandler}
                        disabled={isPending || !response || !mail}
                        className={`
                            w-full py-2.5 px-4 rounded-lg
                            flex items-center justify-center gap-2
                            bg-gradient-to-r from-blue-500 via-blue-600 to-blue-700
                            hover:from-blue-600 hover:via-blue-700 hover:to-blue-800
                            text-white font-medium
                            disabled:opacity-50 disabled:cursor-not-allowed
                            disabled:bg-gray-400 disabled:hover:bg-gray-400
                            focus:outline-none focus:ring-2 focus:ring-blue-500/40
                            transition-all duration-200
                        `}
                    >
                        <Send size={18} />
                        <span>Send Reply</span>
                    </button>
                </div>
            </div>
            <div className="p-6 row-span-2 rounded-lg flex flex-col shadow-lg bg-primary h-full">
                <h3 className="text-xl font-semibold text-gray-100 mb-4">
                    Predicted Reply
                </h3>

                <div className="flex-1 overflow-hidden flex flex-col">
                    {!isLoadingPredict && !predictedResponse.reply && (
                        <div className="flex-1 p-4 bg-[#1E1E1E] text-white/60 border border-[#333333] rounded-lg">
                            No prediction generated yet...
                        </div>
                    )}

                    {isLoadingPredict ? (
                        <div className="flex-1 p-4 bg-[#1E1E1E] border border-[#333333] rounded-lg animate-pulse">
                            <p className="text-white flex items-center gap-2">
                                <BrainCog className="animate-spin" size={16} />
                                Thinking...
                            </p>
                        </div>
                    ) : (
                        predictedResponse.reply && (
                            <div className="flex-1 flex flex-col h-full">
                                <div className="mb-3 bg-blue-500/10 border border-blue-500/20 rounded-lg p-3">
                                    <div className="flex items-center gap-2">
                                        <span className="text-white/80">
                                            Probability:
                                        </span>
                                        <span className="text-blue-400 font-semibold">
                                            {predictedResponse.probability}%
                                        </span>
                                    </div>
                                </div>

                                <div className="flex-1 overflow-y-auto">
                                    <div className="p-4 bg-[#1E1E1E] text-white/90 border border-[#333333] rounded-lg">
                                        {predictedResponse.reply
                                            .split("\n")
                                            .map((paragraph, index) => (
                                                <p
                                                    key={index}
                                                    className="mb-3 last:mb-0 leading-relaxed"
                                                >
                                                    {paragraph
                                                        .split(/(\*\*.*?\*\*)/)
                                                        .map((part, i) =>
                                                            part.startsWith(
                                                                "**"
                                                            ) &&
                                                            part.endsWith(
                                                                "**"
                                                            ) ? (
                                                                <strong
                                                                    key={i}
                                                                    className="text-blue-400 font-medium"
                                                                >
                                                                    {part.slice(
                                                                        2,
                                                                        -2
                                                                    )}
                                                                </strong>
                                                            ) : (
                                                                part
                                                            )
                                                        )}
                                                </p>
                                            ))}
                                    </div>
                                </div>
                            </div>
                        )
                    )}

                    <button
                        disabled={
                            isLoadingPredict || !mail || !response.length > 0
                        }
                        onClick={() => {
                            startTransitionPredict(() => {
                                getPredictedReplayfromAi();
                            });
                        }}
                        className={`
              mt-4 w-full py-2.5 px-4 rounded-lg flex items-center justify-center gap-2
              ${
                  isLoadingPredict
                      ? "bg-gray-600 cursor-not-allowed"
                      : "bg-blue-500 hover:bg-blue-600 active:bg-blue-700"
              }
              disabled:opacity-50 disabled:cursor-not-allowed
              text-white font-medium transition-colors
            `}
                    >
                        <BrainCog
                            size={18}
                            className={isLoadingPredict ? "animate-spin" : ""}
                        />
                        <span>
                            {isLoadingPredict
                                ? "Generating Prediction..."
                                : "Get Predicted Reply"}
                        </span>
                    </button>
                </div>
            </div>
            {emailHistory && emailHistory.replies.length > 0 && (
                <div className="col-span-2 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg mb-4">
                    <h4 className="text-white font-medium mb-2">
                        Previous Interactions
                    </h4>
                    <p className="text-white/80 text-sm">
                        Last interaction:{" "}
                        {new Date(
                            emailHistory.lastInteraction
                        ).toLocaleDateString()}
                    </p>
                    <p className="text-white/80 text-sm">
                        Total interactions: {emailHistory.replies.length}
                    </p>
                </div>
            )}
        </div>
    );
}

export default ResponseMail;
