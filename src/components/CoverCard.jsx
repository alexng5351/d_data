import { useState, useEffect, useRef } from 'react'
import './CoverCard.css'

function CoverCard({ id, onClick, images: propImages }) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isHovering, setIsHovering] = useState(false)
  const [nextIndex, setNextIndex] = useState(1)
  const [isAnimating, setIsAnimating] = useState(false)
  const intervalRef = useRef(null)
  const timeoutRef = useRef(null)
  
  const defaultImages = [
    `/aicover/assets/cover/cover${id}-1.png`,
    `/aicover/assets/cover/cover${id}-2.png`,
    `/aicover/assets/cover/cover${id}-3.png`
  ]
  const allImages = propImages && propImages.length > 0 ? propImages : defaultImages
  // 最多取前3张图片用于轮播
  const images = allImages.slice(0, 3)
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
        />
        {isHovering && shouldCarousel && (
          <img
            key={`next-${id}-${nextIndex}-${Date.now()}`}
            src={images[nextIndex]}
            alt={`Cover ${id} - ${nextIndex + 1}`}
            className={`carousel-image next ${isAnimating ? 'sliding' : ''}`}
            style={{ zIndex: isAnimating ? 10 : 0 }}
          />
        )}
      </div>
    </div>
  )
}

export default CoverCard
