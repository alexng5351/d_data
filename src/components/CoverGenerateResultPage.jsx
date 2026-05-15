import { useState } from 'react'
import './CoverGenerateResultPage.css'
import Sidebar from './Sidebar'

function CoverGenerateResultPage({ onBack, onRegenerate, images, onTabChange, collapsed, onToggleCollapse, onDeleteResult }) {
  const [menuOpen, setMenuOpen] = useState(null)
  const [localImages, setLocalImages] = useState(images.map((img, index) => ({
    id: Date.now() + index,
    image: img,
    addedAt: new Date().toLocaleString(),
    resultId: `202605061012568660${index}`,
    aiMode: 'Seedream 4.5(ModelHub)'
  })))

  const handleDownload = (imageUrl, fileName = 'cover-image.png') => {
    const link = document.createElement('a')
    link.href = imageUrl
    link.download = fileName
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    setMenuOpen(null)
  }

  const handleDelete = (index) => {
    setLocalImages(prev => {
      const newList = [...prev]
      newList.splice(index, 1)
      return newList
    })
    setMenuOpen(null)
    if (onDeleteResult) {
      onDeleteResult(index)
    }
  }

  return (
    <div className="cover-result-page">
      <Sidebar activeTab="Cover" onTabChange={onTabChange} collapsed={collapsed} onToggleCollapse={onToggleCollapse} />

      <div className="main-content">
        <div className="back-button" onClick={onBack}>
          <span className="back-icon">←</span>
          <span>Back to AI Cover</span>
        </div>

        <div className="page-header">
          <h1>Create your Cover</h1>
        </div>

        <div className="content-wrapper">
          <div className="left-panel">
            <div className="panel-header">
              <h2>Generated Covers</h2>
            </div>

            <div className="template-display">
              <div className="selected-template">
                <div className="template-preview">
                  <img src={localImages[0]?.image || images[0]} alt="Template" />
                </div>
              </div>
            </div>

            <div className="upload-section">
              <h3>Uploaded Images</h3>
              <p className="upload-hint">Please select template images to use for generating style prompts (up to 9 images)</p>
              
              <div className="upload-grid">
                <div className="upload-item large">
                  <div className="upload-placeholder">
                    <span className="upload-icon">📷</span>
                  </div>
                </div>
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="upload-item small">
                    <div className="upload-placeholder mini">
                      <span className="upload-icon">➕</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <button className="generate-button" onClick={onRegenerate}>
              <span>Regenerate</span>
              <span className="ai-icon">🤖</span>
            </button>
          </div>

          <div className="right-panel">
            <div className="results-grid">
              {localImages.map((result, index) => (
                <div key={result.id} className="result-card">
                  <div className="result-image">
                    <img src={result.image} alt={`Generated ${index + 1}`} />
                  </div>
                  <div className="result-info">
                    <p>Added At: {result.addedAt}</p>
                    <p>ID: {result.resultId}</p>
                    <p>{result.aiMode}</p>
                  </div>
                  <div className="menu-container">
                    <button
                      className="menu-button"
                      onClick={() => setMenuOpen(menuOpen === index ? null : index)}
                    >
                      ⋮
                    </button>
                    {menuOpen === index && (
                      <div className="card-menu">
                        <div className="menu-item">
                          <button 
                            className="menu-item-button"
                            onClick={() => handleDownload(result.image, `cover-result-${result.resultId}.png`)}
                          >
                            Download
                          </button>
                        </div>
                        <div className="menu-item">
                          <button 
                            className="menu-item-button"
                            onClick={() => handleDelete(index)}
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CoverGenerateResultPage