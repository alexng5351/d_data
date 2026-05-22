import Sidebar from './Sidebar'
import EmojiDetailModal from './EmojiDetailModal'
import './MemeDetailPage.css'
import { useState, useRef, useEffect } from 'react'

function MemeDetailPage({ onBack, onTabChange, collapsed, onToggleCollapse, targetCardIndex }) {
  const [selectedEmoji, setSelectedEmoji] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const cardRefs = useRef([])

  const handleEmojiClick = (emojiImage, index) => {
    const emoji = {
      image: emojiImage,
      label: `Emoji ${index + 1}`,
      description: 'This is a remixed emoji based on popular meme references.'
    }
    setSelectedEmoji(emoji)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setSelectedEmoji(null)
  }

  useEffect(() => {
    if (targetCardIndex !== null && cardRefs.current[targetCardIndex]) {
      cardRefs.current[targetCardIndex].scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      })
    }
  }, [targetCardIndex])

  // 热梗meme数据
  const memeData = [
    {
      id: 1,
      name: 'Fruitcore Meme Culture',
      source: 'TikTok trend, May 2026',
      referenceImage: '/aicover/assets/emoji_design/memes/meme_ref_1.png',
      emojis: [
        '/aicover/assets/emoji_design/memes/meme1_emoji1.png',
        '/aicover/assets/emoji_design/memes/meme1_emoji2.png',
        '/aicover/assets/emoji_design/memes/meme1_emoji3.png',
        '/aicover/assets/emoji_design/memes/meme1_emoji4.png',
        '/aicover/assets/emoji_design/memes/meme1_emoji5.png'
      ]
    },
    {
      id: 2,
      name: 'Lei Jun\'s Selfie Moment',
      source: 'Social media viral, Apr 2026',
      referenceImage: '/aicover/assets/emoji_design/memes/meme_ref_2.png',
      emojis: [
        '/aicover/assets/emoji_design/memes/meme2_emoji1.png',
        '/aicover/assets/emoji_design/memes/meme2_emoji2.png',
        '/aicover/assets/emoji_design/memes/meme2_emoji3.png',
        '/aicover/assets/emoji_design/memes/meme2_emoji4.png'
      ]
    },
    {
      id: 3,
      name: 'Side-Eye Dog',
      source: 'TikTok trend, May 2026',
      referenceImage: '/aicover/assets/emoji_design/memes/meme_ref_3.png',
      emojis: [
        '/aicover/assets/emoji_design/memes/meme3_emoji1.png',
        '/aicover/assets/emoji_design/memes/meme3_emoji2.png',
        '/aicover/assets/emoji_design/memes/meme3_emoji3.png'
      ]
    },
    {
      id: 4,
      name: 'Viral Lobster Creature',
      source: 'TikTok trend, May 2026',
      referenceImage: '/aicover/assets/emoji_design/memes/meme_ref_4.png',
      emojis: [
        '/aicover/assets/emoji_design/memes/meme4_emoji1.png',
        '/aicover/assets/emoji_design/memes/meme4_emoji2.png',
        '/aicover/assets/emoji_design/memes/meme4_emoji3.png',
        '/aicover/assets/emoji_design/memes/meme4_emoji4.png'
      ]
    },
    {
      id: 5,
      name: 'Chaotic Pigtail Reaction',
      source: 'TikTok trend, May 2026',
      referenceImage: '/aicover/assets/emoji_design/memes/meme_ref_5.png',
      emojis: [
        '/aicover/assets/emoji_design/memes/meme5_emoji1.png',
        '/aicover/assets/emoji_design/memes/meme5_emoji2.png',
        '/aicover/assets/emoji_design/memes/meme5_emoji3.png'
      ]
    }
  ]

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
            {memeData.map((meme, index) => (
              <div 
                key={meme.id} 
                className="meme-detail-card"
                ref={(el) => (cardRefs.current[index] = el)}
              >
                <div className="meme-detail-card-header">
                  <img src="/aicover/assets/icon_fire.png" alt="Fire" className="meme-detail-fire-icon" />
                  <div className="meme-detail-header-content">
                    <h3 className="meme-detail-card-name">{meme.name}</h3>
                    <p className="meme-detail-card-source">Source: {meme.source}</p>
                  </div>
                </div>
                <div className="meme-detail-card-content">
                  <div className="meme-detail-reference-section">
                    <img src={meme.referenceImage} alt={meme.name} className="meme-detail-reference-image" />
                    <div className="meme-detail-divider"></div>
                  </div>
                  <div className="meme-detail-emojis-section">
                    {meme.emojis.map((emoji, index) => (
                      <div 
                        key={index} 
                        className="meme-detail-emoji-wrapper"
                        onClick={() => handleEmojiClick(emoji, index)}
                      >
                        <img src={emoji} alt={`Emoji ${index + 1}`} className="meme-detail-emoji" />
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
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
