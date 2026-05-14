import { useState } from 'react'
import './AddTemplatePage.css'
import Sidebar from './Sidebar'

function AddTemplatePage({ onBack, onTabChange, collapsed, onToggleCollapse, onSaveTemplate }) {
  const [coverImages, setCoverImages] = useState([null, null, null])
  const [prompt, setPrompt] = useState('')
  const [json, setJson] = useState('')
  const [hasInput, setHasInput] = useState(false)

  const checkHasInput = (covers, promptText, jsonText) => {
    const hasCovers = covers.some(img => img !== null)
    const hasPrompt = promptText.trim() !== ''
    const hasJson = jsonText.trim() !== ''
    setHasInput(hasCovers || hasPrompt || hasJson)
  }

  const handleImageUpload = (index, e) => {
    const file = e.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (event) => {
        const newCovers = [...coverImages]
        newCovers[index] = event.target.result
        setCoverImages(newCovers)
        checkHasInput(newCovers, prompt, json)
      }
      reader.readAsDataURL(file)
    }
  }

  const handlePromptChange = (e) => {
    setPrompt(e.target.value)
    checkHasInput(coverImages, e.target.value, json)
  }

  const handleJsonChange = (e) => {
    setJson(e.target.value)
    checkHasInput(coverImages, prompt, e.target.value)
  }

  const handleSave = () => {
    if (hasInput) {
      const newTemplate = {
        id: Date.now(),
        images: coverImages.filter(img => img !== null),
        prompt: prompt,
        json: json
      }
      onSaveTemplate(newTemplate)
    }
  }

  return (
    <div className="add-template-page">
      <Sidebar activeTab="Cover" onTabChange={onTabChange} collapsed={collapsed} onToggleCollapse={onToggleCollapse} />
      <div className="main-content">
        <div className="back-button" onClick={onBack}>
          <span>&lt; Back to AI Cover</span>
        </div>
        <h1 className="page-title">Create a new template</h1>
        <div className="form-container">
          <div className="section">
            <h2 className="section-title">Choose Cover</h2>
            <div className="cover-grid">
              {coverImages.map((img, index) => (
                <div key={index} className="cover-placeholder" onClick={() => document.getElementById(`cover-upload-${index}`).click()}>
                  {img ? (
                    <img src={img} alt={`Cover ${index + 1}`} className="cover-preview" />
                  ) : (
                    <div className="upload-icon-container">
                      <img src="/assets/icon_addimages.png" alt="Add" className="upload-icon" />
                    </div>
                  )}
                  <input
                    id={`cover-upload-${index}`}
                    type="file"
                    accept="image/*"
                    style={{ display: 'none' }}
                    onChange={(e) => handleImageUpload(index, e)}
                  />
                </div>
              ))}
            </div>
          </div>
          <div className="section">
            <div className="section-header">
              <h2 className="section-title">Prompt</h2>
              <button className="verify-button">Verify legality</button>
            </div>
            <textarea
              className="prompt-input"
              value={prompt}
              onChange={handlePromptChange}
              placeholder="Enter your prompt here..."
            />
          </div>
          <div className="section">
            <h2 className="section-title">Json</h2>
            <textarea
              className="json-input"
              value={json}
              onChange={handleJsonChange}
              placeholder='{"key": "value"}'
            />
          </div>
          <button
            className={`save-button ${hasInput ? 'active' : ''}`}
            onClick={handleSave}
            disabled={!hasInput}
          >
            Save
          </button>
        </div>
      </div>
    </div>
  )
}

export default AddTemplatePage
