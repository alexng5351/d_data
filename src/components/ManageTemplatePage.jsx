import { useState } from 'react'
import './ManageTemplatePage.css'
import Sidebar from './Sidebar'
import ManageTemplateCard from './ManageTemplateCard'
import EditTemplateModal from './EditTemplateModal'

function ManageTemplatePage({ onBack, onTabChange, collapsed, onToggleCollapse }) {
  const tabs = ['All', 'Single Image', 'Multiple Images', 'Shared Records', 'Tutorial Post', 'Community Discussion', 'Other']
  const [activeTabIndex, setActiveTabIndex] = useState(0)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState(null)
  
  const templateNames = ['Minimal Modern', 'Cozy Aesthetic', 'Clean Editorial', 'Dark Elegance', 'Bright Pop', 'Retro Vibe', 'Minimalist Chic', 'Urban Style']
  const defaultTags = ['Extrinsic', 'Record', 'Products', 'Help and Interaction', 'Other']

  const handleEdit = (template) => {
    setEditingTemplate(template)
    setShowEditModal(true)
  }

  const handleDelete = (id) => {
    console.log('Delete template:', id)
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
          {[9, 10, 11, 12, 13, 14, 15, 16].map((id, index) => (
            <ManageTemplateCard
              key={id}
              id={id}
              name={templateNames[index]}
              tags={defaultTags}
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
    </div>
  )
}

export default ManageTemplatePage
