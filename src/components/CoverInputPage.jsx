import { useState, useEffect, useRef } from 'react'
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
  const [activeHistoryMenuIndex, setActiveHistoryMenuIndex] = useState(null)
  const [hoveredMenuItem, setHoveredMenuItem] = useState(null)
  const [showExitModal, setShowExitModal] = useState(false)
  const [description, setDescription] = useState('')
  const [selectedAIMode, setSelectedAIMode] = useState('Seedream 4.0 (Mod...)')
  const [showAIModeMenu, setShowAIModeMenu] = useState(false)
  const [aimMenuPosition, setAimMenuPosition] = useState('bottom')
  const [newResults, setNewResults] = useState([])

  const aiModes = [
    'Seedream 4.0 (Mod...)',
    'Seedream 4.5(ModelHub)',
    'Seedream 5.0',
    'Other Model'
  ]

  useEffect(() => {
    if (templateId !== null && templateId !== undefined) {
      setCurrentId(templateId)
    }
  }, [templateId])

  useEffect(() => {
    const handleClickOutside = () => {
      if (activeMenuIndex !== null || activeHistoryMenuIndex !== null) {
        closeMenu()
      }
    }
    if (activeMenuIndex !== null || activeHistoryMenuIndex !== null) {
      document.addEventListener('click', handleClickOutside)
    }
    return () => {
      document.removeEventListener('click', handleClickOutside)
    }
  }, [activeMenuIndex, activeHistoryMenuIndex])

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
      // 用户模板：返回实际数量（最多3张）
      return userTemplate.images.slice(0, 3)
    }
    const id = typeof currentId === 'number' ? currentId : 1
    // 默认模板：固定返回3张
    return [
      `/aicover/assets/cover/cover${id}-1.png`,
      `/aicover/assets/cover/cover${id}-2.png`,
      `/aicover/assets/cover/cover${id}-3.png`,
    ]
  }

  const coverImages = getTemplateImages()
  
  // 确保 selectedImageIndex 不会超出实际图片数量的范围
  useEffect(() => {
    if (coverImages.length > 0 && selectedImageIndex >= coverImages.length) {
      setSelectedImageIndex(0)
      setModalImageIndex(0)
    }
  }, [coverImages.length])
  
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

  const generateResultImages = () => {
    return [0, 1, 2].map((i) => ({
      id: Date.now() + i,
      image: `/aicover/assets/cover_generate${i + 1}.png`,
      addedAt: new Date().toLocaleString(),
      resultId: `202605061012568660${i}`,
      aiMode: selectedAIMode
    }))
  }

  const handleGenerate = () => {
    if (!showGenerateContainer) {
      setShowGenerateContainer(true)
    }
    
    if (generateComplete) {
      // 将当前结果添加到历史
      if (newResults.length > 0) {
        setResultHistory(prev => [...prev, { timestamp: Date.now(), results: newResults }])
      }
      setIsRegenerating(true)
      setGenerateComplete(false)
      setTimeout(() => {
        setIsRegenerating(false)
        const results = generateResultImages()
        setNewResults(results)
        setGenerateComplete(true)
      }, 2500)
    } else {
      setGenerateComplete(false)
      setTimeout(() => {
        const results = generateResultImages()
        setNewResults(results)
        setGenerateComplete(true)
      }, 2500)
    }
  }

  const toggleMenu = (index) => {
    if (activeMenuIndex === index) {
      setActiveMenuIndex(null)
    } else {
      setActiveMenuIndex(index)
      setActiveHistoryMenuIndex(null)
    }
  }

  const toggleHistoryMenu = (historyIndex, resultIndex) => {
    const key = `${historyIndex}-${resultIndex}`
    if (activeHistoryMenuIndex === key) {
      setActiveHistoryMenuIndex(null)
    } else {
      setActiveHistoryMenuIndex(key)
      setActiveMenuIndex(null)
    }
  }

  const closeMenu = () => {
    setActiveMenuIndex(null)
    setActiveHistoryMenuIndex(null)
  }

  const handleDownload = (imageUrl, fileName = 'cover-image.png') => {
    const link = document.createElement('a')
    link.href = imageUrl
    link.download = fileName
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    closeMenu()
  }

  const handleDeleteNewResult = (index) => {
    setNewResults(prev => {
      const newList = [...prev]
      newList.splice(index, 1)
      return newList
    })
    closeMenu()
  }

  const handleDeleteHistoryResult = (historyIndex, resultIndex) => {
    setResultHistory(prev => {
      const newHistory = [...prev]
      const historyItem = newHistory[historyIndex]
      if (historyItem && historyItem.results) {
        historyItem.results = [...historyItem.results]
        historyItem.results.splice(resultIndex, 1)
        // 如果该历史批次没有结果了，删除整个批次
        if (historyItem.results.length === 0) {
          newHistory.splice(historyIndex, 1)
        }
      }
      return newHistory
    })
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

  const aiModeSelectRef = useRef(null)

  const toggleAIModeMenu = (e) => {
    e.stopPropagation()
    const isOpen = !showAIModeMenu
    if (isOpen && aiModeSelectRef.current) {
      const rect = aiModeSelectRef.current.getBoundingClientRect()
      const menuHeight = 160 // 预估菜单高度
      const windowHeight = window.innerHeight
      
      // 判断向下展开是否会超出视口
      if (rect.bottom + menuHeight > windowHeight) {
        setAimMenuPosition('top')
      } else {
        setAimMenuPosition('bottom')
      }
    }
    setShowAIModeMenu(isOpen)
  }

  const selectAIMode = (mode, e) => {
    e.stopPropagation()
    setSelectedAIMode(mode)
    setShowAIModeMenu(false)
  }

  useEffect(() => {
    const handleClickOutsideAIMode = () => {
      if (showAIModeMenu) {
        setShowAIModeMenu(false)
      }
    }
    if (showAIModeMenu) {
      document.addEventListener('click', handleClickOutsideAIMode)
    }
    return () => {
      document.removeEventListener('click', handleClickOutsideAIMode)
    }
  }, [showAIModeMenu])

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
            <div className="cover-input-feather-overlay"></div>
          </div>
          <p className="cover-input-template-hint">Please select template images to use for generating style prompts. <br />(up to 8 images)</p>

          <div className="cover-input-scrollable-content">
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
                      <img src="/aicover/assets/icon_addimages.png" alt="Add" className="cover-input-upload-icon" />
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

            <div className="cover-input-description-section">
              <div className="cover-input-section-label">Description</div>
              <textarea
                className="cover-input-description-textarea"
                placeholder="Add a description..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
              />
            </div>

            <div className="cover-input-ai-mode-section">
              <div className="cover-input-section-label">AI Mode</div>
              <div className="cover-input-ai-mode-container">
                <div 
                  className="cover-input-ai-mode-select" 
                  onClick={toggleAIModeMenu}
                  ref={aiModeSelectRef}
                >
                  <span>{selectedAIMode}</span>
                  <svg className={`cover-input-ai-mode-arrow ${showAIModeMenu ? 'open' : ''}`} width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M4 6L8 10L12 6" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <button className="cover-input-ai-mode-refresh">
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M10 3.33334C7.0555 3.33334 4.58333 5.27776 3.75 8.05556C3.61111 8.49999 3.88889 8.94444 4.33333 8.94444H5.83333C6.11111 8.94444 6.33333 8.72222 6.33333 8.44444C6.83333 6.83334 8.27778 5.66668 10 5.66668C12.4444 5.66668 14.4444 7.66668 14.4444 10.1111C14.4444 12.5556 12.4444 14.5556 10 14.5556C8.5 14.5556 7.16667 13.8333 6.38889 12.7222C6.27778 12.5556 6.11111 12.4444 5.88889 12.4444H4.38889C3.94444 12.4444 3.72222 12.8889 3.88889 13.2222C4.77778 14.9444 6.72222 16.1111 10 16.1111C13.3148 16.1111 16 13.4259 16 10.1111C16 6.79631 13.3148 4.11112 10 4.11112V3.33334Z" fill="white"/>
                  </svg>
                </button>
                {showAIModeMenu && (
                  <div className={`cover-input-ai-mode-menu ${aimMenuPosition === 'top' ? 'top' : ''}`} onClick={(e) => e.stopPropagation()}>
                    {aiModes.map((mode, index) => (
                      <div
                        key={index}
                        className={`cover-input-ai-mode-menu-item ${selectedAIMode === mode ? 'active' : ''}`}
                        onClick={(e) => selectAIMode(mode, e)}
                      >
                        {mode}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          <button className="cover-input-generate-button" onClick={handleGenerate}>
            <span>Generating</span>
            <img src="/aicover/assets/icon_generate_black.png" alt="Generate" className="cover-input-generate-icon" />
          </button>
        </div>

        <div className={`cover-input-generate-container ${showGenerateContainer ? 'show' : ''} ${generateComplete ? 'complete' : ''} ${isRegenerating ? 'regenerating' : ''} ${resultHistory.length > 0 ? 'has-old-results' : ''}`}>
          {/* 加载状态：只显示在正在生成时 */}
          {!generateComplete && (
            <div className="cover-input-generate-inner-frame">
              <img src="/aicover/assets/icon_generate.png" alt="Generating" className="cover-input-generate-inner-icon" />
            </div>
          )}
          
          {/* 新结果卡片 */}
          {generateComplete && newResults.length > 0 && (
            <div className="cover-input-generate-results new-results">
              {newResults.map((result, index) => (
                <div key={result.id} className={`cover-input-generate-result-item cover-input-generate-result-item-${index}`}>
                  <div className="cover-input-generate-result-image">
                    <img src={result.image} alt={`Result ${index + 1}`} />
                    {activeMenuIndex === index && (
                      <div className="cover-input-generate-result-menu" onClick={(e) => e.stopPropagation()}>
                        <div className="cover-input-generate-result-menu-item">
                          <button 
                            className={`cover-input-generate-result-menu-item-button ${hoveredMenuItem === `${index}-download` ? 'active' : ''}`}
                            onMouseEnter={() => setHoveredMenuItem(`${index}-download`)}
                            onMouseLeave={() => setHoveredMenuItem(null)}
                            onClick={() => handleDownload(result.image, `cover-result-${result.resultId}.png`)}
                          >
                            Download
                          </button>
                        </div>
                        <div className="cover-input-generate-result-menu-item">
                          <button 
                            className={`cover-input-generate-result-menu-item-button ${hoveredMenuItem === `${index}-delete` ? 'active' : ''}`}
                            onMouseEnter={() => setHoveredMenuItem(`${index}-delete`)}
                            onMouseLeave={() => setHoveredMenuItem(null)}
                            onClick={() => handleDeleteNewResult(index)}
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                  <div className="cover-input-generate-result-bottom">
                    <div className="cover-input-generate-result-info">
                      <div>Added At: {result.addedAt}</div>
                      <div>ID: {result.resultId}</div>
                      <div>{result.aiMode}</div>
                    </div>
                    <div className="cover-input-generate-result-menu-button" onClick={(e) => {
                      e.stopPropagation()
                      toggleMenu(index)
                    }}>
                      <img src="/aicover/assets/icon_dot.png" alt="Menu" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {/* 历史结果卡片 - 依次显示在下方 */}
          {resultHistory.map((historyItem, historyIndex) => (
            <div key={historyItem.timestamp} className="cover-input-generate-results history-results">
              {historyItem.results.map((result, index) => (
                <div key={result.id} className="cover-input-generate-result-item">
                  <div className="cover-input-generate-result-image">
                    <img src={result.image} alt={`Result ${index + 1}`} />
                    {activeHistoryMenuIndex === `${historyIndex}-${index}` && (
                      <div className="cover-input-generate-result-menu" onClick={(e) => e.stopPropagation()}>
                        <div className="cover-input-generate-result-menu-item">
                          <button 
                            className={`cover-input-generate-result-menu-item-button ${hoveredMenuItem === `history-${historyIndex}-${index}-download` ? 'active' : ''}`}
                            onMouseEnter={() => setHoveredMenuItem(`history-${historyIndex}-${index}-download`)}
                            onMouseLeave={() => setHoveredMenuItem(null)}
                            onClick={() => handleDownload(result.image, `cover-result-${result.resultId}.png`)}
                          >
                            Download
                          </button>
                        </div>
                        <div className="cover-input-generate-result-menu-item">
                          <button 
                            className={`cover-input-generate-result-menu-item-button ${hoveredMenuItem === `history-${historyIndex}-${index}-delete` ? 'active' : ''}`}
                            onMouseEnter={() => setHoveredMenuItem(`history-${historyIndex}-${index}-delete`)}
                            onMouseLeave={() => setHoveredMenuItem(null)}
                            onClick={() => handleDeleteHistoryResult(historyIndex, index)}
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                  <div className="cover-input-generate-result-bottom">
                    <div className="cover-input-generate-result-info">
                      <div>Added At: {result.addedAt}</div>
                      <div>ID: {result.resultId}</div>
                      <div>{result.aiMode}</div>
                    </div>
                    <div className="cover-input-generate-result-menu-button" onClick={(e) => {
                      e.stopPropagation()
                      toggleHistoryMenu(historyIndex, index)
                    }}>
                      <img src="/aicover/assets/icon_dot.png" alt="Menu" />
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
              <img src="/aicover/assets/icon_previous.png" alt="Previous" />
            </button>
            <button 
              className={`cover-input-image-modal-next ${modalImageIndex === coverImages.length - 1 ? 'disabled' : ''}`}
              onClick={handleNextImage}
            >
              <img src="/aicover/assets/icon_next.png" alt="Next" />
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
              <div className="cover-input-exit-modal-title">Leave this page?</div>
              <div className="cover-input-exit-modal-close" onClick={handleCancel}>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M4 4L12 12M4 12L12 4" stroke="white" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </div>
            </div>
            <div className="cover-input-exit-modal-body">
              <div className="cover-input-exit-modal-message">
                Your current changes will be lost and cannot be recovered.
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