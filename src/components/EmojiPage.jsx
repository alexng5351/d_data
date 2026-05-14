import './EmojiPage.css'
import Sidebar from './Sidebar'

function EmojiPage({ onTabChange, collapsed, onToggleCollapse }) {
  return (
    <div className="emoji-page">
      <Sidebar activeTab="Emoji" onTabChange={onTabChange} collapsed={collapsed} onToggleCollapse={onToggleCollapse} />
      <div className="main-content">
        <div className="empty-state">
          <h1 className="page-title">Emoji</h1>
          <p className="page-description">Coming soon...</p>
        </div>
      </div>
    </div>
  )
}

export default EmojiPage