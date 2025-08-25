document.addEventListener('DOMContentLoaded', function () {
  // YouTube IFrame API
  let player;
  let ultimoAvance = 0;
  function onYouTubeIframeAPIReady() {
    player = new YT.Player('youtube-player', {
      events: {
        'onStateChange': onPlayerStateChange
      }
    });
  }
  window.onYouTubeIframeAPIReady = onYouTubeIframeAPIReady;

  function onPlayerStateChange(event) {
    if (event.data === YT.PlayerState.PLAYING) {
      updateProgress();
    }
  }

  function updateProgress() {
    const progress = document.getElementById("video-progress");
    const progressText = document.getElementById("progress-text");
    function tick() {
      if (player.getPlayerState() === YT.PlayerState.PLAYING) {
        const duracion = player.getDuration();
        const current = player.getCurrentTime();
        const porcentaje = duracion ? Math.round((current / duracion) * 100) : 0;
        progress.value = percent;
        progressText.textContent = percent + "%";
        ultimoAvance = porcentaje;
        setTimeout(tick, 1000);
      }
    }
    tick();
  }
  // Guardar avance al salir de la página
  window.addEventListener('beforeunload', function (e) {
    // Reemplaza cursoId con la variable de tu curso (puedes pasarla con Jinja2)
    const cursoId = window.cursoId || "{{ curso.id }}";
    navigator.sendBeacon(`/curso/${cursoId}/avance`, JSON.stringify({ avance: ultimoAvance }));
  });
});