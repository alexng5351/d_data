import { useState, useEffect, useRef } from 'react'
import './CoverCard.css'
import { getCoverImages } from './MainPage'

function CoverCard({ id, onClick, images: propImages }) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isHovering, setIsHovering] = useState(false)
  const [nextIndex, setNextIndex] = useState(1)
  const [isAnimating, setIsAnimating] = useState(false)
  const intervalRef = useRef(null)
  const timeoutRef = useRef(null)
  
  const handleImageError = (e, index) => {
    const img = e.target
    const currentSrc = img.src
    // 如果是png格式，尝试回退到jpg
    if (currentSrc.endsWith('.png')) {
      const jpgSrc = currentSrc.replace('.png', '.jpg')
      img.src = jpgSrc
    }
  }
  
  const allImages = propImages && propImages.length > 0 ? propImages : getCoverImages(id)
  // 使用所有提供的图片，不限制数量
  const images = allImages
  // 判断是否需要轮播（至少2张图片才轮播）
  const shouldCarousel = images.length >= 2

  const startCarousel = () => {
    if (!shouldCarousel) {
      return
    }
    
    setIsHovering(true)
    setCurrentIndex(0)
    setNextIndex(1)
    let counter = 1
    timeoutRef.current = setTimeout(() => {
      setIsAnimating(true)
      setTimeout(() => {
        setCurrentIndex(1)
        setNextIndex(images.length > 2 ? 2 : 0)
        setIsAnimating(false)
      }, 500)
      intervalRef.current = setInterval(() => {
        counter++
        const newCurrentIndex = counter % images.length
        const newNextIndex = (counter + 1) % images.length
        setIsAnimating(true)
        setTimeout(() => {
          setCurrentIndex(newCurrentIndex)
          setNextIndex(newNextIndex)
          setIsAnimating(false)
        }, 500)
      }, 1800)
    }, 100)
  }

  const stopCarousel = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
      timeoutRef.current = null
    }
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
    setIsHovering(false)
    setCurrentIndex(0)
    setNextIndex(1)
    setIsAnimating(false)
  }

  useEffect(() => {
    return () => {
      stopCarousel()
    }
  }, [])

  return (
    <div
      className="cover-card"
      onClick={onClick}
      onMouseEnter={startCarousel}
      onMouseLeave={stopCarousel}
    >
      <div className="images-container">
        <img
          key={`current-${id}-${currentIndex}`}
          src={images[currentIndex]}
          alt={`Cover ${id} - ${currentIndex + 1}`}
          className="carousel-image current"
          style={{ zIndex: 1 }}
          onError={(e) => handleImageError(e, currentIndex)}
        />
        {isHovering && shouldCarousel && (
          <img
            key={`next-${id}-${nextIndex}-${Date.now()}`}
            src={images[nextIndex]}
            alt={`Cover ${id} - ${nextIndex + 1}`}
            className={`carousel-image next ${isAnimating ? 'sliding' : ''}`}
            style={{ zIndex: isAnimating ? 10 : 0 }}
            onError={(e) => handleImageError(e, nextIndex)}
          />
        )}
      </div>
    </div>
  )
}

export default CoverCard
