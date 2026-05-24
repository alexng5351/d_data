import Sidebar from './Sidebar'
import './TrendingDetailPage.css'
import { useState, useRef, useEffect } from 'react'

function TrendingDetailPage({ onBack, onTabChange, collapsed, onToggleCollapse, targetCardIndex }) {
  const cardRefs = useRef([])
  const [showImageModal, setShowImageModal] = useState(false)
  const [modalImageIndex, setModalImageIndex] = useState(0)
  const [currentTrendingCovers, setCurrentTrendingCovers] = useState([])

  const openImageModal = (covers, index) => {
    setCurrentTrendingCovers(covers)
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
    if (modalImageIndex < currentTrendingCovers.length - 1) {
      setModalImageIndex(prev => prev + 1)
    }
  }

  useEffect(() => {
    if (targetCardIndex !== null && cardRefs.current[targetCardIndex]) {
      cardRefs.current[targetCardIndex].scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      })
    }
  }, [targetCardIndex])

  // 热门模版数据
  const trendingData = [
    {
      id: 1,
      name: 'Instagram',
      source: 'Social media viral, May 2026',
      referenceImage: '/d_data/assets/cover_trend/cover_trend1-1.png',
      covers: [
        '/d_data/assets/cover_trend/cover_trend1-2.png',
        '/d_data/assets/cover_trend/cover_trend1-3.png',
        '/d_data/assets/cover_trend/cover_trend1-4.png'
      ],
      allImages: [
        '/d_data/assets/cover_trend/cover_trend1-1.png',
        '/d_data/assets/cover_trend/cover_trend1-2.png',
        '/d_data/assets/cover_trend/cover_trend1-3.png',
        '/d_data/assets/cover_trend/cover_trend1-4.png'
      ]
    },
    {
      id: 2,
      name: 'Rednote',
      source: 'Social media viral, May 2026',
      referenceImage: '/d_data/assets/cover_trend/cover_trend2-1.png',
      covers: [
        '/d_data/assets/cover_trend/cover_trend2-2.png',
        '/d_data/assets/cover_trend/cover_trend2-3.png',
        '/d_data/assets/cover_trend/cover_trend2-4.png'
      ],
      allImages: [
        '/d_data/assets/cover_trend/cover_trend2-1.png',
        '/d_data/assets/cover_trend/cover_trend2-2.png',
        '/d_data/assets/cover_trend/cover_trend2-3.png',
        '/d_data/assets/cover_trend/cover_trend2-4.png'
      ]
    },
    {
      id: 3,
      name: 'Youtube',
      source: 'Social media viral, May 2026',
      referenceImage: '/d_data/assets/cover_trend/cover_trend3-1.png',
      covers: [
        '/d_data/assets/cover_trend/cover_trend3-2.png',
        '/d_data/assets/cover_trend/cover_trend3-3.png'
      ],
      allImages: [
        '/d_data/assets/cover_trend/cover_trend3-1.png',
        '/d_data/assets/cover_trend/cover_trend3-2.png',
        '/d_data/assets/cover_trend/cover_trend3-3.png'
      ]
    },
    {
      id: 4,
      name: 'Pinterest',
      source: 'Social media viral, May 2026',
      referenceImage: '/d_data/assets/cover_trend/cover_trend4-1.png',
      covers: [
        '/d_data/assets/cover_trend/cover_trend4-2.png',
        '/d_data/assets/cover_trend/cover_trend4-3.png',
        '/d_data/assets/cover_trend/cover_trend4-4.png'
      ],
      allImages: [
        '/d_data/assets/cover_trend/cover_trend4-1.png',
        '/d_data/assets/cover_trend/cover_trend4-2.png',
        '/d_data/assets/cover_trend/cover_trend4-3.png',
        '/d_data/assets/cover_trend/cover_trend4-4.png'
      ]
    },
    {
      id: 5,
      name: 'VSCO',
      source: 'Social media viral, May 2026',
      referenceImage: '/d_data/assets/cover_trend/cover_trend5-1.png',
      covers: [
        '/d_data/assets/cover_trend/cover_trend5-2.png',
        '/d_data/assets/cover_trend/cover_trend5-3.png',
        '/d_data/assets/cover_trend/cover_trend5-4.png'
      ],
      allImages: [
        '/d_data/assets/cover_trend/cover_trend5-1.png',
        '/d_data/assets/cover_trend/cover_trend5-2.png',
        '/d_data/assets/cover_trend/cover_trend5-3.png',
        '/d_data/assets/cover_trend/cover_trend5-4.png'
      ]
    }
  ]

  return (
    <div className="trending-detail-page">
      <Sidebar activeTab="Cover" onTabChange={onTabChange} collapsed={collapsed} onToggleCollapse={onToggleCollapse} />
      
      <div className="trending-detail-content">
        <div className="trending-detail-header">
          <div className="trending-detail-back-button" onClick={onBack}>
            <span className="trending-detail-back-icon">&lt;</span>
            <span>Back to AI Cover</span>
          </div>

          <h1 className="trending-detail-page-title">Today's Popular Templates</h1>
        </div>

        <div className="trending-detail-grid-wrapper">
          <div className="trending-detail-grid">
            {trendingData.map((trending, index) => (
              <div 
                key={trending.id} 
                className="trending-detail-card"
                ref={(el) => (cardRefs.current[index] = el)}
              >
                <div className="trending-detail-card-header">
                  <img src="/d_data/assets/icon_fire.png" alt="Fire" className="trending-detail-fire-icon" />
                  <div className="trending-detail-header-content">
                    <h3 className="trending-detail-card-name">{trending.name}</h3>
                    <p className="trending-detail-card-source">Source: {trending.source}</p>
                  </div>
                </div>
                <div className="trending-detail-card-content">
                  <div className="trending-detail-reference-section">
                    <img src={trending.referenceImage} alt={trending.name} className="trending-detail-reference-image" />
                    <div className="trending-detail-divider"></div>
                  </div>
                  <div className="trending-detail-covers-section">
                    {trending.covers.map((cover, index) => (
                      <div 
                        key={index} 
                        className="trending-detail-cover-wrapper"
                        onClick={() => openImageModal(trending.covers, index)}
                      >
                        <img src={cover} alt={`Cover ${index + 1}`} className="trending-detail-cover" />
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {showImageModal && (
        <div className="trending-detail-image-modal" onClick={closeImageModal}>
          <div className="trending-detail-image-modal-content" onClick={(e) => e.stopPropagation()}>
            <img 
              src={currentTrendingCovers[modalImageIndex]} 
              alt="Preview" 
              className="trending-detail-image-modal-image"
            />
            <button 
              className={`trending-detail-image-modal-prev ${modalImageIndex === 0 ? 'disabled' : ''}`}
              onClick={handlePrevImage}
            >
              <img src="/d_data/assets/icon_previous.png" alt="Previous" />
            </button>
            <button 
              className={`trending-detail-image-modal-next ${modalImageIndex === currentTrendingCovers.length - 1 ? 'disabled' : ''}`}
              onClick={handleNextImage}
            >
              <img src="/d_data/assets/icon_next.png" alt="Next" />
            </button>
            <div className="trending-detail-image-modal-dots">
              {currentTrendingCovers.map((_, index) => (
                <div 
                  key={index}
                  className={`trending-detail-image-modal-dot ${index === modalImageIndex ? 'active' : ''}`}
                />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default TrendingDetailPage
