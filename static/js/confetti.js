const canvas = document.getElementById('confetti_canvas')

const jsConfetti = new JSConfetti({ canvas })

setTimeout(() => {
  jsConfetti.addConfetti({
      confettiNumber: 2000,
  })
}, 700)
