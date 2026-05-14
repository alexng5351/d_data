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
    `/assets/cover/cover${id}-1.png`,
    `/assets/cover/cover${id}-2.png`,
    `/assets/cover/cover${id}-3.png`
  ]
  const images = propImages && propImages.length > 0 ? propImages : defaultImages

  const startCarousel = () => {
    setIsHovering(true)
    setCurrentIndex(0)
    setNextIndex(1)
    let counter = 1
    timeoutRef.current = setTimeout(() => {
      setIsAnimating(true)
      setTimeout(() => {
        setCurrentIndex(1)
        setNextIndex(2)
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
        {isHovering && (
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
