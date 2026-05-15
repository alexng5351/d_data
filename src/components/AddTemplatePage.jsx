import { useState, useEffect } from 'react'
import './AddTemplatePage.css'
import Sidebar from './Sidebar'

function AddTemplatePage({ onBack, onTabChange, collapsed, onToggleCollapse, onSaveTemplate }) {
  const [coverImages, setCoverImages] = useState([null, null, null])
  const [templateName, setTemplateName] = useState('')
  const [prompt, setPrompt] = useState('')
  const [json, setJson] = useState('')
  const [tags, setTags] = useState([])
  const [hasInput, setHasInput] = useState(false)
  const [showCustomTagInput, setShowCustomTagInput] = useState(false)
  const [customTagInput, setCustomTagInput] = useState('')

  const [customTags, setCustomTags] = useState([])

  const tagOptions = [
    'Single Image',
    'Multiple Images',
    'Shared Records',
    'Tutorial Post',
    'Community Discussion',
    'Other'
  ]

  const allTagOptions = [...tagOptions, ...customTags]

  const checkHasInput = (covers, nameText, promptText, jsonText, currentTags) => {
    const hasCovers = covers.some(img => img !== null)
    const hasName = nameText.trim() !== ''
    const hasJson = jsonText.trim() !== ''
    const hasTags = currentTags.length > 0
    setHasInput(hasCovers && hasName && hasJson && hasTags)
  }

  useEffect(() => {
    checkHasInput(coverImages, templateName, prompt, json, tags)
  }, [coverImages, templateName, prompt, json, tags])

  const handleTagToggle = (tag) => {
    if (tags.includes(tag)) {
      setTags(tags.filter(t => t !== tag))
    } else {
      setTags([...tags, tag])
    }
  }

  const handleAddCustomTag = () => {
    if (customTagInput.trim() !== '' && !allTagOptions.includes(customTagInput.trim())) {
      setCustomTags([...customTags, customTagInput.trim()])
      setTags([...tags, customTagInput.trim()])
      setCustomTagInput('')
      setShowCustomTagInput(false)
    }
  }

  const handleCustomTagKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleAddCustomTag()
    } else if (e.key === 'Escape') {
      setShowCustomTagInput(false)
      setCustomTagInput('')
    }
  }

  const handleImageUpload = (index, e) => {
    const file = e.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (event) => {
        const newCovers = [...coverImages]
        newCovers[index] = event.target.result
        setCoverImages(newCovers)
      }
      reader.readAsDataURL(file)
    }
  }

  const handlePromptChange = (e) => {
    setPrompt(e.target.value)
  }

  const handleJsonChange = (e) => {
    setJson(e.target.value)
  }

  const handleSave = () => {
    const hasCovers = coverImages.some(img => img !== null)
    const hasName = templateName.trim() !== ''
    const hasJson = json.trim() !== ''
    const hasTags = tags.length > 0
    
    if (hasCovers && hasName && hasJson && hasTags) {
      const newTemplate = {
        id: Date.now(),
        images: coverImages.filter(img => img !== null),
        name: templateName,
        prompt: prompt,
        json: json,
        tags: tags
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
            <h2 className="section-title">Choose Cover<span className="required">*</span></h2>
            <div className="cover-grid">
              {coverImages.map((img, index) => (
                <div key={index} className="cover-placeholder" onClick={() => document.getElementById(`cover-upload-${index}`).click()}>
                  {img ? (
                    <img src={img} alt={`Cover ${index + 1}`} className="cover-preview" />
                  ) : (
                    <div className="upload-icon-container">
                      <img src="/aicover/assets/icon_addimages.png" alt="Add" className="upload-icon" />
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
              <h2 className="section-title">Template Name<span className="required">*</span></h2>
            </div>
            <input
              className="template-name-input"
              value={templateName}
              onChange={(e) => setTemplateName(e.target.value)}
              placeholder="Enter template name..."
            />
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
            <h2 className="section-title">Json<span className="required">*</span></h2>
            <textarea
              className="json-input"
              value={json}
              onChange={handleJsonChange}
              placeholder='{"key": "value"}'
            />
          </div>
          <div className="section">
            <h2 className="section-title">Category Tags<span className="required">*</span></h2>
            <div className="tags-container">
              {allTagOptions.map((tag, index) => (
                <button
                  key={index}
                  className={`tag-button ${tags.includes(tag) ? 'active' : ''}`}
                  onClick={() => handleTagToggle(tag)}
                >
                  {tag}
                </button>
              ))}
              {!showCustomTagInput ? (
                <button
                  className="tag-button add-tag-button"
                  onClick={() => setShowCustomTagInput(true)}
                >
                  +
                </button>
              ) : (
                <input
                  className="custom-tag-input"
                  value={customTagInput}
                  onChange={(e) => setCustomTagInput(e.target.value)}
                  onKeyDown={handleCustomTagKeyDown}
                  onBlur={handleAddCustomTag}
                  placeholder="Enter tag..."
                  autoFocus
                />
              )}
            </div>
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
