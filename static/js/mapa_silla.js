document.addEventListener('DOMContentLoaded', () => {
    const formAsientos = document.getElementById('form-asientos');
    if (!formAsientos) return;

    const listaAsientosEl = document.getElementById('lista-asientos');
    const totalAsientosEl = document.getElementById('total-asientos');
    const btnBoletas = document.getElementById('btn-boletas');
    const inputAsientos = document.getElementById('input-asientos');
    const numerosInferioresEl = document.getElementById('numeros-inferiores');

    let seleccionados = [];

    document.querySelectorAll('#sala .asiento').forEach(asiento => {
        if (asiento.dataset.ocupado === '1') {
            asiento.style.pointerEvents = 'none';
            return;
        }
        asiento.addEventListener('click', () => {
            asiento.classList.toggle('seleccionado');
            const codigo = asiento.dataset.codigo;
            if (asiento.classList.contains('seleccionado')) {
                seleccionados.push(codigo);
            } else {
                seleccionados = seleccionados.filter(item => item !== codigo);
            }
            actualizarResumen();
        });
    });

    const primerFila = document.querySelector('#sala .fila');
    if (primerFila) {
        const totalColumnas = primerFila.querySelectorAll('.asiento').length;
        for (let i = 1; i <= totalColumnas; i++) {
            const num = document.createElement('div');
            num.classList.add('numero-columna');
            num.textContent = i;
            numerosInferioresEl.appendChild(num);
        }
    }

    function actualizarResumen() {
        listaAsientosEl.textContent = seleccionados.length > 0 ? seleccionados.join(', ') : 'Ninguno';
        totalAsientosEl.textContent = seleccionados.length;
        inputAsientos.value = seleccionados.join(',');
        btnBoletas.disabled = seleccionados.length === 0;
    }
});