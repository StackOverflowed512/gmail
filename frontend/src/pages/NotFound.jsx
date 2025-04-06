import React from 'react'

function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--color-background)' }}>
      <div className="text-center p-8 rounded-lg" style={{ backgroundColor: 'var(--color-secondary)', boxShadow: 'var(--shadow)' }}>
        <h1 className="text-6xl font-bold mb-4" style={{ color: 'var(--color-text-primary)' }}>404</h1>
        <h2 className="text-2xl font-semibold mb-4" style={{ color: 'var(--color-text-secondary)' }}>Page Not Found</h2>
        <p className="mb-8" style={{ color: 'var(--color-text-secondary)' }}>
          The page you are looking for doesn't exist or has been moved.
        </p>
        <a 
          href="/"
          className="px-6 py-3 rounded-lg transition-colors duration-300"
          style={{ 
            backgroundColor: 'var(--color-primary)',
            color: 'var(--color-text-primary)',
            ':hover': {
              backgroundColor: 'var(--color-hover)'
            }
          }}
        >
          Go Back Home
        </a>
      </div>
    </div>
  )
}

export default NotFound