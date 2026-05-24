import { useEffect, useState } from 'react'
import { getAssetPath } from '../utils'
import './EmojiDetailModal.css'

function EmojiDetailModal({ emoji, isOpen, onClose }) {
  const [messages, setMessages] = useState([])
  const [isAnimating, setIsAnimating] = useState(false)
  const [isPreparing, setIsPreparing] = useState(false)
  const [newMessageId, setNewMessageId] = useState(null)
  const [isClicking, setIsClicking] = useState(false)
  const [currentPage, setCurrentPage] = useState(0)
  const [commentPageEmojiCount, setCommentPageEmojiCount] = useState(3)
  
  const pages = ['chat', 'page2', 'page3']

  useEffect(() => {
    if (isOpen && emoji) {
      document.body.style.overflow = 'hidden'
      const initialMsg = { id: Date.now(), image: emoji.image, label: emoji.label }
      setMessages([initialMsg])
      setNewMessageId(null)
      setCommentPageEmojiCount(3)
      setCurrentPage(0)
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, emoji])

  useEffect(() => {
    if (!emoji) return
    
    if (currentPage === 0) {
      const initialMsg = { id: Date.now(), image: emoji.image, label: emoji.label }
      setMessages([initialMsg])
      setNewMessageId(null)
    } else if (currentPage === 1) {
      setCommentPageEmojiCount(3)
    }
  }, [currentPage, emoji])

  const sendEmoji = (emojiImage, emojiLabel) => {
    // 1. 先prepare，让容器向下移动
    setIsPreparing(true)
    
    requestAnimationFrame(() => {
      // 2. 添加新消息
      const newMsg = { id: Date.now(), image: emojiImage, label: emojiLabel }
      setNewMessageId(newMsg.id)
      setMessages(prev => [...prev, newMsg])
      
      // 3. 下一帧开始动画向上
      requestAnimationFrame(() => {
        setIsPreparing(false)
        setIsAnimating(true)
        setTimeout(() => {
          setIsAnimating(false)
          setNewMessageId(null)
        }, 200)
      })
    })
  }

  const handleEmojiClick = () => {
    setIsClicking(true)
    setTimeout(() => setIsClicking(false), 200)
    
    if (currentPage === 1) {
      setCommentPageEmojiCount(prev => Math.min(prev + 1, 10))
    } else {
      sendEmoji(emoji.image, emoji.label)
    }
  }

  const handlePreviousPage = () => {
    setCurrentPage((prev) => (prev - 1 + pages.length) % pages.length)
  }

  const handleNextPage = () => {
    setCurrentPage((prev) => (prev + 1) % pages.length)
  }

  if (!isOpen || !emoji) return null

  return (
    <div className="emoji-detail-modal-overlay" onClick={onClose}>
      <div className="emoji-detail-modal" onClick={(e) => e.stopPropagation()}>
        <div className="emoji-detail-modal-header">
          <div className="emoji-detail-title">
            {emoji.label || 'Emoji Detail'}
            <img src={getAssetPath("assets/icon_airemix.png")} alt="AI Remix" className="emoji-detail-ai-icon" />
          </div>
          <div className="emoji-detail-modal-close" onClick={onClose}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M4 4L12 12M4 12L12 4" stroke="white" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </div>
        </div>

        <div className="emoji-detail-modal-body">
          <div className="emoji-detail-left">
            <img 
              src={emoji.image} 
              alt={emoji.label} 
              className={`emoji-detail-main-image ${isClicking ? 'clicking' : ''}`}
              onClick={handleEmojiClick}
            />
            <div className="emoji-detail-description">
              {emoji.description || 'This is a beautifully designed emoji that you can use in your creative projects.'}
            </div>
          </div>
          
          <div className="emoji-detail-right">
            <div className="emoji-detail-phone-frame">
              <img 
                src={getAssetPath("assets/icon_next.png")} 
                alt="Previous" 
                className={`emoji-detail-nav-button emoji-detail-nav-prev ${currentPage === 0 ? 'disabled' : ''}`}
                onClick={currentPage !== 0 ? handlePreviousPage : undefined}
              />
              <img 
                src={getAssetPath("assets/icon_next.png")} 
                alt="Next" 
                className={`emoji-detail-nav-button emoji-detail-nav-next ${currentPage === pages.length - 1 ? 'disabled' : ''}`}
                onClick={currentPage !== pages.length - 1 ? handleNextPage : undefined}
              />
              
              {currentPage === 0 && (
                <>
                  <img src={getAssetPath("assets/chatpage.png")} alt="Chat Page" className="chatpage-image" />
                  <div className="emoji-detail-chat-area">
                    <div className={`emoji-detail-chat-messages ${isPreparing ? 'emoji-detail-chat-messages-prepare' : ''} ${isAnimating ? 'emoji-detail-chat-messages-animating' : ''}`}>
                      {messages.map((msg) => (
                        <img 
                          key={msg.id} 
                          src={msg.image} 
                          alt={msg.label} 
                          className={`emoji-detail-phone-emoji ${msg.id === newMessageId ? 'emoji-detail-phone-emoji-new' : ''}`}
                        />
                      ))}
                    </div>
                  </div>
                  <div className="emoji-detail-chat-bar">
                    <img 
                      src={getAssetPath("assets/emoji_design/basic/emoji_basic_6.png")} 
                      alt="Basic 6" 
                      className="emoji-detail-chat-bar-emoji"
                      onClick={() => sendEmoji(getAssetPath('assets/emoji_design/basic/emoji_basic_6.png'), 'Basic 6')}
                    />
                    <img 
                      src={getAssetPath("assets/emoji_design/basic/emoji_basic_2.png")} 
                      alt="Basic 2" 
                      className="emoji-detail-chat-bar-emoji"
                      onClick={() => sendEmoji(getAssetPath('assets/emoji_design/basic/emoji_basic_2.png'), 'Basic 2')}
                    />
                    <img 
                      src={getAssetPath("assets/emoji_design/basic/emoji_basic_3.png")} 
                      alt="Basic 3" 
                      className="emoji-detail-chat-bar-emoji"
                      onClick={() => sendEmoji(getAssetPath('assets/emoji_design/basic/emoji_basic_3.png'), 'Basic 3')}
                    />
                    <img 
                      src={getAssetPath("assets/emoji_design/basic/emoji_basic_4.png")} 
                      alt="Basic 4" 
                      className="emoji-detail-chat-bar-emoji"
                      onClick={() => sendEmoji(getAssetPath('assets/emoji_design/basic/emoji_basic_4.png'), 'Basic 4')}
                    />
                    <img 
                      src={emoji.image} 
                      alt={emoji.label} 
                      className="emoji-detail-chat-bar-emoji"
                      onClick={() => sendEmoji(emoji.image, emoji.label)}
                    />
                  </div>
                </>
              )}
              {currentPage === 1 && (
                  <div className="commentpage-container">
                    <img 
                      src={getAssetPath("assets/commentpage.png")} 
                      alt="Comment Page" 
                      className="commentpage-image"
                    />
                    <div className="commentpage-emojis">
                      {Array.from({ length: commentPageEmojiCount }).map((_, index) => (
                        <img 
                          key={index}
                          src={emoji.image} 
                          alt={emoji.label} 
                          className="commentpage-emoji-item"
                        />
                      ))}
                    </div>
                  </div>
                )}
              {currentPage === 2 && (
                <div className="storypage-container">
                  <img 
                    src={getAssetPath("assets/storypage.png")} 
                    alt="Story Page" 
                    className="storypage-image"
                  />
                  <div className="storypage-emojis">
                    <img 
                      key={0}
                      src={getAssetPath("assets/emoji_design/basic/emoji_basic_1.png")} 
                      alt="Basic 1" 
                      className="storypage-emoji-item"
                    />
                    <img 
                      key={1}
                      src={getAssetPath("assets/emoji_design/basic/emoji_basic_2.png")} 
                      alt="Basic 2" 
                      className="storypage-emoji-item"
                    />
                    <img 
                      key={2}
                      src={getAssetPath("assets/emoji_design/basic/emoji_basic_3.png")} 
                      alt="Basic 3" 
                      className="storypage-emoji-item"
                    />
                    <img 
                      key={3}
                      src={getAssetPath("assets/emoji_design/basic/emoji_basic_4.png")} 
                      alt="Basic 4" 
                      className="storypage-emoji-item"
                    />
                    <img 
                      key={4}
                      src={getAssetPath("assets/emoji_design/basic/emoji_basic_5.png")} 
                      alt="Basic 5" 
                      className="storypage-emoji-item"
                    />
                    <img 
                      key={5}
                      src={emoji.image} 
                      alt={emoji.label} 
                      className="storypage-emoji-item"
                    />
                  </div>
                </div>
              )}
              
              <div className="emoji-detail-page-dots">
                {pages.map((_, index) => (
                  <div 
                    key={index} 
                    className={`emoji-detail-page-dot ${index === currentPage ? 'active' : ''}`}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default EmojiDetailModal