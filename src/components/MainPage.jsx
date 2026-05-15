import { useState } from 'react'
import './MainPage.css'
import Sidebar from './Sidebar'
import CoverCard from './CoverCard'

function MainPage({ onCoverClick, onTabChange, collapsed, onToggleCollapse, userTemplates, onAddClick, onManageTemplateClick }) {
  const tabs = ['All', 'Single Image', 'Multiple Images', 'Shared Records', 'Tutorial Post', 'Community Discussion', 'Other']
  const [activeTabIndex, setActiveTabIndex] = useState(0)
  
  const defaultCoverIds = [1, 2, 3, 4, 5, 6, 7, 8]
  const allTemplates = [
    ...userTemplates,
    ...defaultCoverIds.map(id => ({
      id,
      isDefault: true
    }))
  ]

  return (
    <div className="main-page">
      <Sidebar activeTab="Cover" onTabChange={onTabChange} collapsed={collapsed} onToggleCollapse={onToggleCollapse} />
      
      <div className="main-content">
        <div className="top-bar">
          <h1 className="page-title">AI Cover</h1>
          <div className="top-actions">
            <button className="manage-template-btn" onClick={onManageTemplateClick}>Manage Template</button>
            <button className="add-btn" onClick={onAddClick}>
              <img src="/aicover/assets/icon_add.png" alt="Add" className="add-icon" />
            </button>
          </div>
        </div>
        
        <div className="tabs-bar">
          {tabs.map((tab, index) => (
            <button
              key={index}
              className={`tab-item ${index === activeTabIndex ? 'active' : ''}`}
              onClick={() => setActiveTabIndex(index)}
            >
              {tab}
            </button>
          ))}
        </div>
        
        <div className="covers-grid">
          {allTemplates.map((template) => (
            <CoverCard
              key={template.id}
              id={template.id}
              images={template.images}
              onClick={() => onCoverClick(template.id)}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

export default MainPage
