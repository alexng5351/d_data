import Sidebar from './Sidebar'
import { getAssetPath } from '../utils'
import EmojiDetailModal from './EmojiDetailModal'
import './MemeDetailPage.css'
import { useState, useRef, useEffect } from 'react'

function MemeDetailPage({ onBack, onTabChange, collapsed, onToggleCollapse, targetCardIndex }) {
  const getVariantUrl = (variant) => variant?.removed_bg_url || variant?.url
  const getMemeTitle = (meme) => meme.short_name || meme.title || ''
  const getReferenceImageUrl = (meme) => meme.source_url || meme.frame_png_path || ''
  const hasDisplayTitle = (meme) => Boolean((meme.short_name || meme.title || '').trim())
  const hasGeneratedVariant = (meme) =>
    Array.isArray(meme.generated_variants) && meme.generated_variants.some((variant) => getVariantUrl(variant))
  const isDisplayableMeme = (meme) =>
    meme.status === 'generated' && hasGeneratedVariant(meme) && hasDisplayTitle(meme)

  const [selectedEmoji, setSelectedEmoji] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [memeItems, setMemeItems] = useState([])
  const [dataDate, setDataDate] = useState('')
  const cardRefs = useRef([])

  const handleEmojiClick = (emojiImage, index, shortName = '') => {
    const emoji = {
      image: emojiImage,
      label: `Emoji ${index + 1}`,
      description: (
        <>
          You know the look. The iconic <i>"{shortName}"</i>, now living in your emoji keyboard.
        </>
      )
    }
    setSelectedEmoji(emoji)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setSelectedEmoji(null)
  }

  useEffect(() => {
    const loadMemeData = async () => {
      try {
        const response = await fetch('/data/meme/meme_candidates.json')
        const data = await response.json()
        const sortedItems = [...(data.items || [])]
          .filter(isDisplayableMeme)
          .sort((a, b) => (a.index || 0) - (b.index || 0))
        setMemeItems(sortedItems)
        
        // 保存 JSON 中的 last_updated 日期
        if (data.last_updated) {
          const date = new Date(data.last_updated)
          const year = date.getFullYear()
          const month = String(date.getMonth() + 1).padStart(2, '0')
          const day = String(date.getDate()).padStart(2, '0')
          setDataDate(`${year}.${month}.${day}`)
        }
      } catch (error) {
        console.error('Failed to load meme data:', error)
      }
    }
    loadMemeData()
  }, [])

  useEffect(() => {
    if (targetCardIndex !== null && cardRefs.current[targetCardIndex]) {
      cardRefs.current[targetCardIndex].scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      })
    }
  }, [targetCardIndex])

  return (
    <div className="meme-detail-page">
      <Sidebar activeTab="Emoji" onTabChange={onTabChange} collapsed={collapsed} onToggleCollapse={onToggleCollapse} />
      
      <div className="meme-detail-content">
        <div className="meme-detail-header">
          <div className="meme-detail-back-button" onClick={onBack}>
            <span className="meme-detail-back-icon">&lt;</span>
            <span>Back to Emoji</span>
          </div>

          <h1 className="meme-detail-page-title">AI-Remixed Memes as Emojis</h1>
        </div>

        <div className="meme-detail-grid-wrapper">
          <div className="meme-detail-grid">
            {memeItems.map((meme, index) => {
              const generatedStickers = (meme.generated_variants || [])
                .map((variant) => variant.removed_bg_url || variant.url)
                .filter(Boolean)
              const memeTitle = getMemeTitle(meme)

              return (
                <div 
                  key={meme.id || meme.index} 
                  className="meme-detail-card"
                  ref={(el) => (cardRefs.current[index] = el)}
                >
                  <div className="meme-detail-card-header">
                    <img src={getAssetPath("assets/icon_fire.png")} alt="Fire" className="meme-detail-fire-icon" />
                    <div className="meme-detail-header-content">
                      <div className="meme-detail-title-row">
                        <h3 className="meme-detail-card-name">{memeTitle}</h3>
                        <img src={getAssetPath("assets/icon_airemix.png")} alt="" className="meme-detail-airemix-icon" />
                      </div>
                      <p className="meme-detail-card-source">
                        <img src={getAssetPath("assets/icon_link.png")} alt="" className="meme-detail-source-icon" />
                        <span>
                          Source: {
                            meme.page_url ? (
                              <a href={meme.page_url} target="_blank" rel="noopener noreferrer" style={{color: 'inherit', textDecoration: 'underline'}}>
                                {meme.source_platform || 'Giphy'}
                              </a>
                            ) : (meme.source_platform || 'Giphy')
                          }
                          {dataDate && (
                            <span>, {dataDate}</span>
                          )}
                        </span>
                      </p>
                    </div>
                  </div>
                  <div className="meme-detail-card-content">
                    <div className="meme-detail-reference-section">
                      <img src={getReferenceImageUrl(meme)} alt={memeTitle} className="meme-detail-reference-image" />
                      <div className="meme-detail-divider"></div>
                    </div>
                    <div className="meme-detail-emojis-section">
                      {generatedStickers.map((stickerUrl, stickerIndex) => (
                        <div
                          key={`${meme.id || meme.index}-sticker-${stickerIndex}-${stickerUrl}`}
                          className="meme-detail-emoji-wrapper"
                          onClick={() => handleEmojiClick(stickerUrl, stickerIndex, memeTitle)}
                        >
                          <img
                            src={stickerUrl}
                            alt={`${memeTitle} ${stickerIndex + 1}`}
                            className="meme-detail-emoji"
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
        <EmojiDetailModal 
          emoji={selectedEmoji}
          isOpen={isModalOpen}
          onClose={handleCloseModal}
        />
      </div>
    </div>
  )
}

export default MemeDetailPage
