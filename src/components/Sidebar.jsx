import { useState, useEffect } from 'react'
import './Sidebar.css'

function Sidebar({ activeTab = 'Cover', onTabChange, collapsed, onToggleCollapse }) {
  const [showText, setShowText] = useState(!collapsed)
  const navItems = [
    { name: 'Cover', icon: '/aicover/assets/icon_cover.png' },
    { name: 'IP Pet', icon: '/aicover/assets/icon_ippet.png' },
    { name: 'Emoji', icon: '/aicover/assets/icon_emoji.png' }
  ]

  useEffect(() => {
    if (!collapsed) {
      const timer = setTimeout(() => {
        setShowText(true)
      }, 50)
      return () => clearTimeout(timer)
    } else {
      setShowText(false)
    }
  }, [collapsed])

  const handleTabClick = (name) => {
    if (onTabChange) {
      onTabChange(name)
    }
  }

  return (
    <div className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="header-section">
        <img src="/aicover/assets/webname.png" alt="D_DATA" className="logo" />
        <div className="header-actions">
          <img 
            src="/aicover/assets/icon_sidebar.png" 
            alt="sidebar" 
            className="header-icon" 
            onClick={onToggleCollapse}
          />
        </div>
      </div>
      
      <nav className="nav-menu">
        <div className="tab-group-title">TOOLS</div>
        <div className="tab-group">
          {navItems.map((item) => (
            <div
              key={item.name}
              className={`nav-item ${activeTab === item.name ? 'active' : ''}`}
              onClick={() => handleTabClick(item.name)}
            >
              <div className="icon-container">
                <img src={item.icon} alt={item.name} className="nav-icon" />
              </div>
              <span className={`text ${showText ? 'show' : ''}`}>{item.name}</span>
            </div>
          ))}
        </div>
      </nav>
      
      <div className="user-profile">
        <div className="avatar">
          <span className="avatar-text">i</span>
        </div>
        <span className="username">username</span>
        <div className="settings-icon-container">
          <svg className="settings-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06-.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
          </svg>
        </div>
      </div>
    </div>
  )
}

export default Sidebar