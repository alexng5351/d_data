import { useState, useEffect } from 'react'
import './EditTemplateModal.css'

function EditTemplateModal({ template, isOpen, onClose, onSave }) {
  const [templateId, setTemplateId] = useState('')
  const [name, setName] = useState('')
  const [createdAt, setCreatedAt] = useState('')
  const [json, setJson] = useState('')

  useEffect(() => {
    if (template) {
      setTemplateId(template.templateId || '')
      setName(template.name || '')
      setCreatedAt(template.addedAt || '')
      setJson('')
    }
  }, [template])

  const handleSave = () => {
    if (onSave) {
      onSave({
        ...template,
        templateId,
        name,
        addedAt: createdAt
      })
    }
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="edit-template-modal-overlay">
      <div className="edit-template-modal">
        <div className="edit-template-modal-header">
          <div className="edit-template-modal-title">Style Info</div>
          <div className="edit-template-modal-close" onClick={onClose}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M4 4L12 12M4 12L12 4" stroke="white" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
          </div>
        </div>

        <div className="edit-template-modal-body">
          <div className="edit-template-field">
            <label className="edit-template-label">
              Template_ID <span className="edit-template-required">*</span>
            </label>
            <input
              type="text"
              className="edit-template-input"
              value={templateId}
              onChange={(e) => setTemplateId(e.target.value)}
            />
          </div>

          <div className="edit-template-field">
            <label className="edit-template-label">
              Name <span className="edit-template-required">*</span>
            </label>
            <input
              type="text"
              className="edit-template-input"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          <div className="edit-template-field">
            <label className="edit-template-label">Created_at</label>
            <input
              type="text"
              className="edit-template-input"
              value={createdAt}
              onChange={(e) => setCreatedAt(e.target.value)}
            />
          </div>

          <div className="edit-template-field">
            <label className="edit-template-label">Json</label>
            <textarea
              className="edit-template-textarea"
              value={json}
              onChange={(e) => setJson(e.target.value)}
              rows="4"
            />
          </div>
        </div>

        <div className="edit-template-modal-buttons">
          <button
            className="edit-template-modal-button edit-template-modal-button-save"
            onClick={handleSave}
          >
            Save
          </button>
        </div>
      </div>
    </div>
  )
}

export default EditTemplateModal
