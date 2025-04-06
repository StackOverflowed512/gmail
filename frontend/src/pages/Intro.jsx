import { useGSAP } from '@gsap/react'
import gsap from 'gsap'
import React, { useRef } from 'react'
import { useNavigate } from 'react-router'

function Intro() {
  const navigate = useNavigate()
  const intropageRef = useRef(null);
  useGSAP(() => {
    gsap.from(intropageRef.current, {
      duration: 3,
      opacity: 0,
    })
  })
  return (
    <div
      onClick={() => {
        gsap.to(intropageRef.current, {
          duration: 0.5,
          opacity: 0,
          onComplete: () => {
            navigate('/login')
          },
        })
      }}
      className="min-h-screen cursor-pointer w-full flex items-center justify-center"
      id="introPage"
    >
      <div
        ref={intropageRef}
        className="max-w-2xl mx-auto p-8 text-center">
        <div className="text-4xl font-bold text-text-primary mb-6">
          Welcome to Email Client
        </div>
        <div className="text-lg text-text-primary/80 mb-8">
          Empower your email communication effortlessly generate, edit, and send smart responses with our AI-powered email assistant.
        </div>
        <div className="w-full flex items-center justify-center">
          <img
            src="/img1.png"
            alt="Email Icon"
            className="mx-auto w-48 h-48 animate-[spin_10s_linear_infinite] object-contain"
          />
        </div>
        <div className="text-sm text-gray-500 animate-pulse">
          Click anywhere to continue...
        </div>
      </div>
      <div className="bg-conic animate-[spin_20s_linear_infinite] scale-250 from-primary to-secondary h-screen w-screen top-o left-0 fixed -z-1 ">
      </div>
    </div>
  )
}

export default Intro