import React, { useEffect, useRef, useState } from "react";
import { data, useNavigate, useParams } from "react-router";
import { BrainCog, Send } from "lucide-react";
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
  const navigate = useNavigate();
  useEffect(() => {
    const fetcher = async () => {
      const res = await fetch(`/api/mail`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({ uid }),
      });
      if (res.ok) {
        const data = await res.json();
        console.log("Fetched mail:", data);
        setMail(data);
      } else {
        console.error("Error fetching mail:", res.statusText);
      }
    };
    fetcher();
  }, [uid]);
  useEffect(() => {
    if (mail && mail.body) {
      const bodyElement = bodyRef.current;
      if (bodyElement) {
        bodyElement.innerHTML = mail.body.replace(/(?:\r\n|\r|\n)/g, "<br>");
      }
    }
  }, [mail]);

  const getreplayfromAi = async () => {
    setIsLoading(true);
    setResponse("thinking...");
    const res = await fetch("/api/response", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ data: mail.body }),
    });
    if (res.ok) {
      const data = await res.json();
      console.log("AI response:", data.response);
      setIsLoading(false);
      setResponse(data.response);
      console.log("AI response:", data.response);
    } else {
      console.error("Error generating response:", res.statusText);
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
    if (res.ok) {
      const data = await res.json();
      console.log("AI response:", data.predicted_reply);
      setPredictedResponse({
        reply: data.predicted_reply.trim(),
        probability: data.reply_probability,
      });
      setIsLoadingPredict(false);
    } else {
      console.error("Error generating response:", response.statusText);
    }
  };
  return (
    <div className="px-6 py-4 gap-4 grid grid-rows-4 grid-cols-2 bg-secondary min-h-screen max-h-screen">
      <div className="border row-span-4  overflow-hidden overflow-y-scroll p-6 rounded-lg shadow-lg mb-6">
        {mail ? (
          <div>
            <p className="text-white">From: {mail.from}</p>
            <h2 className="text-2xl font-semibold text-white mb-4">
              {mail.subject}
            </h2>
            <p
              id="mailBody"
              ref={bodyRef}
              className="whitespace-pre-wrap text-white/80 leading-relaxed"
            ></p>
          </div>
        ) : (
          <p className="text-gray-500">Loading...</p>
        )}
      </div>
      <div className="p-6 flex items-start flex-col row-span-2 col-start-2 rounded-lg shadow-lg bg-primary">
        <h3 className="text-xl font-semibold text-gray-100 mb-4">Reply</h3>
        <textarea
          value={response}
          name="message"
          onChange={(e) => setResponse(e.target.value)}
          placeholder="response email..."
          className={`w-full h-full resize-none  p-4 bg-[#1E1E1E] text-white placeholder-[#B3B3B3] border border-[#333333] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#4A4A4A] transition-colors ${
            isLoading ? "animate-pulse" : ""
          }`}
        ></textarea>
        <div className="flex space-x-4 mt-4">
          <button
            disabled={isLoading}
            onClick={() => {
              startTransition(() => {
                getreplayfromAi();
              });
            }}
            className={` ${
              isLoading ? "animate-pulse" : ""
            } text-white flex items-center disabled:bg-accent  cursor-pointer justify-center  h-fit py-2 px-2 bg-blue-400 rounded-md `}
          >
            <BrainCog />
            <span className={`ml-2`}>
              {isLoading ? "thinking..." : "Get Replay from AI"}
            </span>
          </button>
          <button></button>
          <button
            onClick={mailsendHandler}
            disabled={isPending}
            className="px-4 h-fit py-2 cursor-pointer flex items-center gap-2 bg-gradient-to-r from-blue-500 via-blue-600 to-blue-700 text-white font-medium rounded-lg hover:from-blue-600 hover:via-blue-700 hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <Send size={18} />
            Send
          </button>
        </div>
      </div>
      <div className="p-6 row-span-2 rounded-lg flex flex-col shadow-lg bg-primary">
        <h3 className="text-xl font-semibold text-gray-100 mb-4">
          Predect Replay
        </h3>
        {!isLoadingPredict && !predictedResponse.reply && (
          <div className="resize-none p-4 h-full bg-[#1E1E1E] text-white placeholder-[#B3B3B3] border border-[#333333] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#4A4A4A] transition-colors"></div>
        )}
        {isLoadingPredict ? (
          <div className="resize-none p-4 bg-[#1E1E1E] text-white placeholder-[#B3B3B3] border border-[#333333] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#4A4A4A] transition-colors">
            <p className="text-white">thinking...</p>
          </div>
        ) : (
          predictedResponse.reply && (
            <div className="w-full overflow-y-auto h-full">
              <p className="text-white mb-2 flex items-center gap-2 bg-blue-300 rounded-lg p-2">
                <span className="text-white">Probability: </span>
                <span className="text-white">
                  {predictedResponse.probability}%
                </span>
              </p>
              <div className="resize-none p-4 bg-[#1E1E1E] text-white placeholder-[#B3B3B3] border border-[#333333] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#4A4A4A] transition-colors">
                {predictedResponse.reply
                  .split("\n") // Split the response into paragraphs by newline
                  .map((paragraph, index) => (
                    <p key={index} className="mb-4">
                      {paragraph
                        .split(/(\*\*.*?\*\*)/) // Split by bold markers (**)
                        .map((part, i) =>
                          part.startsWith("**") && part.endsWith("**") ? (
                            <strong key={i} className="text-blue-400">
                              {part.slice(2, -2)} {/* Remove the ** markers */}
                            </strong>
                          ) : (
                            part
                          )
                        )}
                    </p>
                  ))}
              </div>
            </div>
          )
        )}
        <div className="flex flex-col space-x-4 mt-4">
          <button
            onClick={() => {
              startTransitionPredict(() => {
                getPredictedReplayfromAi();
              });
            }}
            className={` ${
              isLoadingPredict ? "animate-pulse" : ""
            } text-white flex items-center disabled:bg-accent  cursor-pointer justify-center  h-fit py-2 px-2 bg-blue-400 rounded-md `}
          >
            <BrainCog />
            <span className="ml-2">
              {isLoadingPredict
                ? "thinking..."
                : "Get Predicted Replay from AI"}
            </span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default ResponseMail;
