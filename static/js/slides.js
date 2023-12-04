// URL do PDF dos slides
var url = '/static/pdf/Mini curso - Controle de versão com Git.pdf'

var $slides = document.getElementById('slides-canvas')
var $pageNum = document.getElementById('page_num')
var $pageCount = document.getElementById('page_count')

var { pdfjsLib } = globalThis
pdfjsLib.GlobalWorkerOptions.workerSrc = '//mozilla.github.io/pdf.js/build/pdf.worker.mjs'

var pdfDoc = null,
  pageNum = 1,
  pageRendering = false,
  pageNumPending = null,
  scale = 1.5,
  canvas = $slides,
  ctx = canvas.getContext('2d')

function renderPage(num) {
  if (!pdfDoc) return
  pageRendering = true
  pdfDoc.getPage(num).then(function (page) {
    var viewport = page.getViewport({ scale: scale })
    canvas.height = viewport.height
    canvas.width = viewport.width

    var renderContext = {
      canvasContext: ctx,
      viewport: viewport
    }
    var renderTask = page.render(renderContext)

    renderTask.promise.then(function () {
      pageRendering = false
      if (pageNumPending !== null) {
        renderPage(pageNumPending)
        pageNumPending = null
      }
    })
  })

  $pageNum.textContent = num
}

/**
 * If another page rendering in progress, waits until the rendering is
 * finised. Otherwise, executes rendering immediately.
 */
function queueRenderPage(num) {
  if (pageRendering) {
    pageNumPending = num
  } else {
    renderPage(num)
  }
}

function setPage(num) {
  pageNum = num
  queueRenderPage(num)
}

window.setPage = setPage
window.pageCount = 0

/**
 * Asynchronously downloads PDF.
 */
pdfjsLib.getDocument(url).promise.then(function (pdfDoc_) {
  pdfDoc = pdfDoc_
  window.pageCount = pdfDoc.numPages
  $pageCount.textContent = pdfDoc.numPages

  // Initial/first page rendering
  renderPage(pageNum)
})

// Tela cheia
$slides.addEventListener('dblclick', () => toggleFullScreen())
document.addEventListener('fullscreenchange', () => toggleFullScreen(true))
function toggleFullScreen(invert = false) {
  if (invert) {
    document.fullscreen ? enterFullscreen() : exitFullscreen()
  } else {
    !document.fullscreen ? enterFullscreen() : exitFullscreen()
  }
}

function enterFullscreen() {
  $slides.requestFullscreen()
  $slides.classList.add('fullscreen')
}

function exitFullscreen() {
  document.exitFullscreen()
  $slides.classList.remove('fullscreen')
}

// Passar slides com teclado
document.addEventListener('keyup', slideKey)
function slideKey(e) {
  const KEYS = {
    ArrowRight: () => nextSlide(),
    ArrowLeft: () => prevSlide(),
    Home: () => firstSlide(),
    End: () => lastSlide(),
    f: () => toggleFullScreen(),
    F: () => toggleFullScreen()
  }
  KEYS[e.key]?.()
}

// Socket
socketio.on('set-slide', (slideNum) => {
  setPage(slideNum)
  currentSlide = slideNum
})
