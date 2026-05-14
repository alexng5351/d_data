import './IPPetPage.css'
import Sidebar from './Sidebar'

function IPPetPage({ onTabChange, collapsed, onToggleCollapse }) {
  return (
    <div className="ip-pet-page">
      <Sidebar activeTab="IP Pet" onTabChange={onTabChange} collapsed={collapsed} onToggleCollapse={onToggleCollapse} />
      <div className="main-content">
        <div className="empty-state">
          <h1 className="page-title">IP Pet</h1>
          <p className="page-description">Coming soon...</p>
        </div>
      </div>
    </div>
  )
}

export default IPPetPage