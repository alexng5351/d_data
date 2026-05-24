import './IPPetPage.css'
import { getAssetPath } from '../utils'
import Sidebar from './Sidebar'

function IPPetPage({ onTabChange, collapsed, onToggleCollapse }) {
  return (
    <div className="ip-pet-page">
      <Sidebar activeTab="IP Pet" onTabChange={onTabChange} collapsed={collapsed} onToggleCollapse={onToggleCollapse} />
      <div className="main-content">
        <div className="empty-state">
          <img src={getAssetPath("assets/illustration_inprocess.png")} alt="In process" className="in-process-illustration" />
          <p className="coming-soon-text">Hatching Soon</p>
        </div>
      </div>
    </div>
  )
}

export default IPPetPage