import { useState } from 'react'
import './App.css'
import MainPage from './components/MainPage'
import AddTemplatePage from './components/AddTemplatePage'
import ManageTemplatePage from './components/ManageTemplatePage'
import CoverInputPage from './components/CoverInputPage'
import CoverGeneratePage from './components/CoverGeneratePage'
import CoverGenerateResultPage from './components/CoverGenerateResultPage'
import IPPetPage from './components/IPPetPage'
import EmojiPage from './components/EmojiPage'

function App() {
  const [activeTab, setActiveTab] = useState('Cover')
  const [coverPageState, setCoverPageState] = useState('main')
  const [selectedTemplateId, setSelectedTemplateId] = useState(null)
  const [selectedTemplate, setSelectedTemplate] = useState(null)
  const [userImage, setUserImage] = useState(null)
  const [generatedImages, setGeneratedImages] = useState([])
  const [isRegenerating, setIsRegenerating] = useState(false)
  const [collapsed, setCollapsed] = useState(false)
  const [userTemplates, setUserTemplates] = useState([])

  const handleTabChange = (tabName) => {
    setActiveTab(tabName)
    if (tabName === 'Cover') {
      setCoverPageState('main')
    }
  }

  const handleToggleCollapse = () => {
    setCollapsed(!collapsed)
  }

  const handleGoToCoverInput = (templateId) => {
    setSelectedTemplateId(templateId || null)
    setCoverPageState('coverInput')
  }

  const handleBackToMain = () => {
    setCoverPageState('main')
  }

  const handleGoToGenerate = (template, image) => {
    setSelectedTemplate(template)
    setUserImage(image)
    setCoverPageState('coverGenerate')
  }

  const handleBackToCoverInput = () => {
    setCoverPageState('coverInput')
    setIsRegenerating(false)
  }

  const handleGenerateComplete = (images) => {
    setGeneratedImages(images)
    setCoverPageState('coverGenerateResult')
    setIsRegenerating(false)
  }

  const handleRegenerate = () => {
    setIsRegenerating(true)
    setCoverPageState('coverGenerate')
  }

  const handleGoToAddTemplate = () => {
    setCoverPageState('addTemplate')
  }

  const handleGoToManageTemplate = () => {
    setCoverPageState('manageTemplate')
  }

  const handleSaveTemplate = (templateData) => {
    const now = new Date()
    const addedAt = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`
    const templateId = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}${String(now.getSeconds()).padStart(2, '0')}${String(now.getMilliseconds()).padStart(3, '0')}`
    
    const newTemplate = {
      id: Date.now(),
      name: templateData.name,
      templateId: templateId,
      addedAt: addedAt,
      images: templateData.images.filter(img => img !== null),
      prompt: templateData.prompt,
      json: templateData.json,
      tags: templateData.tags
    }
    setUserTemplates([newTemplate, ...userTemplates])
    setCoverPageState('manageTemplate')
  }

  const handleDeleteTemplate = (templateId) => {
    setUserTemplates(userTemplates.filter(template => template.id !== templateId))
  }

  const renderCoverPages = () => {
    switch (coverPageState) {
      case 'main':
        return <MainPage 
          onCoverClick={handleGoToCoverInput} 
          onTabChange={handleTabChange} 
          collapsed={collapsed} 
          onToggleCollapse={handleToggleCollapse}
          userTemplates={userTemplates}
          onAddClick={handleGoToAddTemplate}
          onManageTemplateClick={handleGoToManageTemplate}
        />
      case 'manageTemplate':
        return <ManageTemplatePage
          onBack={handleBackToMain}
          onTabChange={handleTabChange}
          collapsed={collapsed}
          onToggleCollapse={handleToggleCollapse}
          userTemplates={userTemplates}
          onDeleteTemplate={handleDeleteTemplate}
        />
      case 'addTemplate':
        return <AddTemplatePage
          onBack={handleBackToMain}
          onSaveTemplate={handleSaveTemplate}
          onTabChange={handleTabChange}
          collapsed={collapsed}
          onToggleCollapse={handleToggleCollapse}
        />
      case 'coverInput':
        return <CoverInputPage 
          onBack={handleBackToMain} 
          onGenerate={handleGoToGenerate} 
          onTabChange={handleTabChange} 
          collapsed={collapsed} 
          onToggleCollapse={handleToggleCollapse}
          templateId={selectedTemplateId}
          userTemplates={userTemplates}
        />
      case 'coverGenerate':
        return (
          <CoverGeneratePage
            onBack={handleBackToCoverInput}
            onGenerateComplete={handleGenerateComplete}
            isRegenerating={isRegenerating}
            previousImages={isRegenerating ? generatedImages : []}
            onTabChange={handleTabChange}
            collapsed={collapsed}
            onToggleCollapse={handleToggleCollapse}
          />
        )
      case 'coverGenerateResult':
        return (
          <CoverGenerateResultPage
            onBack={handleBackToCoverInput}
            onRegenerate={handleRegenerate}
            images={generatedImages}
            onTabChange={handleTabChange}
            collapsed={collapsed}
            onToggleCollapse={handleToggleCollapse}
          />
        )
      default:
        return <MainPage 
          onCoverClick={handleGoToCoverInput} 
          onTabChange={handleTabChange} 
          collapsed={collapsed} 
          onToggleCollapse={handleToggleCollapse} 
        />
    }
  }

  return (
    <div className="app">
      {activeTab === 'Cover' && renderCoverPages()}
      {activeTab === 'IP Pet' && <IPPetPage onTabChange={handleTabChange} collapsed={collapsed} onToggleCollapse={handleToggleCollapse} />}
      {activeTab === 'Emoji' && <EmojiPage onTabChange={handleTabChange} collapsed={collapsed} onToggleCollapse={handleToggleCollapse} />}
    </div>
  )
}

export default App
