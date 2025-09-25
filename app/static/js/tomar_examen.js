// tu_proyecto/app/static/js/tomar_examen.js

document.addEventListener('DOMContentLoaded', function() {
    // --- Referencias a Elementos ---
    const startScreen = document.getElementById('start-screen');
    const examScreen = document.getElementById('exam-screen');
    const startBtn = document.getElementById('start-exam-btn');
    const examForm = document.getElementById('exam-form');
    
    const questions = document.querySelectorAll('.question-slide');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const timerEl = document.getElementById('timer');

    // --- Si no estamos en la página del examen, no hacemos nada ---
    if (!startScreen || !examScreen || !startBtn) {
        return;
    }

    // --- Variables de Estado ---
    let currentQuestionIndex = 0;
    const totalQuestions = questions.length;
    let timerInterval;

    // --- Funciones ---
    function startExam() {
        startScreen.classList.add('hidden');
        examScreen.classList.remove('hidden');
        showQuestion(0);
        
        // Leemos la duración desde el atributo data-* del HTML
        const durationString = examScreen.dataset.duration;
        console.log("Duración del examen (minutos):", durationString);
        const durationInMinutes = parseInt(durationString, 10);
        console.log("Duración del examen (minutos, parseado):", durationInMinutes);
        
        startTimer(durationInMinutes * 60);
    }

    function showQuestion(index) {
        questions.forEach((q, i) => {
            q.classList.toggle('hidden', i !== index);
        });
        
        const progress = ((index + 1) / totalQuestions) * 100;
        progressBar.style.width = `${progress}%`;
        progressText.textContent = `Pregunta ${index + 1} de ${totalQuestions}`;

        prevBtn.classList.toggle('hidden', index === 0);
        if (index === totalQuestions - 1) {
            nextBtn.textContent = 'Finalizar Examen';
        } else {
            nextBtn.textContent = 'Siguiente';
        }
    }

    function nextQuestion() {
        if (currentQuestionIndex < totalQuestions - 1) {
            currentQuestionIndex++;
            showQuestion(currentQuestionIndex);
        } else {
            submitExam();
        }
    }

    function prevQuestion() {
        if (currentQuestionIndex > 0) {
            currentQuestionIndex--;
            showQuestion(currentQuestionIndex);
        }
    }

    function startTimer(durationInSeconds) {
        let timer = durationInSeconds;
        timerInterval = setInterval(() => {
            if (timer < 0) {
                clearInterval(timerInterval);
                timerEl.textContent = '¡Tiempo agotado!';
                Swal.fire({
                    title: '¡Tiempo Terminado!',
                    text: 'Tu examen se enviará automáticamente.',
                    icon: 'info',
                    timer: 2000,
                    showConfirmButton: false
                }).then(() => {
                    examForm.submit();
                });
            } else {
                const minutes = Math.floor(timer / 60);
                let seconds = timer % 60;
                seconds = seconds < 10 ? '0' + seconds : seconds;
                timerEl.textContent = `${minutes}:${seconds}`;
                timer--;
            }
        }, 1000);
    }

    function submitExam() {
        Swal.fire({
            title: '¿Estás seguro?',
            text: "Una vez enviado, no podrás cambiar tus respuestas.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#FBBF24',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Sí, ¡enviar examen!',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                examForm.submit();
            }
        });
    }

    // --- Event Listeners ---
    startBtn.addEventListener('click', startExam);
    nextBtn.addEventListener('click', nextQuestion);
    prevBtn.addEventListener('click', prevQuestion);
});