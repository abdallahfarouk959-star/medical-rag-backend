import { useState, useRef, useEffect } from 'react';


// --- Minimalist SVG Icons ---
const Icons = {
  Stethoscope: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-6 h-6"><path d="M4.8 2.3A.3.3 0 1 0 5 2H4a2 2 0 0 0-2 2v5a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6V4a2 2 0 0 0-2-2h-1a.2.2 0 1 0 .3.3"/><path d="M8 15v1a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6v-4"/><circle cx="20" cy="10" r="2"/></svg>,
  Sun: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>,
  Moon: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>,
  Upload: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>,
  Trash: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>,
  User: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>,
  Bot: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><line x1="8" y1="16" x2="8" y2="16"/><line x1="16" y1="16" x2="16" y2="16"/></svg>,
  FileText: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-12 h-12"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>,  Send: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>,
  Copy: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-3 h-3"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>,
  ExternalLink: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-3 h-3"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>,
  Search: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="w-12 h-12"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>,
  PanelLeft: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="3" x2="9" y2="21"/></svg>,
  PanelCenter: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/></svg>,
  PanelRight: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="15" y1="3" x2="15" y2="21"/></svg>,
};


function App() {
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'System initialized. Please upload a clinical guideline document to begin query processing.' }
  ]);
  const [input, setInput] = useState('');
  const [evidence, setEvidence] = useState([]);
 
  const [isUploading, setIsUploading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [isFileUploaded, setIsFileUploaded] = useState(false);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [activeChunkId, setActiveChunkId] = useState(null);
  const [currentPdfPage, setCurrentPdfPage] = useState(1);
 
  // --- Layout State (Panels Visibility & Resizing) ---
  const [showChat, setShowChat] = useState(true);
  const [showEvidence, setShowEvidence] = useState(true);
  const [showPdf, setShowPdf] = useState(true);
 
  const [chatWidth, setChatWidth] = useState(33);
  const [evidenceWidth, setEvidenceWidth] = useState(25);
  const [isDragging, setIsDragging] = useState(false);
  const [isDesktop, setIsDesktop] = useState(true);
 
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);
  const mainRef = useRef(null);
  const textareaRef = useRef(null); // Reference for auto-resizing textarea


  useEffect(() => {
    const handleResize = () => setIsDesktop(window.innerWidth >= 1024);
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);


  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);


  const toggleTheme = () => setIsDarkMode(!isDarkMode);
  const handleUploadClick = () => fileInputRef.current.click();


  // --- Auto-resize Textarea Logic ---
  const handleInputChange = (e) => {
    setInput(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 150)}px`; // Max height 150px
  };


  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!isTyping && input.trim()) {
        handleSend();
      }
    }
  };


  // --- Drag to Resize Logic ---
  const startDrag = (e, panel) => {
    e.preventDefault();
    setIsDragging(true);
    const startX = e.clientX;
    const mainWidth = mainRef.current.clientWidth;
    const startChatW = chatWidth;
    const startEvW = evidenceWidth;


    const onMouseMove = (moveEvent) => {
        const delta = moveEvent.clientX - startX;
        const deltaPercent = (delta / mainWidth) * 100;


        if (panel === 'chat') {
            const newWidth = Math.max(15, Math.min(startChatW + deltaPercent, 65));
            const maxAllowed = showPdf ? 85 - (showEvidence ? evidenceWidth : 0) : 100;
            setChatWidth(Math.min(newWidth, maxAllowed));
        } else if (panel === 'evidence') {
            const newWidth = Math.max(15, Math.min(startEvW + deltaPercent, 65));
            const maxAllowed = showPdf ? 85 - (showChat ? chatWidth : 0) : 100;
            setEvidenceWidth(Math.min(newWidth, maxAllowed));
        }
    };


    const onMouseUp = () => {
        setIsDragging(false);
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
    };


    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  };


  const getPanelStyle = (panelName) => {
    if (!isDesktop) return { width: '100%', flex: 'none' };
    if (panelName === 'chat') {
        if (!showEvidence && !showPdf) return { flex: 1 };
        return { width: `${chatWidth}%` };
    }
    if (panelName === 'evidence') {
        if (!showPdf) return { flex: 1 };
        return { width: `${evidenceWidth}%` };
    }
    if (panelName === 'pdf') {
        return { flex: 1 };
    }
  };


  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (file.type !== 'application/pdf') {
      alert('Invalid file type. PDF required.');
      return;
    }


    const fileUrl = URL.createObjectURL(file);
    setPdfUrl(fileUrl);
    setCurrentPdfPage(1);


    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);


    try {
      const response = await fetch('http://127.0.0.1:8000/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (response.ok) {
        setIsFileUploaded(true);
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: `Upload complete. "${file.name}" indexed successfully into ${data.chunks_created || data.chunks} segments. System ready for queries.`
        }]);
      } else {
        alert(`Upload Error: ${data.detail}`);
      }
    } catch (error) {
      alert('Connection failed. Verify backend service is running.');
    } finally {
      setIsUploading(false);
      e.target.value = null;
    }
  };


  const handleSend = async () => {
    if (!input.trim()) return;
    const userQuery = input;


    // Reset Textarea Height
    if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
    }


    if (!isFileUploaded) {
      setMessages(prev => [
        ...prev,
        { role: 'user', content: userQuery },
        {
          role: 'assistant',
          content: 'Error: No knowledge base detected. Upload a clinical guideline PDF prior to submitting queries.'
        }
      ]);
      setInput('');
      return;
    }


    setMessages(prev => [...prev, { role: 'user', content: userQuery }]);
    setInput('');
    setIsTyping(true);


    try {
      const response = await fetch('http://127.0.0.1:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userQuery, top_k: 5 })
      });
      const data = await response.json();


      if (response.ok) {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.recommendation,
          evidence: data.evidence,
          citations: data.citations,
          confidence: data.confidence,
          latency: data.latency_ms,
          isRefused: data.status === "refused"
        }]);
        setEvidence(data.evidence_panel || []);
      } else {
        setMessages(prev => [...prev, { role: 'assistant', content: `API Error: ${data.detail}` }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Network exception occurred. Request failed.' }]);
    } finally {
      setIsTyping(false);
    }
  };


  const handleClearDB = async () => {
    if (!window.confirm("Confirm deletion of all indexed documents from the vector store?")) return;
    try {
      const response = await fetch('http://127.0.0.1:8000/clear', { method: 'POST' });
      if (response.ok) {
        setIsFileUploaded(false);
        setPdfUrl(null);
        setMessages([{ role: 'assistant', content: 'Database purged successfully. Awaiting new document.' }]);
        setEvidence([]);
      }
    } catch (error) {
      alert('Database purge failed.');
    }
  };


  const renderFormattedMessage = (content) => {
    const citationRegex = /\[\s*Page\s+(\d+),\s*([A-Za-z0-9_\-]+)\s*\]/gi;
    const parts = [];
    let lastIndex = 0;
    let match;


    while ((match = citationRegex.exec(content)) !== null) {
      parts.push(content.substring(lastIndex, match.index));
      const pageNum = match[1];
      const chunkId = match[2];
     
      parts.push(
        <button
          key={match.index}
          onClick={() => {
            setActiveChunkId(chunkId);
            setShowEvidence(true);
            const element = document.getElementById(`chunk-${chunkId}`);
            if (element) {
              element.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
          }}
          className={`mx-1 px-1.5 py-0.5 text-[11px] font-semibold rounded border transition-colors inline-flex items-center gap-1 leading-none align-middle ${
            isDarkMode ? 'bg-blue-900/30 text-blue-300 border-blue-800/50 hover:bg-blue-800/40' : 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100'
          }`}
          title={`View chunk ${chunkId}`}
        >
          <span>[P.{pageNum}]</span>
        </button>
      );
      lastIndex = citationRegex.lastIndex;
    }
    parts.push(content.substring(lastIndex));
    return parts;
  };


  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };


  const renderHighlightedChunk = (fullText, query) => {
    if (!query || !fullText) return fullText;
    const ignoreWords = ['what', 'is', 'the', 'and', 'to', 'of', 'for', 'in', 'a', 'how', 'are', 'does', 'do', 'can', 'with', 'recommended', 'patient'];
    const words = query.split(/\s+/).filter(w => w.length > 3 && !ignoreWords.includes(w.toLowerCase()));
   
    if (words.length === 0) return fullText;
   
    const regex = new RegExp(`(${words.join('|')})`, 'gi');
    const parts = fullText.split(regex);
   
    return parts.map((part, i) =>
      regex.test(part)
      ? <span key={i} className={`font-medium rounded-sm px-0.5 ${isDarkMode ? 'bg-blue-900/60 text-blue-100' : 'bg-blue-100 text-blue-900'}`}>{part}</span>
      : part
    );
  };


  const lastUserQuery = messages.filter(m => m.role === 'user').slice(-1)[0]?.content || '';
  const bgMain = isDarkMode ? 'bg-[#0B1120] text-slate-300' : 'bg-slate-50 text-slate-700';
  const bgPanel = isDarkMode ? 'bg-[#0F172A] border-slate-800/50' : 'bg-white border-slate-200';
  const bgHeader = isDarkMode ? 'bg-[#0B1120]/90 border-slate-800/50' : 'bg-white/90 border-slate-200';
  const panelTitleBg = isDarkMode ? 'bg-[#131E32]' : 'bg-slate-50';


  return (
    <div className={`min-h-screen flex flex-col font-sans h-screen transition-colors duration-300 ${bgMain}`}>
     
      {/* Header */}
      <header className={`sticky top-0 z-50 backdrop-blur-md border-b px-4 md:px-6 py-3 flex flex-wrap gap-4 justify-between items-center transition-all ${bgHeader}`}>
        <div className="flex items-center gap-3">
          <div className={`p-1.5 rounded-lg ${isDarkMode ? 'bg-blue-500/10 text-blue-400' : 'bg-blue-50 text-blue-600'}`}>
            <Icons.Stethoscope />
          </div>
          <h1 className={`text-lg font-bold tracking-tight ${isDarkMode ? 'text-slate-100' : 'text-slate-900'}`}>
            GlycoLens <span className="font-normal opacity-50 text-sm ml-1 hidden sm:inline">CDS</span>
          </h1>
        </div>


        {/* Action Toolbar */}
        <div className="flex items-center gap-2">
         
          {/* Panel Visibility Toggles */}
          <div className={`flex p-1 mr-2 rounded-md border ${isDarkMode ? 'bg-[#0B1120] border-slate-700/80' : 'bg-slate-100 border-slate-300'}`}>
            <button onClick={() => setShowChat(!showChat)} title="Toggle Chat" className={`px-2 py-1 rounded-sm text-xs font-semibold flex items-center gap-1 transition-colors ${showChat ? (isDarkMode ? 'bg-slate-700 text-slate-200' : 'bg-white text-slate-700 shadow-sm') : 'text-slate-500 hover:text-slate-400'}`}>
              <Icons.PanelLeft /> <span className="hidden md:inline">Chat</span>
            </button>
            <button onClick={() => setShowEvidence(!showEvidence)} title="Toggle Context Panel" className={`px-2 py-1 rounded-sm text-xs font-semibold flex items-center gap-1 transition-colors ${showEvidence ? (isDarkMode ? 'bg-slate-700 text-slate-200' : 'bg-white text-slate-700 shadow-sm') : 'text-slate-500 hover:text-slate-400'}`}>
              <Icons.PanelCenter /> <span className="hidden md:inline">Context</span>
            </button>
            <button onClick={() => setShowPdf(!showPdf)} title="Toggle PDF Viewer" className={`px-2 py-1 rounded-sm text-xs font-semibold flex items-center gap-1 transition-colors ${showPdf ? (isDarkMode ? 'bg-slate-700 text-slate-200' : 'bg-white text-slate-700 shadow-sm') : 'text-slate-500 hover:text-slate-400'}`}>
              <Icons.PanelRight /> <span className="hidden md:inline">PDF</span>
            </button>
          </div>


          <button onClick={toggleTheme} className={`p-2 rounded-md transition-colors ${isDarkMode ? 'hover:bg-slate-800 text-slate-400' : 'hover:bg-slate-100 text-slate-500'}`} title="Toggle Theme">
            {isDarkMode ? <Icons.Sun /> : <Icons.Moon />}
          </button>
         
          <div className="h-4 w-px bg-slate-700/50 mx-1 hidden sm:block"></div>
         
          <input type="file" accept=".pdf" ref={fileInputRef} onChange={handleFileChange} className="hidden" />
          <button onClick={handleUploadClick} disabled={isUploading} className={`px-3 py-2 rounded-md text-l font-medium flex items-center gap-2 transition-all ${
            isUploading
              ? 'bg-slate-800 text-slate-400 cursor-not-allowed'
              : isDarkMode ? 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700' : 'bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 shadow-sm'
          }`}>
            <Icons.Upload />
            <span className="hidden sm:inline">{isUploading ? 'Indexing...' : 'Upload'}</span>
          </button>
          <button onClick={handleClearDB} className={`p-2 rounded-md transition-colors ${
            isDarkMode ? 'hover:bg-red-900/30 text-slate-500 hover:text-red-400' : 'hover:bg-red-50 text-slate-400 hover:text-red-600'
          }`} title="Clear Database">
            <Icons.Trash />
          </button>
        </div>
      </header>


      {/* Main Content Area */}
      <main ref={mainRef} className={`flex-1 max-w-[1920px] w-full mx-auto p-4 flex flex-col lg:flex-row ${isDesktop ? 'gap-0' : 'gap-4 overflow-y-auto'} h-[calc(100vh-65px)] lg:overflow-hidden`}>
       
        {/* Placeholder if all closed */}
        {!showChat && !showEvidence && !showPdf && (
           <div className="flex-1 flex flex-col items-center justify-center">
               <div className={`text-slate-400 ${isDarkMode ? 'opacity-60' : 'opacity-80'}`}><Icons.Search /></div>
               <p className={`mt-4 font-medium text-sm ${isDarkMode ? 'text-slate-400' : 'text-slate-500'}`}>All panels are closed. Select a panel from the top menu.</p>
           </div>
        )}


        {/* 1. Chat Terminal */}
        {showChat && (
          <div style={getPanelStyle('chat')} className={`flex flex-col rounded-xl border overflow-hidden shrink-0 shadow-sm ${bgPanel} ${!isDesktop ? 'min-h-[500px]' : 'h-full'}`}>
            <div className="flex-1 overflow-y-auto p-4 space-y-5 scroll-smooth">
              {messages.map((msg, idx) => {
                const isWarning = msg.confidence === 'low' || msg.confidence === 'Low' || msg.isRefused || msg.confidence === 'insufficient';
                const isSystem = msg.role === 'assistant';
               
                return (
                  <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                    <div className={`w-8 h-8 shrink-0 flex items-center justify-center rounded-md border ${
                      msg.role === 'user'
                        ? isDarkMode ? 'bg-[#152033] border-transparent text-blue-400' : 'bg-blue-100 border-transparent text-blue-700'
                        : isDarkMode ? 'bg-[#151E2E] border-slate-700/50 text-slate-400' : 'bg-slate-100 border-slate-200 text-slate-500'
                    }`}>
                      {msg.role === 'user' ? <Icons.User /> : <Icons.Bot />}
                    </div>
                   
                    <div className={`flex flex-col max-w-[85%] gap-1.5 mt-1 ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                      <div className={`px-4 py-3 text-[18px] leading-relaxed rounded-xl ${
                        msg.role === 'user'
                        ? 'bg-blue-600 text-white rounded-tr-sm shadow-sm'
                        : isWarning
                          ? isDarkMode ? 'bg-red-950/20 border border-red-900/50 text-slate-300 rounded-tl-sm' : 'bg-red-50 border border-red-100 text-slate-700 rounded-tl-sm'
                          : isDarkMode ? 'bg-[#152033] text-slate-200 rounded-tl-sm' : 'bg-white border border-slate-200 text-slate-700 shadow-sm rounded-tl-sm'
                      }`}>
                        <div className="whitespace-pre-wrap">
                          {isSystem ? (
                            <div className="flex flex-col gap-3">
                              <div className={isDarkMode ? 'text-slate-200' : 'text-slate-800'}>
                                {renderFormattedMessage(msg.content)}
                              </div>
                             
                              {msg.evidence && (
                                <div className={`px-3 py-2 border-l-2 text-[13px] ${isDarkMode ? 'border-slate-600 text-slate-400 bg-slate-800/30' : 'border-slate-300 text-slate-500 bg-slate-50'}`}>
                                  <span className={`font-semibold block mb-1 text-[11px] uppercase tracking-wider ${isDarkMode ? 'text-slate-500' : 'text-slate-400'}`}>Excerpt</span>
                                  "{msg.evidence}"
                                </div>
                              )}


                              {msg.citations && msg.citations.length > 0 && (
                                <div className="mt-1 flex flex-col gap-1.5">
                                  <span className={`text-[11px] font-semibold uppercase tracking-wider ${isDarkMode ? 'text-slate-500' : 'text-slate-400'}`}>
                                    Sources
                                  </span>
                                  {msg.citations.map((cite, cIdx) => (
                                    <div
                                      key={cIdx}
                                      className={`text-[12px] p-2 rounded-md border flex flex-col gap-0.5 ${isDarkMode ? 'bg-slate-800/30 border-slate-700/50 text-slate-400' : 'bg-slate-50 border-slate-200 text-slate-600'}`}
                                    >
                                      <div className="flex justify-between items-start">
                                        <span className={isDarkMode ? 'text-slate-300 font-medium' : 'text-slate-700 font-medium'}>{cite.document}</span>
                                        <span className="text-[10px] opacity-70 border px-1 rounded">Pg {cite.page}</span>
                                      </div>
                                      <div className="opacity-80 truncate" title={cite.section}>{cite.section}</div>
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>
                          ) : (
                            msg.content
                          )}
                        </div>
                      </div>
                     
                      {isSystem && msg.confidence && (
                        <div className="flex gap-2 items-center px-1 mt-0.5">
                          <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded border uppercase tracking-wider ${
                            msg.confidence.toLowerCase() === 'high' ? (isDarkMode ? 'bg-emerald-950/30 text-emerald-400 border-emerald-900/50' : 'bg-emerald-50 text-emerald-700 border-emerald-200') :
                            msg.confidence.toLowerCase() === 'medium' ? (isDarkMode ? 'bg-amber-950/30 text-amber-400 border-amber-900/50' : 'bg-amber-50 text-amber-700 border-amber-200') :
                            (isDarkMode ? 'bg-rose-950/30 text-rose-400 border-rose-900/50' : 'bg-rose-50 text-rose-700 border-rose-200')
                          }`}>
                            {msg.confidence} CONF
                          </span>
                          {msg.latency && (
                            <span className={`text-[10px] px-1.5 py-0.5 font-mono rounded ${isDarkMode ? 'text-slate-500' : 'text-slate-400'}`}>
                              {msg.latency}ms
                            </span>
                          )}
                          <button
                            onClick={() => copyToClipboard(msg.content)}
                            className={`text-[10px] px-1.5 py-0.5 rounded flex items-center gap-1 transition-colors ${isDarkMode ? 'text-slate-400 hover:text-slate-200 hover:bg-slate-800' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'}`}
                            title="Copy to clipboard"
                          >
                            <Icons.Copy /> Copy
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
             
              {isTyping && (
                <div className="flex gap-3 flex-row">
                  <div className={`w-8 h-8 shrink-0 flex items-center justify-center rounded-md border ${isDarkMode ? 'bg-[#151E2E] border-slate-700/50 text-slate-400' : 'bg-slate-100 border-slate-200 text-slate-500'}`}>
                    <Icons.Bot />
                  </div>
                  <div className={`px-4 py-3 rounded-lg border w-24 flex items-center justify-center ${isDarkMode ? 'bg-[#152033] border-transparent' : 'bg-white border-slate-200 shadow-sm'}`}>
                    <div className={`w-full h-1.5 rounded-full overflow-hidden ${isDarkMode ? 'bg-slate-800' : 'bg-slate-100'}`}>
                      <div className="h-full bg-blue-500/50 w-1/2 animate-[pulse_1s_ease-in-out_infinite_alternate] rounded-full"></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>


            {/* Input Area (Auto-resizing Textarea) */}
            <div className={`p-4 border-t ${isDarkMode ? 'border-slate-800/50 bg-[#0F172A]' : 'border-slate-200 bg-white'}`}>
              <div className="flex gap-3 relative items-end">
                <textarea
                  ref={textareaRef}
                  value={input}
                  onChange={handleInputChange}
                  onKeyDown={handleKeyDown}
                  placeholder="Query clinical guidelines... (Shift+Enter for new line)"
                  disabled={isTyping}
                  rows={1}
                  className={`flex-1 rounded-xl px-4 py-3 text-xl outline-none transition-all border focus:ring-1 focus:ring-blue-500/50 resize-none overflow-y-auto [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none] ${
                    isDarkMode
                    ? 'bg-[#0B1120] border-slate-700 text-slate-200 placeholder-slate-500'
                    : 'bg-slate-50 border-slate-300 text-slate-900 placeholder-slate-400'
                  } ${isTyping ? 'opacity-50 cursor-not-allowed' : ''}`}
                  style={{ minHeight: '44px', colorScheme: isDarkMode ? 'dark' : 'light' }}
                />
                <button
                  onClick={handleSend}
                  disabled={isTyping || !input.trim()}
                  className={`p-3 rounded-xl flex items-center justify-center transition-all duration-200 shrink-0 h-[44px] w-[44px] ${
                    isTyping || !input.trim()
                    ? isDarkMode ? 'bg-slate-800 text-slate-600 cursor-not-allowed' : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-500 text-white shadow-md hover:shadow-lg'
                  }`}
                >
                  <Icons.Send />
                </button>
              </div>
            </div>
          </div>
        )}


        {/* Resizer 1 */}
        {showChat && (showEvidence || showPdf) && isDesktop && (
          <div onMouseDown={(e) => startDrag(e, 'chat')} className="w-4 cursor-col-resize flex justify-center group z-10 shrink-0 select-none">
            <div className={`w-0.5 h-full transition-colors rounded-full ${isDarkMode ? 'bg-slate-800 group-hover:bg-blue-500' : 'bg-slate-200 group-hover:bg-blue-400'}`} />
          </div>
        )}


        {/* 2. Evidence Explorer */}
        {showEvidence && (
          <div style={getPanelStyle('evidence')} className={`flex flex-col rounded-xl border overflow-hidden shrink-0 shadow-sm ${bgPanel} ${!isDesktop ? 'min-h-[400px]' : 'h-full'}`}>
            <div className={`py-3 px-4 font-semibold text-l tracking-wide uppercase border-b flex items-center gap-2 ${panelTitleBg} ${isDarkMode ? 'border-slate-800/80 text-slate-400' : 'border-slate-200 text-slate-500'}`}>
              <Icons.FileText /> Retrieved Context
            </div>
            <div className="flex-1 overflow-y-auto p-4 scroll-smooth bg-black/5 dark:bg-black/20">
                  {evidence.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-center">
                      <div className={`text-slate-400 ${isDarkMode ? 'opacity-60' : 'opacity-80'}`}><Icons.Search /></div>
                      <p className={`text-s mt-3 font-medium ${isDarkMode ? 'text-slate-400' : 'text-slate-500'}`}>No context loaded</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {evidence.map((chunk, index) => {
                        const meta = chunk.metadata || {};
                        const isHighlighted = activeChunkId === meta.chunk_id;
                        const chunkText = chunk.text || meta.text || meta.snippet || "No text available";
                       
                        return (
                          <div key={index} id={`chunk-${meta.chunk_id}`} className={`p-3.5 rounded-lg border transition-all duration-300 ${
                            isHighlighted
                            ? isDarkMode ? 'bg-blue-900/10 border-blue-500/50 shadow-[0_0_15px_rgba(59,130,246,0.05)]' : 'bg-blue-50/80 border-blue-300'
                            : isDarkMode ? 'bg-[#151E2E] border-slate-700/50 hover:border-slate-600' : 'bg-white border-slate-200 hover:border-slate-300 shadow-sm'
                          }`}>
                           
                            <div className="flex justify-between items-center mb-2">
                              <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                                isDarkMode ? 'bg-slate-800 text-slate-300' : 'bg-slate-100 text-slate-600'
                              }`}>
                                PG. {meta.page_number || 'N/A'}
                              </span>
                              {chunk.rerank_score && (
                                <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border ${
                                  isDarkMode ? 'bg-slate-900 border-slate-700 text-slate-400' : 'bg-slate-50 border-slate-200 text-slate-500'
                                }`}>
                                  SIM: {(chunk.rerank_score * 100).toFixed(1)}%
                                </span>
                              )}
                            </div>


                            <div className={`mb-3 pb-2 border-b text-[11px] ${isDarkMode ? 'border-slate-700/50 text-slate-400' : 'border-slate-100 text-slate-500'}`}>
                              <div className="truncate mb-0.5" title={meta.document_name}><span className="font-semibold">Doc:</span> {meta.document_name || 'unknown'}</div>
                              {meta.section_title && (
                                <div className="truncate text-slate-500 dark:text-slate-500" title={meta.section_title}>{meta.section_title}</div>
                              )}
                            </div>


                            <div className={`text-[13px] leading-relaxed whitespace-pre-wrap ${isDarkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                              {renderHighlightedChunk(chunkText, lastUserQuery)}
                            </div>


                            {meta.page_number && pdfUrl && (
                              <div className="flex justify-start mt-3 pt-2">
                                <button
                                  onClick={() => {
                                    setCurrentPdfPage(meta.page_number);
                                    setShowPdf(true); // Open PDF Viewer if closed
                                  }}
                                  className={`text-[11px] font-medium flex items-center gap-1 transition-colors px-2 py-1 rounded-md ${
                                    isDarkMode ? 'bg-slate-800 hover:bg-slate-700 text-blue-400' : 'bg-slate-100 hover:bg-slate-200 text-blue-600'
                                  }`}
                                >
                                  <Icons.ExternalLink /> Open in PDF
                                </button>
                              </div>
                            )}


                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
          </div>
        )}


        {/* Resizer 2 */}
        {showEvidence && showPdf && isDesktop && (
          <div onMouseDown={(e) => startDrag(e, 'evidence')} className="w-4 cursor-col-resize flex justify-center group z-10 shrink-0 select-none">
            <div className={`w-0.5 h-full transition-colors rounded-full ${isDarkMode ? 'bg-slate-800 group-hover:bg-blue-500' : 'bg-slate-200 group-hover:bg-blue-400'}`} />
          </div>
        )}


        {/* 3. Document Viewer */}
        {showPdf && (
          <div style={getPanelStyle('pdf')} className={`flex flex-col rounded-xl border overflow-hidden shrink-0 shadow-sm ${bgPanel} ${!isDesktop ? 'min-h-[600px]' : 'h-full'}`}>
            <div className={`py-3 px-4 font-semibold text-l tracking-wide uppercase border-b flex items-center gap-2 ${panelTitleBg} ${isDarkMode ? 'border-slate-800/80 text-slate-400' : 'border-slate-200 text-slate-500'}`}>
               Source Document
            </div>
            <div className="flex-1 overflow-hidden relative">
                {isDragging && <div className="absolute inset-0 z-50 cursor-col-resize" />}
               
                <div className={`h-full w-full flex flex-col items-center justify-center ${isDarkMode ? 'bg-[#0B1120]' : 'bg-slate-100'}`}>
                  {!pdfUrl ? (
                    <div className="flex flex-col items-center">
                      <div className={`text-slate-400 ${isDarkMode ? 'opacity-60' : 'opacity-80'}`}><Icons.FileText /></div>
                      <p className={`text-s mt-3 font-medium ${isDarkMode ? 'text-slate-400' : 'text-slate-500'}`}>No document loaded</p>
                    </div>
                  ) : (
                    <iframe
                      key={`${pdfUrl}-${currentPdfPage}`}
                      src={`${pdfUrl}#page=${currentPdfPage}&zoom=80&pagemode=none`}
                      className="w-full h-full border-0 bg-white relative z-10"
                      title="PDF Viewer"
                    />
                  )}
                </div>
            </div>
          </div>
        )}


      </main>
    </div>
  );
}


export default App;