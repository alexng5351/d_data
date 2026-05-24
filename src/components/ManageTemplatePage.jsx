import { useState } from 'react'
import './ManageTemplatePage.css'
import Sidebar from './Sidebar'
import ManageTemplateCard from './ManageTemplateCard'
import EditTemplateModal from './EditTemplateModal'
import { getCoverImages } from './MainPage'

function ManageTemplatePage({ onBack, onTabChange, collapsed, onToggleCollapse, userTemplates = [], onDeleteTemplate }) {
  const tabs = ['All', 'Single Image', 'Multiple Images', 'Shared Records', 'Tutorial Post', 'Community Discussion', 'Other']
  const [activeTabIndex, setActiveTabIndex] = useState(0)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState(null)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [deletingTemplateId, setDeletingTemplateId] = useState(null)
  
  const templateNames = [
    'Instagram Style', 'Rednote Design', 'Youtube Banner', 'Pinterest Layout', 'VSCO Aesthetic',
    'Minimal Modern', 'Cozy Aesthetic', 'Clean Editorial', 'Dark Elegance', 'Bright Pop',
    'Retro Vibe', 'Minimalist Chic', 'Urban Style', 'Artistic Flair', 'Elegant Design',
    'Creative Layout', 'Modern Minimal', 'Bold Colors', 'Soft Pastel', 'Geometric Style'
  ]
  
  const allTags = ['Single Image', 'Multiple Images', 'Shared Records', 'Tutorial Post', 'Community Discussion', 'Other']
  
  // 随机选择3个标签
  const getRandomTags = () => {
    const shuffled = [...allTags].sort(() => Math.random() - 0.5)
    return shuffled.slice(0, 3)
  }
  
  const defaultTemplates = Array.from({ length: 20 }, (_, i) => {
    const id = i + 1
    return {
      id,
      name: templateNames[i],
      addedAt: '2026-05-06 18:13:04',
      templateId: `2026050610125686${String(i).padStart(3, '0')}`,
      tags: getRandomTags(),
      images: getCoverImages(id)
    }
  })

  const allTemplates = [...userTemplates, ...defaultTemplates]

  const filteredTemplates = activeTabIndex === 0 
    ? allTemplates 
    : allTemplates.filter(template => template.tags && template.tags.includes(tabs[activeTabIndex]))

  const handleEdit = (template) => {
    setEditingTemplate(template)
    setShowEditModal(true)
  }

  const handleDelete = (id) => {
    console.log('handleDelete called with id:', id)
    console.log('userTemplates:', userTemplates)
    // 暂时移除限制，让所有模板都可以删除来测试
    setDeletingTemplateId(id)
    setShowDeleteModal(true)
  }

  const confirmDelete = () => {
    if (deletingTemplateId !== null && onDeleteTemplate) {
      onDeleteTemplate(deletingTemplateId)
    }
    setShowDeleteModal(false)
    setDeletingTemplateId(null)
  }

  const cancelDelete = () => {
    setShowDeleteModal(false)
    setDeletingTemplateId(null)
  }

  const handleSaveTemplate = (template) => {
    console.log('Save template:', template)
  }

  return (
    <div className="manage-template-page">
      <Sidebar activeTab="Cover" onTabChange={onTabChange} collapsed={collapsed} onToggleCollapse={onToggleCollapse} />
      
      <div className="mtp-main-content">
        <div className="mtp-back-button" onClick={onBack}>
          <span>&lt; Back to AI Cover</span>
        </div>
        <h1 className="mtp-page-title">Manage Template</h1>
        
        <div className="mtp-tabs-bar">
          {tabs.map((tab, index) => (
            <button
              key={index}
              className={`mtp-tab-item ${index === activeTabIndex ? 'active' : ''}`}
              onClick={() => setActiveTabIndex(index)}
            >
              {tab}
            </button>
          ))}
        </div>
        
        <div className="mtp-covers-grid">
          {filteredTemplates.map((template, index) => (
            <ManageTemplateCard
              key={template.id}
              id={template.id}
              name={template.name}
              addedAt={template.addedAt}
              templateId={template.templateId}
              tags={template.tags}
              images={template.images}
              onEdit={handleEdit}
              onDelete={handleDelete}
            />
          ))}
        </div>
      </div>

      <EditTemplateModal
        template={editingTemplate}
        isOpen={showEditModal}
        onClose={() => setShowEditModal(false)}
        onSave={handleSaveTemplate}
      />

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="cover-input-exit-modal-overlay" onClick={cancelDelete}>
          <div className="cover-input-exit-modal" onClick={(e) => e.stopPropagation()}>
            <div className="cover-input-exit-modal-header">
              <div className="cover-input-exit-modal-title">Delete this template?</div>
              <div className="cover-input-exit-modal-close" onClick={cancelDelete}>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M4 4L12 12M4 12L12 4" stroke="white" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </div>
            </div>
            <div className="cover-input-exit-modal-body">
              <div className="cover-input-exit-modal-message">
                This template will be permanently deleted and cannot be recovered.
              </div>
            </div>
            <div className="cover-input-exit-modal-buttons">
              <button 
                className="cover-input-exit-modal-button cover-input-exit-modal-button-exit"
                onClick={confirmDelete}
              >
                Delete
              </button>
              <button 
                className="cover-input-exit-modal-button cover-input-exit-modal-button-cancel"
                onClick={cancelDelete}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ManageTemplatePage
