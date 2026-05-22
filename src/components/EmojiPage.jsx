import { useState, useEffect } from 'react'
import './EmojiPage.css'
import Sidebar from './Sidebar'

function EmojiPage({ onTabChange, collapsed, onToggleCollapse }) {
  const [activeCategoryIndex, setActiveCategoryIndex] = useState(0)
  const [currentDate, setCurrentDate] = useState('')

  useEffect(() => {
    const date = new Date()
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    setCurrentDate(`${year}.${month}.${day}`)
  }, [])

  const categories = ['All', 'Basic', 'Styles', 'Animals', 'Hands', 'Words', 'Others']
  const trendingMemes = [
    'Raise a lobster',
    'Lei Jun\'s Selfie Moment',
    'The Internet Is Becoming Chinese',
    'AI Fruit Drama Is Addictive',
    'AI Fruit Drama Is Addictive'
  ]

  const emojiData = {
    basic: [
      { image: '/aicover/assets/emoji_design/basic/emoji_basic_1.png', label: 'Basic 1' },
      { image: '/aicover/assets/emoji_design/basic/emoji_basic_2.png', label: 'Basic 2' },
      { image: '/aicover/assets/emoji_design/basic/emoji_basic_3.png', label: 'Basic 3' },
      { image: '/aicover/assets/emoji_design/basic/emoji_basic_4.png', label: 'Basic 4' },
      { image: '/aicover/assets/emoji_design/basic/emoji_basic_5.png', label: 'Basic 5' },
      { image: '/aicover/assets/emoji_design/basic/emoji_basic_6.png', label: 'Basic 6' },
      { image: '/aicover/assets/emoji_design/basic/emoji_basic_7.png', label: 'Basic 7' },
      { image: '/aicover/assets/emoji_design/basic/emoji_basic_8.png', label: 'Basic 8' },
      { image: '/aicover/assets/emoji_design/basic/emoji_basic_9.png', label: 'Basic 9' }
    ],
    styles: [
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_1.png', label: 'Style 1' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_2.png', label: 'Style 2' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_3.png', label: 'Style 3' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_4.png', label: 'Style 4' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_5.png', label: 'Style 5' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_6.png', label: 'Style 6' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_7.png', label: 'Style 7' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_8.png', label: 'Style 8' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_9.png', label: 'Style 9' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_10.png', label: 'Style 10' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_11.png', label: 'Style 11' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_12.png', label: 'Style 12' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_13.png', label: 'Style 13' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_14.png', label: 'Style 14' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_15.png', label: 'Style 15' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_16.png', label: 'Style 16' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_17.png', label: 'Style 17' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_18.png', label: 'Style 18' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_19.png', label: 'Style 19' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_20.png', label: 'Style 20' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_21.png', label: 'Style 21' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_22.png', label: 'Style 22' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_23.png', label: 'Style 23' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_24.png', label: 'Style 24' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_25.png', label: 'Style 25' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_26.png', label: 'Style 26' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_27.png', label: 'Style 27' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_28.png', label: 'Style 28' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_29.png', label: 'Style 29' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_30.png', label: 'Style 30' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_31.png', label: 'Style 31' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_32.png', label: 'Style 32' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_33.png', label: 'Style 33' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_34.png', label: 'Style 34' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_35.png', label: 'Style 35' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_36.png', label: 'Style 36' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_37.png', label: 'Style 37' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_38.png', label: 'Style 38' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_39.png', label: 'Style 39' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_40.png', label: 'Style 40' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_41.png', label: 'Style 41' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_42.png', label: 'Style 42' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_43.png', label: 'Style 43' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_44.png', label: 'Style 44' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_45.png', label: 'Style 45' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_46.png', label: 'Style 46' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_47.png', label: 'Style 47' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_48.png', label: 'Style 48' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_49.png', label: 'Style 49' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_50.png', label: 'Style 50' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_51.png', label: 'Style 51' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_52.png', label: 'Style 52' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_53.png', label: 'Style 53' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_54.png', label: 'Style 54' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_55.png', label: 'Style 55' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_56.png', label: 'Style 56' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_57.png', label: 'Style 57' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_58.png', label: 'Style 58' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_59.png', label: 'Style 59' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_60.png', label: 'Style 60' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_61.png', label: 'Style 61' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_62.png', label: 'Style 62' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_63.png', label: 'Style 63' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_64.png', label: 'Style 64' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_65.png', label: 'Style 65' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_66.png', label: 'Style 66' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_67.png', label: 'Style 67' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_68.png', label: 'Style 68' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_69.png', label: 'Style 69' },
      { image: '/aicover/assets/emoji_design/styles/emoji_styles_70.png', label: 'Style 70' }
    ],
    animals: [
      { image: '/aicover/assets/emoji_design/animals/emoji_animals_1.png', label: 'Animal 1' },
      { image: '/aicover/assets/emoji_design/animals/emoji_animals_2.png', label: 'Animal 2' },
      { image: '/aicover/assets/emoji_design/animals/emoji_animals_3.png', label: 'Animal 3' },
      { image: '/aicover/assets/emoji_design/animals/emoji_animals_4.png', label: 'Animal 4' },
      { image: '/aicover/assets/emoji_design/animals/emoji_animals_5.png', label: 'Animal 5' },
      { image: '/aicover/assets/emoji_design/animals/emoji_animals_6.png', label: 'Animal 6' },
      { image: '/aicover/assets/emoji_design/animals/emoji_animals_7.png', label: 'Animal 7' },
      { image: '/aicover/assets/emoji_design/animals/emoji_animals_8.png', label: 'Animal 8' },
      { image: '/aicover/assets/emoji_design/animals/emoji_animals_9.png', label: 'Animal 9' },
      { image: '/aicover/assets/emoji_design/animals/emoji_animals_10.png', label: 'Animal 10' },
      { image: '/aicover/assets/emoji_design/animals/emoji_animals_11.png', label: 'Animal 11' },
      { image: '/aicover/assets/emoji_design/animals/emoji_animals_12.png', label: 'Animal 12' },
      { image: '/aicover/assets/emoji_design/animals/emoji_animals_13.png', label: 'Animal 13' },
      { image: '/aicover/assets/emoji_design/animals/emoji_animals_14.png', label: 'Animal 14' },
      { image: '/aicover/assets/emoji_design/animals/emoji_animals_15.png', label: 'Animal 15' },
      { image: '/aicover/assets/emoji_design/animals/emoji_animals_16.png', label: 'Animal 16' },
      { image: '/aicover/assets/emoji_design/animals/emoji_animals_17.png', label: 'Animal 17' },
      { image: '/aicover/assets/emoji_design/animals/emoji_animals_18.png', label: 'Animal 18' },
      { image: '/aicover/assets/emoji_design/animals/emoji_animals_19.png', label: 'Animal 19' },
      { image: '/aicover/assets/emoji_design/animals/emoji_animals_20.png', label: 'Animal 20' },
      { image: '/aicover/assets/emoji_design/animals/emoji_animals_21.png', label: 'Animal 21' }
    ],
    hands: [
      { image: '/aicover/assets/emoji_design/hands/emoji_hands_1.png', label: 'Hand 1' },
      { image: '/aicover/assets/emoji_design/hands/emoji_hands_2.png', label: 'Hand 2' },
      { image: '/aicover/assets/emoji_design/hands/emoji_hands_3.png', label: 'Hand 3' },
      { image: '/aicover/assets/emoji_design/hands/emoji_hands_4.png', label: 'Hand 4' },
      { image: '/aicover/assets/emoji_design/hands/emoji_hands_5.png', label: 'Hand 5' },
      { image: '/aicover/assets/emoji_design/hands/emoji_hands_6.png', label: 'Hand 6' },
      { image: '/aicover/assets/emoji_design/hands/emoji_hands_7.png', label: 'Hand 7' },
      { image: '/aicover/assets/emoji_design/hands/emoji_hands_8.png', label: 'Hand 8' },
      { image: '/aicover/assets/emoji_design/hands/emoji_hands_9.png', label: 'Hand 9' },
      { image: '/aicover/assets/emoji_design/hands/emoji_hands_10.png', label: 'Hand 10' },
      { image: '/aicover/assets/emoji_design/hands/emoji_hands_11.png', label: 'Hand 11' },
      { image: '/aicover/assets/emoji_design/hands/emoji_hands_12.png', label: 'Hand 12' }
    ],
    words: [
      { image: '/aicover/assets/emoji_design/words/emoji_words_1.png', label: 'Word 1' },
      { image: '/aicover/assets/emoji_design/words/emoji_words_2.png', label: 'Word 2' },
      { image: '/aicover/assets/emoji_design/words/emoji_words_3.png', label: 'Word 3' },
      { image: '/aicover/assets/emoji_design/words/emoji_words_4.png', label: 'Word 4' },
      { image: '/aicover/assets/emoji_design/words/emoji_words_5.png', label: 'Word 5' },
      { image: '/aicover/assets/emoji_design/words/emoji_words_6.png', label: 'Word 6' },
      { image: '/aicover/assets/emoji_design/words/emoji_words_7.png', label: 'Word 7' },
      { image: '/aicover/assets/emoji_design/words/emoji_words_8.png', label: 'Word 8' },
      { image: '/aicover/assets/emoji_design/words/emoji_words_9.png', label: 'Word 9' },
      { image: '/aicover/assets/emoji_design/words/emoji_words_10.png', label: 'Word 10' },
      { image: '/aicover/assets/emoji_design/words/emoji_words_11.png', label: 'Word 11' }
    ],
    others: [
      { image: '/aicover/assets/emoji_design/others/emoji_others_1.png', label: 'Other 1' },
      { image: '/aicover/assets/emoji_design/others/emoji_others_2.png', label: 'Other 2' }
    ]
  }

  const categoryKeys = ['all', 'basic', 'styles', 'animals', 'hands', 'words', 'others']

  const getFilteredEmojiData = () => {
    const selectedCategory = categoryKeys[activeCategoryIndex]
    if (selectedCategory === 'all') {
      return [
        ...emojiData.basic,
        ...emojiData.styles,
        ...emojiData.animals,
        ...emojiData.hands,
        ...emojiData.words,
        ...emojiData.others
      ]
    }
    return emojiData[selectedCategory] || []
  }

  const filteredEmojiData = getFilteredEmojiData()

  return (
    <div className="emoji-page">
      <Sidebar activeTab="Emoji" onTabChange={onTabChange} collapsed={collapsed} onToggleCollapse={onToggleCollapse} />
      
      <div className="main-content">
        <div className="top-bar">
          <h1 className="page-title">Emoji</h1>
          <div className="top-actions">
            <button className="manage-template-btn">Manage Template</button>
            <button className="add-btn">
              <img src="/aicover/assets/icon_add.png" alt="Add" className="add-icon" />
            </button>
          </div>
        </div>

        {/* 实时热梗字条展示区 */}
        <div className="trending-section">
          <div className="trending-left">
            <div className="trending-date">{currentDate}</div>
            <div className="trending-memes">
              {trendingMemes.map((meme, index) => (
                <div key={index} className="meme-item">
                  <img src="/aicover/assets/icon_fire.png" alt="Fire" className="meme-flame" />
                  <span className="meme-text">{meme}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="trending-right">
            <img src="/aicover/assets/emoji_banner.png" alt="Emoji Banner" className="emoji-banner" />
            <div className="emoji-bubble-container emoji-1-container">
              <img src="/aicover/assets/bubble.png" alt="Bubble 1" className="banner-bubble size-208" />
              <img src="/aicover/assets/emoji_design/memes/emoji_meme_1.png" alt="Emoji 1" className="banner-emoji size-160" />
            </div>
            <div className="emoji-bubble-container emoji-2-container">
              <img src="/aicover/assets/bubble.png" alt="Bubble 2" className="banner-bubble size-156" />
              <img src="/aicover/assets/emoji_design/memes/emoji_meme_2.png" alt="Emoji 2" className="banner-emoji size-120" />
            </div>
            <div className="emoji-bubble-container emoji-3-container">
              <img src="/aicover/assets/bubble.png" alt="Bubble 3" className="banner-bubble size-104" />
              <img src="/aicover/assets/emoji_design/memes/emoji_meme_3.png" alt="Emoji 3" className="banner-emoji size-80" />
            </div>
            <div className="emoji-bubble-container emoji-4-container">
              <img src="/aicover/assets/bubble.png" alt="Bubble 4" className="banner-bubble size-221" />
              <img src="/aicover/assets/emoji_design/memes/emoji_meme_4.png" alt="Emoji 4" className="banner-emoji size-170" />
            </div>
            <div className="emoji-bubble-container emoji-5-container">
              <img src="/aicover/assets/bubble.png" alt="Bubble 5" className="banner-bubble size-156" />
              <img src="/aicover/assets/emoji_design/memes/emoji_meme_5.png" alt="Emoji 5" className="banner-emoji size-120" />
            </div>
          </div>
        </div>

        {/* 新的分类标签栏 */}
        <div className="category-tabs-bar">
          {categories.map((category, index) => (
            <button
              key={index}
              className={`category-tab-item ${index === activeCategoryIndex ? 'active' : ''}`}
              onClick={() => setActiveCategoryIndex(index)}
            >
              {category}
            </button>
          ))}
        </div>

        {/* emoji 卡片网格 */}
        <div className="emoji-grid">
          {filteredEmojiData.map((item, index) => (
            <div key={index} className="emoji-card">
              <div className="emoji-card-content">
                <img src={item.image} alt={item.label} className="emoji-card-emoji" />
              </div>
              <div className="emoji-card-label">{item.label}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default EmojiPage