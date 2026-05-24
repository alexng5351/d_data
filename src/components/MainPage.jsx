import { useState, useEffect } from 'react'
import './MainPage.css'
import Sidebar from './Sidebar'
import CoverCard from './CoverCard'

// 封面素材信息映射
export const getCoverInfo = (id) => {
  const coverData = {
    1: { count: 3, extensions: ['png', 'png', 'png'] },
    2: { count: 2, extensions: ['png', 'png'] },
    3: { count: 2, extensions: ['png', 'png'] },
    4: { count: 2, extensions: ['png', 'png'] },
    5: { count: 3, extensions: ['png', 'png', 'png'] },
    6: { count: 2, extensions: ['png', 'png'] },
    7: { count: 2, extensions: ['png', 'png'] },
    8: { count: 3, extensions: ['png', 'png', 'png'] },
    9: { count: 2, extensions: ['png', 'png'] },
    10: { count: 2, extensions: ['png', 'png'] },
    11: { count: 2, extensions: ['png', 'png'] },
    12: { count: 2, extensions: ['png', 'png'] },
    13: { count: 2, extensions: ['png', 'jpg'] },
    14: { count: 2, extensions: ['png', 'png'] },
    15: { count: 2, extensions: ['png', 'png'] },
    16: { count: 2, extensions: ['png', 'png'] },
    17: { count: 2, extensions: ['png', 'png'] },
    18: { count: 2, extensions: ['png', 'png'] },
    19: { count: 2, extensions: ['png', 'png'] },
    20: { count: 2, extensions: ['png', 'png'] },
  }
  
  const numId = Number(id)
  return coverData[numId] || { count: 3, extensions: ['png', 'png', 'png'] }
}

// 获取封面图片路径数组
export const getCoverImages = (id) => {
  const info = getCoverInfo(id)
  return info.extensions.map((ext, index) => 
    `/assets/cover/cover${id}-${index + 1}.${ext}`
  )
}

function MainPage({ onCoverClick, onTabChange, collapsed, onToggleCollapse, userTemplates, onAddClick, onManageTemplateClick, onTrendingClick }) {
  const tabs = ['All', 'Single Image', 'Multiple Images', 'Shared Records', 'Tutorial Post', 'Community Discussion', 'Other']
  const [activeTabIndex, setActiveTabIndex] = useState(0)
  const [currentDate, setCurrentDate] = useState('')

  const handleImageError = (e) => {
    const img = e.target
    const currentSrc = img.src
    // 如果是png格式，尝试回退到jpg
    if (currentSrc.endsWith('.png')) {
      const jpgSrc = currentSrc.replace('.png', '.jpg')
      img.src = jpgSrc
    }
  }

  useEffect(() => {
    const date = new Date()
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    setCurrentDate(`${year}.${month}.${day}`)
  }, [])
  
  const trendingTemplates = [
    'Instagram',
    'Rednote',
    'Youtube',
    'Pinterest',
    'VSCO'
  ]
  
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
  
  const defaultCoverIds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
  const defaultTemplates = defaultCoverIds.map((id, index) => ({
    id,
    isDefault: true,
    tags: getRandomTags(),
    images: getCoverImages(id)
  }))
  
  const allTemplates = [
    ...userTemplates,
    ...defaultTemplates
  ]
  
  const filteredTemplates = activeTabIndex === 0 
    ? allTemplates 
    : allTemplates.filter(template => template.tags && template.tags.includes(tabs[activeTabIndex]))

  return (
    <div className="main-page">
      <Sidebar activeTab="Cover" onTabChange={onTabChange} collapsed={collapsed} onToggleCollapse={onToggleCollapse} />
      
      <div className="main-content">
        <div className="top-bar">
          <h1 className="page-title">AI Cover</h1>
          <div className="top-actions">
            <button className="manage-template-btn" onClick={onManageTemplateClick}>Manage Template</button>
            <button className="add-btn" onClick={onAddClick}>
              <img src="/assets/icon_add.png" alt="Add" className="add-icon" />
            </button>
          </div>
        </div>
        
        {/* 热门模版精选展示区 */}
        <div className="trending-section">
          <div className="trending-left">
            <div className="trending-header">
              <span className="trending-date">{currentDate}</span>
              <span className="trending-separator">|</span>
              <span className="trending-title">Today’s Popular Templates</span>
            </div>
            <div className="trending-memes">
              {trendingTemplates.map((template, index) => (
                <div key={index} className="meme-item" onClick={() => onTrendingClick(index)} style={{ cursor: 'pointer' }}>
                  <img src="/assets/icon_fire.png" alt="Fire" className="meme-flame" />
                  <span className="meme-text">{template}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="trending-right">
            <img src="/assets/cover_banner.png" alt="Cover Banner" className="cover-banner" />
            <div className="trending-covers-container">
              {[1, 2, 3, 4, 5].map((id, index) => (
                <img
                  key={id}
                  src={`/assets/cover_trend/cover_trend${id}-1.png`}
                  alt={`Cover ${id}`}
                  className="trending-cover"
                  onClick={() => onTrendingClick(index)}
                  onError={handleImageError}
                />
              ))}
            </div>
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
          {filteredTemplates.map((template) => (
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
