import { useState, useEffect } from 'react'
import './ManageTemplateCard.css'

function ManageTemplateCard({ id, name = 'Template Name', addedAt = '2026-05-06 18:13:04', templateId = '2026050610125686600', tags = ['Extrinsic', 'Record', 'Products', 'Help and Interaction', 'Other'], images = [], onEdit, onDelete }) {
  const [menuOpen, setMenuOpen] = useState(false)
  const [hoveredMenuItem, setHoveredMenuItem] = useState(null)

  const handleDotClick = (e) => {
    e.stopPropagation()
    setMenuOpen(!menuOpen)
  }

  const handleEdit = () => {
    console.log('Edit template:', id)
    setMenuOpen(false)
    if (onEdit) {
      onEdit({ id, name, addedAt, templateId, tags })
    }
  }

  const handleDelete = () => {
    console.log('Delete template:', id)
    setMenuOpen(false)
    if (onDelete) {
      onDelete(id)
    }
  }

  useEffect(() => {
    const handleClickOutside = () => {
      if (menuOpen) {
        setMenuOpen(false)
      }
    }

    if (menuOpen) {
      document.addEventListener('click', handleClickOutside)
    }

    return () => {
      document.removeEventListener('click', handleClickOutside)
    }
  }, [menuOpen])

  return (
    <div className="manage-template-card">
      <div className="cover-image-container">
        <img 
          src={images && images.length > 0 ? images[0] : `/aicover/assets/cover/cover${id}.png`} 
          alt={name} 
          className="cover-image" 
        />
        {menuOpen && (
          <div className="card-menu" onClick={(e) => e.stopPropagation()}>
            <div className="menu-item">
              <button 
                className={`menu-item-button ${hoveredMenuItem === 'edit' ? 'active' : ''}`}
                onMouseEnter={() => setHoveredMenuItem('edit')}
                onMouseLeave={() => setHoveredMenuItem(null)}
                onClick={handleEdit}
              >Edit</button>
            </div>
            <div className="menu-item">
              <button 
                className={`menu-item-button ${hoveredMenuItem === 'delete' ? 'active' : ''}`}
                onMouseEnter={() => setHoveredMenuItem('delete')}
                onMouseLeave={() => setHoveredMenuItem(null)}
                onClick={handleDelete}
              >Delete</button>
            </div>
          </div>
        )}
      </div>
      
      <div className="card-bottom">
        <div className="card-info">
          <div className="card-header">
            <h3 className="card-title">{name}</h3>
            <div className="info-icon">
              <img src="/aicover/assets/icon_info.png" alt="info" className="info-icon-img" />
            </div>
          </div>
          
          <div className="card-meta">
            <p className="meta-text">Added At: {addedAt}</p>
            <p className="meta-text">ID: {templateId}</p>
          </div>
          
          <div className="tags-container">
            <span className="tag-label">Tag:</span>
            <div className="tags-wrapper">
              {tags.slice(0, 3).map((tag, index) => (
                <span key={index} className="tag">{tag}</span>
              ))}
            </div>
            {tags.length > 3 && (
              <div className="tags-wrapper tags-wrapper-second">
                {tags.slice(3).map((tag, index) => (
                  <span key={index} className="tag">{tag}</span>
                ))}
              </div>
            )}
          </div>
        </div>
        
        <div className="dot-icon-container">
          <img 
            src="/aicover/assets/icon_dot.png" 
            alt="dot" 
            className="dot-icon" 
            onClick={handleDotClick}
          />
        </div>
      </div>
    </div>
  )
}

export default ManageTemplateCard
