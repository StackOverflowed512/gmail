import React, { useEffect, useRef, useState } from "react";
import { useParams } from "react-router";

function MailViewer() {
  const { uid } = useParams();
  const [mail, setMail] = useState();
  const bodyRef = useRef(null);

  useEffect(() => {
    const fetcher = async () => {
      const res = await fetch(`/api/sent_mail`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({ uid }),
      });
      if (res.ok) {
        const data = await res.json();
        setMail(data[0]);
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

  return (
    <div className="p-6 bg-secondary min-h-screen max-h-screen">
      <div className="border overflow-hidden overflow-y-scroll p-6 rounded-lg shadow-lg">
        {mail ? (
          <div>
            <p className="text-white">From: {mail.to}</p>
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
    </div>
  );
}

export default MailViewer;
