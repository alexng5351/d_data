import { useState, useEffect } from 'react'
import './CoverGeneratePage.css'
import Sidebar from './Sidebar'

function CoverGeneratePage({ onBack, onGenerateComplete, isRegenerating, previousImages, onTabChange, collapsed, onToggleCollapse }) {
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState('Initializing...')

  const statusMessages = [
    'Initializing...',
    'Analyzing template style...',
    'Processing your image...',
    'Generating first cover...',
    'Generating second cover...',
    'Generating third cover...',
    'Finalizing...',
    'Complete!'
  ]

  useEffect(() => {
    let currentStep = 0
    const interval = setInterval(() => {
      if (currentStep < statusMessages.length) {
        setStatus(statusMessages[currentStep])
        setProgress(((currentStep + 1) / statusMessages.length) * 100)
        currentStep++
      } else {
        clearInterval(interval)
        setTimeout(() => {
          const generatedImages = [
            'https://copilot-cn.bytedance.net/api/ide/v1/text_to_image?prompt=beautiful%20anime%20portrait%20art%20style&image_size=landscape_4_3',
            'https://copilot-cn.bytedance.net/api/ide/v1/text_to_image?prompt=cyberpunk%20neon%20portrait%20futuristic&image_size=landscape_4_3',
            'https://copilot-cn.bytedance.net/api/ide/v1/text_to_image?prompt=classical%20oil%20painting%20portrait%20masterpiece&image_size=landscape_4_3'
          ]
          onGenerateComplete(generatedImages)
        }, 500)
      }
    }, 800)

    return () => clearInterval(interval)
  }, [onGenerateComplete])

  return (
    <div className="cover-generate-page">
      <Sidebar activeTab="Cover" onTabChange={onTabChange} collapsed={collapsed} onToggleCollapse={onToggleCollapse} />

      <div className="main-content">
        <div className="back-button" onClick={onBack}>
          <span className="back-icon">←</span>
          <span>Back to AI Cover</span>
        </div>

        <div className="page-header">
          <h1>Generating Your Covers...</h1>
        </div>

        {isRegenerating && previousImages.length > 0 && (
          <div className="previous-images-section">
            <h3>Previous Results</h3>
            <div className="previous-images-grid">
              {previousImages.map((img, idx) => (
                <div key={idx} className="previous-image-card">
                  <img src={img} alt={`Previous ${idx + 1}`} />
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="generate-container">
          <div className="animation-container">
            <div className="spinner">
              <div className="spinner-ring"></div>
              <div className="spinner-ring"></div>
              <div className="spinner-ring"></div>
              <div className="spinner-center">🤖</div>
            </div>
          </div>

          <div className="status-section">
            <p className="status-text">{status}</p>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${progress}%` }}></div>
            </div>
            <p className="progress-percentage">{Math.round(progress)}%</p>
          </div>

          <div className="preview-container">
            <div className="preview-card generating">
              <div className="shimmer"></div>
            </div>
            <div className="preview-card generating">
              <div className="shimmer"></div>
            </div>
            <div className="preview-card generating">
              <div className="shimmer"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CoverGeneratePage