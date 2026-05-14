import { useState, useEffect } from 'react'
import './CoverInputPage.css'
import Sidebar from './Sidebar'

function CoverInputPage({ onBack, onGenerate, onTabChange, collapsed, onToggleCollapse, templateId = null, userTemplates = [] }) {
  const [currentId, setCurrentId] = useState(templateId || 1)
  const [selectedImageIndex, setSelectedImageIndex] = useState(0)
  const [userImages, setUserImages] = useState(new Array(8).fill(null))
  const [showImageModal, setShowImageModal] = useState(false)
  const [modalImageIndex, setModalImageIndex] = useState(0)
  const [showGenerateContainer, setShowGenerateContainer] = useState(false)
  const [generateComplete, setGenerateComplete] = useState(false)
  const [isRegenerating, setIsRegenerating] = useState(false)
  const [resultHistory, setResultHistory] = useState([])
  const [activeMenuIndex, setActiveMenuIndex] = useState(null)
  const [hoveredMenuItem, setHoveredMenuItem] = useState(null)
  const [showExitModal, setShowExitModal] = useState(false)

  useEffect(() => {
    if (templateId !== null && templateId !== undefined) {
      setCurrentId(templateId)
    }
  }, [templateId])

  useEffect(() => {
    const handleClickOutside = () => {
      if (activeMenuIndex !== null) {
        closeMenu()
      }
    }
    if (activeMenuIndex !== null) {
      document.addEventListener('click', handleClickOutside)
    }
    return () => {
      document.removeEventListener('click', handleClickOutside)
    }
  }, [activeMenuIndex])

  const openImageModal = (index) => {
    setModalImageIndex(index)
    setShowImageModal(true)
  }

  const closeImageModal = () => {
    setShowImageModal(false)
  }

  const handlePrevImage = () => {
    if (modalImageIndex > 0) {
      setModalImageIndex(prev => prev - 1)
    }
  }

  const handleNextImage = () => {
    if (modalImageIndex < coverImages.length - 1) {
      setModalImageIndex(prev => prev + 1)
    }
  }

  const getTemplateImages = () => {
    const userTemplate = userTemplates.find(t => t.id === currentId)
    if (userTemplate && userTemplate.images && userTemplate.images.length > 0) {
      const images = [...userTemplate.images]
      while (images.length < 3) images.push(images[0] || '')
      return images.slice(0, 3)
    }
    const id = typeof currentId === 'number' ? currentId : 1
    return [
      `/assets/cover/cover${id}-1.png`,
      `/assets/cover/cover${id}-2.png`,
      `/assets/cover/cover${id}-3.png`,
    ]
  }

  const coverImages = getTemplateImages()
  
  // 找出第一个空位置
  const firstEmptyIndex = userImages.findIndex(img => img === null)

  const handleImageUpload = (e) => {
    const files = Array.from(e.target.files)
    const emptyIndices = userImages.map((img, idx) => img === null ? idx : -1).filter(idx => idx !== -1)
    if (emptyIndices.length === 0) return
    
    const filesToProcess = files.slice(0, emptyIndices.length)
    filesToProcess.forEach((file, fileIndex) => {
      const reader = new FileReader()
      reader.onload = (event) => {
        setUserImages(prev => {
          const newImages = [...prev]
          newImages[emptyIndices[fileIndex]] = event.target.result
          return newImages
        })
      }
      reader.readAsDataURL(file)
    })
  }

  const handleRemoveImage = (index) => {
    setUserImages(prev => {
      // 1. 先删除指定位置的图片（设为null）
      const removedNull = [...prev]
      removedNull[index] = null
      // 2. 过滤掉所有null值
      const filtered = removedNull.filter(img => img !== null)
      // 3. 末尾补null到8个位置
      while (filtered.length < 8) {
        filtered.push(null)
      }
      return filtered
    })
  }

  const handleGenerate = () => {
    if (!showGenerateContainer) {
      setShowGenerateContainer(true)
    }
    
    if (generateComplete) {
      // 将当前结果添加到历史
      setResultHistory(prev => [...prev, Date.now()])
      setIsRegenerating(true)
      setTimeout(() => {
        setGenerateComplete(false)
        setTimeout(() => {
          setIsRegenerating(false)
          setGenerateComplete(true)
        }, 2500)
      }, 500)
    } else {
      setGenerateComplete(false)
      setTimeout(() => {
        setGenerateComplete(true)
      }, 2500)
    }
  }

  const toggleMenu = (index) => {
    if (activeMenuIndex === index) {
      setActiveMenuIndex(null)
    } else {
      setActiveMenuIndex(index)
    }
  }

  const closeMenu = () => {
    setActiveMenuIndex(null)
  }

  const handleDownload = (index) => {
    console.log(`Downloading image ${index + 1}`)
    closeMenu()
  }

  const handleDelete = (index) => {
    console.log(`Deleting image ${index + 1}`)
    closeMenu()
  }

  const handleBackClick = () => {
    setShowExitModal(true)
  }

  const handleExit = () => {
    setShowExitModal(false)
    onBack()
  }

  const handleCancel = () => {
    setShowExitModal(false)
  }

  return (
    <div className="cover-input-page">
      <Sidebar activeTab="Cover" onTabChange={onTabChange} collapsed={collapsed} onToggleCollapse={onToggleCollapse} />
      
      <div className="cover-input-content">
        <div className="cover-input-back-button" onClick={handleBackClick}>
          <span className="cover-input-back-icon">&lt;</span>
          <span>Back to AI Cover</span>
        </div>

        <h1 className="cover-input-page-title">Create your Cover</h1>

        <div className="cover-input-content-card">
          <div className="cover-input-template-display">
            <div className="cover-input-cover-images">
              {coverImages.map((image, index) => (
                <div 
                  key={index}
                  className="cover-input-cover-image-item"
                  onClick={() => {
                    setSelectedImageIndex(index)
                    openImageModal(index)
                  }}
                >
                  <img src={image} alt={`Cover ${index + 1}`} />
                </div>
              ))}
            </div>
            <p className="cover-input-template-hint">Please select template images to use for generating style prompts. <br />(up to 8 images)</p>
          </div>

          <div className="cover-input-upload-area">
            {/* 直接渲染8个固定位置 */}
            {[0, 1, 2, 3, 4, 5, 6, 7].map((index) => {
              const hasImage = userImages[index] !== null
              const isUploadSpot = index === firstEmptyIndex
              const hasAnyImages = userImages.some(img => img !== null)
              
              if (hasImage) {
                // 有图片的位置
                return (
                  <div key={`pos-${index}`} className="cover-input-uploaded-item">
                    <img src={userImages[index]} alt={`Uploaded ${index + 1}`} className="cover-input-uploaded-image" />
                    <button className="cover-input-remove-image-btn" onClick={() => handleRemoveImage(index)}>×</button>
                  </div>
                )
              } else if (isUploadSpot) {
                // 第一个空位置，显示上传按钮
                return (
                  <label key={`pos-${index}`} className="cover-input-upload-placeholder">
                    <img src="/assets/icon_addimages.png" alt="Add" className="cover-input-upload-icon" />
                    <input id="image-upload" name="images" type="file" accept="image/*" multiple style={{ display: 'none' }} onChange={handleImageUpload} />
                  </label>
                )
              } else if (hasAnyImages) {
                // 有图片时，其他空位置保留（维持grid布局和间距）
                return (
                  <div key={`pos-${index}`} className="cover-input-upload-empty-slot" />
                )
              } else {
                // 没有任何图片时，其他空位置不渲染
                return null
              }
            })}
          </div>

          <button className="cover-input-generate-button" onClick={handleGenerate}>
            <span>Generating</span>
            <img src="/assets/icon_generate_black.png" alt="Generate" className="cover-input-generate-icon" />
          </button>
        </div>

        <div className={`cover-input-generate-container ${showGenerateContainer ? 'show' : ''} ${generateComplete ? 'complete' : ''} ${isRegenerating ? 'regenerating' : ''} ${resultHistory.length > 0 ? 'has-old-results' : ''}`}>
          {/* 加载状态：只显示在正在生成时 */}
          {!generateComplete && (
            <div className="cover-input-generate-inner-frame">
              <img src="/assets/icon_generate.png" alt="Generating" className="cover-input-generate-inner-icon" />
            </div>
          )}
          
          {/* 新结果卡片 */}
          {generateComplete && (
            <div className="cover-input-generate-results new-results">
              {[0, 1, 2].map((index) => (
                <div key={`new-${index}`} className={`cover-input-generate-result-item cover-input-generate-result-item-${index}`}>
                  <div className="cover-input-generate-result-image">
                    <img src={`/assets/cover_generate${index + 1}.png`} alt={`Result ${index + 1}`} />
                    {activeMenuIndex === index && (
                      <div className="cover-input-generate-result-menu" onClick={(e) => e.stopPropagation()}>
                        <div className="cover-input-generate-result-menu-item">
                          <button 
                            className={`cover-input-generate-result-menu-item-button ${hoveredMenuItem === `${index}-download` ? 'active' : ''}`}
                            onMouseEnter={() => setHoveredMenuItem(`${index}-download`)}
                            onMouseLeave={() => setHoveredMenuItem(null)}
                            onClick={() => handleDownload(index)}
                          >
                            Download
                          </button>
                        </div>
                        <div className="cover-input-generate-result-menu-item">
                          <button 
                            className={`cover-input-generate-result-menu-item-button ${hoveredMenuItem === `${index}-delete` ? 'active' : ''}`}
                            onMouseEnter={() => setHoveredMenuItem(`${index}-delete`)}
                            onMouseLeave={() => setHoveredMenuItem(null)}
                            onClick={() => handleDelete(index)}
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                  <div className="cover-input-generate-result-bottom">
                    <div className="cover-input-generate-result-info">
                      <div>Added At: 2026-05-06 18:13:04</div>
                      <div>ID: 202605061012568660{index}</div>
                      <div>Seedream 4.5(ModelHub)</div>
                    </div>
                    <div className="cover-input-generate-result-menu-button" onClick={(e) => {
                      e.stopPropagation()
                      toggleMenu(index)
                    }}>
                      <img src="/assets/icon_dot.png" alt="Menu" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {/* 历史结果卡片 - 依次显示在下方 */}
          {resultHistory.map((timestamp, historyIndex) => (
            <div key={timestamp} className="cover-input-generate-results history-results">
              {[0, 1, 2].map((index) => (
                <div key={`history-${historyIndex}-${index}`} className="cover-input-generate-result-item">
                  <div className="cover-input-generate-result-image">
                    <img src={`/assets/cover_generate${index + 1}.png`} alt={`Result ${index + 1}`} />
                  </div>
                  <div className="cover-input-generate-result-bottom">
                    <div className="cover-input-generate-result-info">
                      <div>Added At: 2026-05-06 18:13:04</div>
                      <div>ID: 202605061012568660{index}</div>
                      <div>Seedream 4.5(ModelHub)</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>

      {showImageModal && (
        <div className="cover-input-image-modal" onClick={closeImageModal}>
          <div className="cover-input-image-modal-content" onClick={(e) => e.stopPropagation()}>
            <img 
              src={coverImages[modalImageIndex]} 
              alt="Preview" 
              className="cover-input-image-modal-image"
            />
            <button 
              className={`cover-input-image-modal-prev ${modalImageIndex === 0 ? 'disabled' : ''}`}
              onClick={handlePrevImage}
            >
              <img src="/assets/icon_previous.png" alt="Previous" />
            </button>
            <button 
              className={`cover-input-image-modal-next ${modalImageIndex === coverImages.length - 1 ? 'disabled' : ''}`}
              onClick={handleNextImage}
            >
              <img src="/assets/icon_next.png" alt="Next" />
            </button>
            <div className="cover-input-image-modal-dots">
              {coverImages.map((_, index) => (
                <div 
                  key={index}
                  className={`cover-input-image-modal-dot ${index === modalImageIndex ? 'active' : ''}`}
                />
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Exit Confirmation Modal */}
      {showExitModal && (
        <div className="cover-input-exit-modal-overlay" onClick={handleCancel}>
          <div className="cover-input-exit-modal" onClick={(e) => e.stopPropagation()}>
            <div className="cover-input-exit-modal-header">
              <div className="cover-input-exit-modal-title">Are you sure you want to exit?</div>
              <div className="cover-input-exit-modal-close" onClick={handleCancel}>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M4 4L12 12M4 12L12 4" stroke="white" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </div>
            </div>
            <div className="cover-input-exit-modal-body">
              <div className="cover-input-exit-modal-message">
                Your current edits may not be saved. Are you sure you want to exit?
              </div>
            </div>
            <div className="cover-input-exit-modal-buttons">
              <button 
                className="cover-input-exit-modal-button cover-input-exit-modal-button-exit"
                onClick={handleExit}
              >
                Exit
              </button>
              <button 
                className="cover-input-exit-modal-button cover-input-exit-modal-button-cancel"
                onClick={handleCancel}
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

export default CoverInputPage