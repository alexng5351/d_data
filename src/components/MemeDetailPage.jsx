import Sidebar from './Sidebar'
import { getAssetPath } from '../utils'
import EmojiDetailModal from './EmojiDetailModal'
import './MemeDetailPage.css'
import { useState, useRef, useEffect } from 'react'

function MemeDetailPage({ onBack, onTabChange, collapsed, onToggleCollapse, targetCardIndex }) {
  const [selectedEmoji, setSelectedEmoji] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [activeInfoId, setActiveInfoId] = useState(null)
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
      name: 'Cheating AI Fruit',
      source: 'Know Your Meme',
      source_url: 'https://knowyourmeme.com/memes/cheating-ai-fruit',
      fetched_at: '2026-05-25',
      infoDescription: 'AI 生成的水果拟人情侣，用来表达"完美搭档"或秀恩爱，是 2024-2025 年 TikTok/Instagram 上的 AI 卡通美图风潮代表。',
      referenceImage: getAssetPath('assets/emoji_design/memes/meme_ref_1.png'),
      emojis: [
        getAssetPath('assets/emoji_design/memes/meme1_emoji1.png'),
        getAssetPath('assets/emoji_design/memes/meme1_emoji2.png'),
        getAssetPath('assets/emoji_design/memes/meme1_emoji3.png'),
        getAssetPath('assets/emoji_design/memes/meme1_emoji4.png'),
        getAssetPath('assets/emoji_design/memes/meme1_emoji5.png')
      ]
    },
    {
      id: 2,
      name: 'Elon Musk and Lei Jun State Dinner Selfie',
      source: 'reddit',
      source_url: 'https://www.reddit.com/r/UnfilteredChina/comments/1tdl8ng/xiaomis_president_and_ceo_lei_jun_tries_to_take_a/',
      fetched_at: '2026-05-25',
      infoDescription: '雷军在国宴上试图和马斯克合影，马斯克回头笑的瞬间，被玩成"社交牛逼症 vs 社交尴尬症"的对比梗。',
      referenceImage: getAssetPath('assets/emoji_design/memes/meme_ref_2.png'),
      emojis: [
        getAssetPath('assets/emoji_design/memes/meme2_emoji1.png'),
        getAssetPath('assets/emoji_design/memes/meme2_emoji2.png'),
        getAssetPath('assets/emoji_design/memes/meme2_emoji3.png'),
        getAssetPath('assets/emoji_design/memes/meme2_emoji4.png')
      ]
    },
    {
      id: 3,
      name: 'Evil Chihuahua Smiling',
      source: 'Know Your Meme',
      source_url: 'https://knowyourmeme.com/memes/evil-chihuahua-smiling',
      fetched_at: '2026-05-25',
      infoDescription: '吉娃娃犬斜眼皮笑肉不笑的表情，用来表达"表面配合内心不屑"、"我忍了但我没忘"的阴阳怪气场景。',
      referenceImage: getAssetPath('assets/emoji_design/memes/meme_ref_3.png'),
      emojis: [
        getAssetPath('assets/emoji_design/memes/meme3_emoji1.png'),
        getAssetPath('assets/emoji_design/memes/meme3_emoji2.png'),
        getAssetPath('assets/emoji_design/memes/meme3_emoji3.png')
      ]
    },
    {
      id: 4,
      name: 'Viral Lobster Creature',
      source: 'OpenClaw',
      source_url: 'https://www.architjn.com/blog/openclaw-hype-exposed-ai-lobster-revolution-non-techies',
      fetched_at: '2026-05-25',
      infoDescription: 'AI龙虾卡通形象，是近期流行的 AI角色代表，常被用来表达"圆滚滚可爱但有点危险"的反差感。',
      referenceImage: getAssetPath('assets/emoji_design/memes/meme_ref_4.png'),
      emojis: [
        getAssetPath('assets/emoji_design/memes/meme4_emoji1.png'),
        getAssetPath('assets/emoji_design/memes/meme4_emoji2.png'),
        getAssetPath('assets/emoji_design/memes/meme4_emoji3.png'),
        getAssetPath('assets/emoji_design/memes/meme4_emoji4.png')
      ]
    },
    {
      id: 5,
      name: 'Chaotic Pigtail Reaction',
      source: 'Know Your Meme',
      source_url: 'https://knowyourmeme.com/memes/people/xiao-xiao-chinese-kick-girl',
      fetched_at: '2026-05-25',
      infoDescription: '深肤色网红绑着两个冲天小辫、摆出傲娇手势的视频截图，在 TikTok 上广泛流传，象征一种"我很美我知道"的自信戏剧化表情包。',
      referenceImage: getAssetPath('assets/emoji_design/memes/meme_ref_5.png'),
      emojis: [
        getAssetPath('assets/emoji_design/memes/meme5_emoji1.png'),
        getAssetPath('assets/emoji_design/memes/meme5_emoji2.png'),
        getAssetPath('assets/emoji_design/memes/meme5_emoji3.png')
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
                  <img src={getAssetPath("assets/icon_fire.png")} alt="Fire" className="meme-detail-fire-icon" />
                  <div className="meme-detail-header-content">
                    <div className="meme-detail-title-row">
                      <h3 className="meme-detail-card-name">{meme.name}</h3>
                      {meme.infoDescription ? (
                        <>
                          <button
                            type="button"
                            className={`meme-detail-info-button ${activeInfoId === meme.id ? 'active' : ''}`}
                            aria-label={`${meme.name} info`}
                            aria-expanded={activeInfoId === meme.id}
                            onClick={() => setActiveInfoId(activeInfoId === meme.id ? null : meme.id)}
                          >
                            !
                          </button>
                          {activeInfoId === meme.id ? (
                            <span className="meme-detail-info-description">{meme.infoDescription}</span>
                          ) : null}
                        </>
                      ) : null}
                    </div>
                    <p className="meme-detail-card-source">
                      Source: {
                        meme.source_url ? (
                          <a href={meme.source_url} target="_blank" rel="noopener noreferrer" style={{color: 'inherit', textDecoration: 'underline'}}>
                            {meme.source}
                          </a>
                        ) : meme.source
                      }
                      {meme.fetched_at ? (
                        <>
                          , May 2026
                        </>
                      ) : null}
                    </p>
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
